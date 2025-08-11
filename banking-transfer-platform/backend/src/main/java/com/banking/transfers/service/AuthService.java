package com.banking.transfers.service;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.model.User;
import com.banking.transfers.repository.UserRepository;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.UUID;

/**
 * Service d'authentification et de gestion des utilisateurs
 */
@Service
@Transactional
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;
    private final JwtService jwtService;
    private final MfaService mfaService;
    private final AuditService auditService;

    public AuthService(UserRepository userRepository,
                      PasswordEncoder passwordEncoder,
                      AuthenticationManager authenticationManager,
                      JwtService jwtService,
                      MfaService mfaService,
                      AuditService auditService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.authenticationManager = authenticationManager;
        this.jwtService = jwtService;
        this.mfaService = mfaService;
        this.auditService = auditService;
    }

    /**
     * Authentifie un utilisateur
     */
    public LoginResponse authenticate(LoginRequest loginRequest) {
        try {
            // Vérifier si l'utilisateur existe
            Optional<User> userOpt = findUserByIdentifier(loginRequest.getUsernameOrEmail());
            if (userOpt.isEmpty()) {
                throw new BadCredentialsException("Identifiants invalides");
            }

            User user = userOpt.get();

            // Vérifier si le compte est actif et non verrouillé
            if (!user.isEnabled()) {
                if (user.getIsLocked()) {
                    throw new LockedException("Compte verrouillé. Contactez l'administrateur.");
                } else {
                    throw new BadCredentialsException("Compte inactif");
                }
            }

            // Authentifier avec Spring Security
            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                    user.getUsername(),
                    loginRequest.getPassword()
                )
            );

            SecurityContextHolder.getContext().setAuthentication(authentication);

            // Vérifier MFA si activé
            if (user.getMfaEnabled()) {
                if (loginRequest.getMfaCode() == null || loginRequest.getMfaCode().trim().isEmpty()) {
                    throw new BadCredentialsException("Code MFA requis");
                }

                if (!mfaService.verifyCode(user.getMfaSecret(), loginRequest.getMfaCode())) {
                    user.incrementFailedLoginAttempts();
                    userRepository.save(user);
                    throw new BadCredentialsException("Code MFA invalide");
                }
            }

            // Réinitialiser les tentatives de connexion échouées
            user.resetFailedLoginAttempts();
            user.setLastLoginDate(LocalDateTime.now());
            userRepository.save(user);

            // Générer les tokens
            String accessToken = jwtService.generateAccessToken(user);
            String refreshToken = jwtService.generateRefreshToken(user);

            // Créer la réponse
            LoginResponse response = new LoginResponse(accessToken, refreshToken, jwtService.getAccessTokenExpiration());
            populateUserInfo(response, user);
            response.setMfaRequired(user.getMfaEnabled());
            response.setMfaEnabled(user.getMfaEnabled());
            response.setIsCompliant(user.isCompliant());
            response.setSessionId(UUID.randomUUID().toString());
            response.setDeviceId(loginRequest.getDeviceId());
            response.setIpAddress(loginRequest.getIpAddress());

            // Auditer la connexion
            auditService.logLogin(user, loginRequest.getIpAddress(), loginRequest.getUserAgent(), true, null);

            return response;

        } catch (BadCredentialsException | LockedException e) {
            // Auditer l'échec de connexion
            Optional<User> userOpt = findUserByIdentifier(loginRequest.getUsernameOrEmail());
            if (userOpt.isPresent()) {
                User user = userOpt.get();
                user.incrementFailedLoginAttempts();
                userRepository.save(user);
                auditService.logLogin(user, loginRequest.getIpAddress(), loginRequest.getUserAgent(), false, e.getMessage());
            }
            throw e;
        }
    }

    /**
     * Rafraîchit un token d'accès
     */
    public LoginResponse refreshToken(String refreshToken) {
        try {
            String username = jwtService.extractUsername(refreshToken);
            Optional<User> userOpt = userRepository.findByUsername(username);

            if (userOpt.isEmpty() || !jwtService.isTokenValid(refreshToken, userOpt.get())) {
                throw new BadCredentialsException("Token de rafraîchissement invalide");
            }

            User user = userOpt.get();
            if (!user.isEnabled()) {
                throw new BadCredentialsException("Compte inactif ou verrouillé");
            }

            String newAccessToken = jwtService.generateAccessToken(user);
            String newRefreshToken = jwtService.generateRefreshToken(user);

            LoginResponse response = new LoginResponse(newAccessToken, newRefreshToken, jwtService.getAccessTokenExpiration());
            populateUserInfo(response, user);
            response.setMfaEnabled(user.getMfaEnabled());
            response.setIsCompliant(user.isCompliant());

            return response;

        } catch (Exception e) {
            throw new BadCredentialsException("Impossible de rafraîchir le token");
        }
    }

    /**
     * Déconnecte un utilisateur
     */
    public void logout(String accessToken, String ipAddress) {
        try {
            String username = jwtService.extractUsername(accessToken);
            Optional<User> userOpt = userRepository.findByUsername(username);

            if (userOpt.isPresent()) {
                User user = userOpt.get();
                auditService.logLogout(user, ipAddress, true, null);
            }

            // Invalider le token (ajouter à une liste noire si nécessaire)
            jwtService.invalidateToken(accessToken);

        } catch (Exception e) {
            // Log l'erreur mais ne pas la propager
            auditService.logLogout(null, ipAddress, false, e.getMessage());
        }
    }

    /**
     * Change le mot de passe d'un utilisateur
     */
    public void changePassword(String username, String currentPassword, String newPassword) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isEmpty()) {
            throw new BadCredentialsException("Utilisateur non trouvé");
        }

        User user = userOpt.get();

        // Vérifier l'ancien mot de passe
        if (!passwordEncoder.matches(currentPassword, user.getPasswordHash())) {
            throw new BadCredentialsException("Mot de passe actuel incorrect");
        }

        // Vérifier que le nouveau mot de passe est différent
        if (passwordEncoder.matches(newPassword, user.getPasswordHash())) {
            throw new BadCredentialsException("Le nouveau mot de passe doit être différent de l'actuel");
        }

        // Encoder et sauvegarder le nouveau mot de passe
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        user.setPasswordChangedDate(LocalDateTime.now());
        userRepository.save(user);

        // Auditer le changement de mot de passe
        auditService.logPasswordChange(user, true, null);
    }

    /**
     * Active ou désactive MFA pour un utilisateur
     */
    public void toggleMfa(String username, boolean enable) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isEmpty()) {
            throw new BadCredentialsException("Utilisateur non trouvé");
        }

        User user = userOpt.get();

        if (enable && !user.getMfaEnabled()) {
            // Activer MFA
            String secret = mfaService.generateSecret();
            user.setMfaSecret(secret);
            user.setMfaEnabled(true);
            user.setMfaBackupCodes(mfaService.generateBackupCodes());
        } else if (!enable && user.getMfaEnabled()) {
            // Désactiver MFA
            user.setMfaSecret(null);
            user.setMfaEnabled(false);
            user.setMfaBackupCodes(null);
        }

        userRepository.save(user);
        auditService.logMfaToggle(user, enable, true, null);
    }

    /**
     * Vérifie un code MFA
     */
    public boolean verifyMfaCode(String username, String code) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isEmpty()) {
            return false;
        }

        User user = userOpt.get();
        if (!user.getMfaEnabled() || user.getMfaSecret() == null) {
            return false;
        }

        return mfaService.verifyCode(user.getMfaSecret(), code);
    }

    /**
     * Trouve un utilisateur par son identifiant (username ou email)
     */
    private Optional<User> findUserByIdentifier(String identifier) {
        // Essayer d'abord par username
        Optional<User> user = userRepository.findByUsername(identifier);
        if (user.isPresent()) {
            return user;
        }

        // Essayer par email
        return userRepository.findByEmail(identifier);
    }

    /**
     * Remplit les informations utilisateur dans la réponse
     */
    private void populateUserInfo(LoginResponse response, User user) {
        response.setUserId(user.getId().toString());
        response.setUsername(user.getUsername());
        response.setEmail(user.getEmail());
        response.setFirstName(user.getFirstName());
        response.setLastName(user.getLastName());
        response.setFullName(user.getFullName());
        response.setRoles(user.getRoles());
        response.setPermissions(user.getPermissions());
        response.setKycStatus(user.getKycStatus());
        response.setAmlStatus(user.getAmlStatus());
        response.setRiskScore(user.getRiskScore());
    }

    /**
     * Vérifie si un utilisateur peut effectuer des transferts
     */
    public boolean canUserTransfer(String username) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isEmpty()) {
            return false;
        }

        User user = userOpt.get();
        return user.isEnabled() && user.isCompliant() && !user.isHighRisk();
    }

    /**
     * Vérifie les permissions d'un utilisateur
     */
    public boolean hasPermission(String username, String permission) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isEmpty()) {
            return false;
        }

        User user = userOpt.get();
        return user.hasPermission(permission);
    }

    /**
     * Vérifie les rôles d'un utilisateur
     */
    public boolean hasRole(String username, String role) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isEmpty()) {
            return false;
        }

        User user = userOpt.get();
        return user.hasRole(role);
    }

    /**
     * Déverrouille un compte utilisateur
     */
    public void unlockAccount(String username) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isEmpty()) {
            throw new BadCredentialsException("Utilisateur non trouvé");
        }

        User user = userOpt.get();
        user.resetFailedLoginAttempts();
        userRepository.save(user);

        auditService.logAccountUnlock(user, true, null);
    }

    /**
     * Active ou désactive un compte utilisateur
     */
    public void toggleAccountStatus(String username, boolean active) {
        Optional<User> userOpt = userRepository.findByUsername(username);
        if (userOpt.isEmpty()) {
            throw new BadCredentialsException("Utilisateur non trouvé");
        }

        User user = userOpt.get();
        user.setIsActive(active);
        if (!active) {
            user.setIsLocked(true);
        }
        userRepository.save(user);

        auditService.logAccountStatusChange(user, active, true, null);
    }
}
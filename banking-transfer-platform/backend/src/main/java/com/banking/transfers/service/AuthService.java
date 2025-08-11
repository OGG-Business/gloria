package com.banking.transfers.service;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.model.User;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
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

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private MfaService mfaService;

    @Autowired
    private AuditService auditService;

    /**
     * Authentification d'un utilisateur
     */
    public LoginResponse login(LoginRequest request) {
        try {
            // Validation des champs
            validateLoginRequest(request);

            // Recherche de l'utilisateur
            User user = findUserByUsernameOrEmail(request.getUsernameOrEmailTrimmed());
            if (user == null) {
                throw new BadCredentialsException("Identifiants invalides");
            }

            // Vérification du statut du compte
            validateUserAccount(user);

            // Authentification avec Spring Security
            Authentication authentication = authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                    user.getUsername(),
                    request.getPasswordTrimmed()
                )
            );

            // Vérification MFA si activé
            if (user.getMfaEnabled() && user.getMfaSecret() != null) {
                if (!request.isMfaRequired()) {
                    return createMfaRequiredResponse(user);
                }
                
                if (!mfaService.validateMfaCode(user.getMfaSecret(), request.getMfaCodeTrimmed())) {
                    handleFailedLogin(user, "Code MFA invalide");
                    throw new BadCredentialsException("Code MFA invalide");
                }
            }

            // Mise à jour des informations de connexion
            updateUserLoginInfo(user, request);

            // Génération des tokens
            String accessToken = jwtService.generateAccessToken(user);
            String refreshToken = jwtService.generateRefreshToken(user);

            // Création de la réponse
            LoginResponse response = createLoginResponse(user, accessToken, refreshToken);

            // Audit de la connexion
            auditService.logLogin(user, request.getClientIp(), request.getUserAgent(), true, null);

            return response;

        } catch (AuthenticationException e) {
            handleAuthenticationError(request, e);
            throw e;
        } catch (Exception e) {
            auditService.logLogin(null, request.getClientIp(), request.getUserAgent(), false, e.getMessage());
            throw new RuntimeException("Erreur lors de l'authentification", e);
        }
    }

    /**
     * Déconnexion d'un utilisateur
     */
    public void logout(String token, String clientIp, String userAgent) {
        try {
            if (token != null && token.startsWith("Bearer ")) {
                token = token.substring(7);
            }

            // Invalidation du token
            jwtService.invalidateToken(token);

            // Récupération de l'utilisateur depuis le token
            String username = jwtService.extractUsername(token);
            if (username != null) {
                Optional<User> userOpt = userRepository.findByUsername(username);
                if (userOpt.isPresent()) {
                    User user = userOpt.get();
                    auditService.logLogout(user, clientIp, userAgent, true, null);
                }
            }

        } catch (Exception e) {
            auditService.logLogout(null, clientIp, userAgent, false, e.getMessage());
            throw new RuntimeException("Erreur lors de la déconnexion", e);
        }
    }

    /**
     * Rafraîchissement d'un token
     */
    public LoginResponse refreshToken(String refreshToken) {
        try {
            // Validation du refresh token
            if (!jwtService.validateRefreshToken(refreshToken)) {
                throw new BadCredentialsException("Refresh token invalide");
            }

            // Extraction des informations utilisateur
            String username = jwtService.extractUsername(refreshToken);
            User user = findUserByUsername(username);
            if (user == null) {
                throw new BadCredentialsException("Utilisateur non trouvé");
            }

            // Vérification du statut du compte
            validateUserAccount(user);

            // Génération de nouveaux tokens
            String newAccessToken = jwtService.generateAccessToken(user);
            String newRefreshToken = jwtService.generateRefreshToken(user);

            // Création de la réponse
            LoginResponse response = createLoginResponse(user, newAccessToken, newRefreshToken);

            // Audit
            auditService.logTokenRefresh(user, true, null);

            return response;

        } catch (Exception e) {
            auditService.logTokenRefresh(null, false, e.getMessage());
            throw new RuntimeException("Erreur lors du rafraîchissement du token", e);
        }
    }

    /**
     * Validation d'un token d'accès
     */
    public boolean validateToken(String token) {
        try {
            if (token != null && token.startsWith("Bearer ")) {
                token = token.substring(7);
            }

            if (!jwtService.validateAccessToken(token)) {
                return false;
            }

            String username = jwtService.extractUsername(token);
            User user = findUserByUsername(username);
            
            return user != null && user.getIsActive() && !user.getIsLocked();

        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Changement de mot de passe
     */
    public void changePassword(UUID userId, String currentPassword, String newPassword) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        // Vérification du mot de passe actuel
        if (!passwordEncoder.matches(currentPassword, user.getPasswordHash())) {
            throw new BadCredentialsException("Mot de passe actuel incorrect");
        }

        // Validation du nouveau mot de passe
        validatePassword(newPassword);

        // Mise à jour du mot de passe
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        user.setPasswordChangedDate(LocalDateTime.now());
        user.setFailedLoginAttempts(0);
        user.setIsLocked(false);

        userRepository.save(user);

        // Audit
        auditService.logPasswordChange(user, true, null);
    }

    /**
     * Réinitialisation de mot de passe
     */
    public void resetPassword(String email) {
        User user = userRepository.findByEmail(email)
            .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        // Génération d'un token de réinitialisation
        String resetToken = jwtService.generatePasswordResetToken(user);
        
        // TODO: Envoi d'email avec le token de réinitialisation
        
        // Audit
        auditService.logPasswordResetRequest(user, true, null);
    }

    /**
     * Confirmation de réinitialisation de mot de passe
     */
    public void confirmPasswordReset(String resetToken, String newPassword) {
        try {
            // Validation du token
            if (!jwtService.validatePasswordResetToken(resetToken)) {
                throw new BadCredentialsException("Token de réinitialisation invalide");
            }

            String username = jwtService.extractUsername(resetToken);
            User user = findUserByUsername(username);
            if (user == null) {
                throw new RuntimeException("Utilisateur non trouvé");
            }

            // Validation du nouveau mot de passe
            validatePassword(newPassword);

            // Mise à jour du mot de passe
            user.setPasswordHash(passwordEncoder.encode(newPassword));
            user.setPasswordChangedDate(LocalDateTime.now());
            user.setFailedLoginAttempts(0);
            user.setIsLocked(false);

            userRepository.save(user);

            // Invalidation du token
            jwtService.invalidateToken(resetToken);

            // Audit
            auditService.logPasswordReset(user, true, null);

        } catch (Exception e) {
            auditService.logPasswordReset(null, false, e.getMessage());
            throw new RuntimeException("Erreur lors de la réinitialisation du mot de passe", e);
        }
    }

    // Méthodes privées utilitaires

    private void validateLoginRequest(LoginRequest request) {
        if (request.getUsernameOrEmailTrimmed() == null || request.getUsernameOrEmailTrimmed().trim().isEmpty()) {
            throw new BadCredentialsException("Nom d'utilisateur ou email requis");
        }
        if (request.getPasswordTrimmed() == null || request.getPasswordTrimmed().trim().isEmpty()) {
            throw new BadCredentialsException("Mot de passe requis");
        }
    }

    private User findUserByUsernameOrEmail(String usernameOrEmail) {
        // Essayer d'abord par nom d'utilisateur
        Optional<User> userOpt = userRepository.findByUsername(usernameOrEmail);
        if (userOpt.isPresent()) {
            return userOpt.get();
        }

        // Essayer par email
        userOpt = userRepository.findByEmail(usernameOrEmail);
        return userOpt.orElse(null);
    }

    private User findUserByUsername(String username) {
        return userRepository.findByUsername(username).orElse(null);
    }

    private void validateUserAccount(User user) {
        if (!user.getIsActive()) {
            throw new LockedException("Compte désactivé");
        }
        if (user.getIsLocked()) {
            throw new LockedException("Compte verrouillé");
        }
        if (!user.getKycStatus().isValid()) {
            throw new LockedException("KYC non vérifié");
        }
        if (!user.getAmlStatus().isValid()) {
            throw new LockedException("AML non vérifié");
        }
    }

    private void updateUserLoginInfo(User user, LoginRequest request) {
        user.setLastLoginDate(LocalDateTime.now());
        user.setFailedLoginAttempts(0);
        user.setIsLocked(false);
        userRepository.save(user);
    }

    private LoginResponse createMfaRequiredResponse(User user) {
        LoginResponse response = new LoginResponse(
            user.getId(), 
            user.getUsername(), 
            user.getEmail(), 
            user.getFirstName(), 
            user.getLastName()
        );
        response.setMfaEnabled(true);
        response.setMfaRequired(true);
        response.setMessage("Code MFA requis");
        return response;
    }

    private LoginResponse createLoginResponse(User user, String accessToken, String refreshToken) {
        LoginResponse response = new LoginResponse(
            user.getId(), 
            user.getUsername(), 
            user.getEmail(), 
            user.getFirstName(), 
            user.getLastName()
        );

        response.setAccessToken(accessToken);
        response.setRefreshToken(refreshToken);
        response.setExpiresIn(jwtService.getAccessTokenExpiration());
        response.setExpiresAt(LocalDateTime.now().plusSeconds(jwtService.getAccessTokenExpiration()));
        response.setKycStatus(user.getKycStatus());
        response.setAmlStatus(user.getAmlStatus());
        response.setRiskScore(user.getRiskScore());
        response.setMfaEnabled(user.getMfaEnabled());
        response.setMfaRequired(false);
        response.setPreferredLanguage(user.getPreferredLanguage());
        response.setTimezone(user.getTimezone());
        response.setLastLoginDate(user.getLastLoginDate());
        response.setIsFirstLogin(user.getLastLoginDate() == null);
        response.setSessionId(UUID.randomUUID().toString());
        response.setMessage("Connexion réussie");

        return response;
    }

    private void handleAuthenticationError(LoginRequest request, AuthenticationException e) {
        String usernameOrEmail = request.getUsernameOrEmailTrimmed();
        User user = findUserByUsernameOrEmail(usernameOrEmail);
        
        if (user != null) {
            handleFailedLogin(user, e.getMessage());
        }
        
        auditService.logLogin(user, request.getClientIp(), request.getUserAgent(), false, e.getMessage());
    }

    private void handleFailedLogin(LoginRequest request, AuthenticationException e) {
        String usernameOrEmail = request.getUsernameOrEmailTrimmed();
        User user = findUserByUsernameOrEmail(usernameOrEmail);
        
        if (user != null) {
            handleFailedLogin(user, e.getMessage());
        }
        
        auditService.logLogin(user, request.getClientIp(), request.getUserAgent(), false, e.getMessage());
    }

    private void handleFailedLogin(User user, String reason) {
        user.incrementFailedLoginAttempts();
        userRepository.save(user);
        
        auditService.logFailedLogin(user, reason);
    }

    private void validatePassword(String password) {
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Le mot de passe doit contenir au moins 8 caractères");
        }
        if (password.length() > 128) {
            throw new IllegalArgumentException("Le mot de passe ne peut pas dépasser 128 caractères");
        }
        // TODO: Ajouter d'autres validations (complexité, caractères spéciaux, etc.)
    }
}
package com.banking.transfers.service;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.model.User;
import com.banking.transfers.repository.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
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
    private final JwtService jwtService;
    private final MfaService mfaService;
    private final AuditService auditService;

    public AuthService(UserRepository userRepository,
                      PasswordEncoder passwordEncoder,
                      JwtService jwtService,
                      MfaService mfaService,
                      AuditService auditService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.mfaService = mfaService;
        this.auditService = auditService;
    }

    /**
     * Authentifie un utilisateur
     */
    public LoginResponse authenticate(LoginRequest request) {
        // Rechercher l'utilisateur par nom d'utilisateur ou email
        Optional<User> userOpt = userRepository.findByUsernameOrEmail(request.getIdentifier());
        
        if (userOpt.isEmpty()) {
            throw new AuthenticationException("Identifiants invalides");
        }

        User user = userOpt.get();

        // Vérifier si le compte est actif et non verrouillé
        if (!user.isAccountActive()) {
            throw new AuthenticationException("Compte inactif");
        }

        if (user.isAccountLocked()) {
            throw new AuthenticationException("Compte verrouillé");
        }

        // Vérifier le mot de passe
        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            handleFailedLogin(user, request);
            throw new AuthenticationException("Identifiants invalides");
        }

        // Vérifier MFA si activé
        if (user.getMfaEnabled() && !mfaService.verifyMfaCode(user, request.getMfaCode())) {
            throw new AuthenticationException("Code MFA invalide");
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
        populateSessionInfo(response, request);

        // Auditer la connexion
        auditService.logLogin(user, request.getIpAddress(), request.getUserAgent(), true, null);

        return response;
    }

    /**
     * Crée un nouvel utilisateur
     */
    public User createUser(User user, String rawPassword) {
        // Vérifier que le nom d'utilisateur et l'email sont uniques
        if (userRepository.existsByUsername(user.getUsername())) {
            throw new UserExistsException("Le nom d'utilisateur existe déjà");
        }

        if (userRepository.existsByEmail(user.getEmail())) {
            throw new UserExistsException("L'email existe déjà");
        }

        // Encoder le mot de passe
        user.setPasswordHash(passwordEncoder.encode(rawPassword));
        user.setPasswordChangedDate(LocalDateTime.now());

        // Définir les valeurs par défaut
        user.setIsActive(true);
        user.setIsLocked(false);
        user.setFailedLoginAttempts(0);
        user.setMfaEnabled(false);
        user.setRiskScore(0);

        // Sauvegarder l'utilisateur
        User savedUser = userRepository.save(user);

        // Auditer la création
        auditService.logUserCreation(savedUser);

        return savedUser;
    }

    /**
     * Met à jour un utilisateur
     */
    public User updateUser(UUID userId, User userDetails) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));

        // Mettre à jour les champs autorisés
        user.setFirstName(userDetails.getFirstName());
        user.setLastName(userDetails.getLastName());
        user.setPhone(userDetails.getPhone());
        user.setAddress(userDetails.getAddress());
        user.setCity(userDetails.getCity());
        user.setCountry(userDetails.getCountry());
        user.setPostalCode(userDetails.getPostalCode());
        user.setNationality(userDetails.getNationality());
        user.setDateOfBirth(userDetails.getDateOfBirth());
        user.setIdNumber(userDetails.getIdNumber());
        user.setIdType(userDetails.getIdType());

        User updatedUser = userRepository.save(user);

        // Auditer la modification
        auditService.logUserUpdate(updatedUser);

        return updatedUser;
    }

    /**
     * Change le mot de passe d'un utilisateur
     */
    public void changePassword(UUID userId, String currentPassword, String newPassword) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));

        // Vérifier l'ancien mot de passe
        if (!passwordEncoder.matches(currentPassword, user.getPasswordHash())) {
            throw new AuthenticationException("Mot de passe actuel incorrect");
        }

        // Encoder et sauvegarder le nouveau mot de passe
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        user.setPasswordChangedDate(LocalDateTime.now());
        userRepository.save(user);

        // Auditer le changement de mot de passe
        auditService.logPasswordChange(user);
    }

    /**
     * Active ou désactive MFA pour un utilisateur
     */
    public void toggleMfa(UUID userId, boolean enable) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));

        if (enable) {
            String mfaSecret = mfaService.generateMfaSecret();
            user.setMfaSecret(mfaSecret);
            user.setMfaEnabled(true);
        } else {
            user.setMfaSecret(null);
            user.setMfaEnabled(false);
        }

        userRepository.save(user);

        // Auditer le changement MFA
        auditService.logMfaToggle(user, enable);
    }

    /**
     * Verrouille ou déverrouille un compte utilisateur
     */
    public void toggleAccountLock(UUID userId, boolean lock) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));

        user.setIsLocked(lock);
        if (!lock) {
            user.setFailedLoginAttempts(0);
        }

        userRepository.save(user);

        // Auditer le verrouillage/déverrouillage
        auditService.logAccountLockToggle(user, lock);
    }

    /**
     * Trouve un utilisateur par ID
     */
    @Transactional(readOnly = true)
    public User findById(UUID userId) {
        return userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));
    }

    /**
     * Trouve un utilisateur par nom d'utilisateur
     */
    @Transactional(readOnly = true)
    public User findByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));
    }

    /**
     * Trouve un utilisateur par email
     */
    @Transactional(readOnly = true)
    public User findByEmail(String email) {
        return userRepository.findByEmail(email)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));
    }

    /**
     * Trouve tous les utilisateurs actifs
     */
    @Transactional(readOnly = true)
    public List<User> findAllActiveUsers() {
        return userRepository.findByIsActiveTrue();
    }

    /**
     * Trouve les utilisateurs nécessitant une vérification KYC
     */
    @Transactional(readOnly = true)
    public List<User> findUsersRequiringKYC() {
        return userRepository.findUsersRequiringKYCVerification();
    }

    /**
     * Trouve les utilisateurs nécessitant une vérification AML
     */
    @Transactional(readOnly = true)
    public List<User> findUsersRequiringAML() {
        return userRepository.findUsersRequiringAMLVerification();
    }

    /**
     * Trouve les utilisateurs à haut risque
     */
    @Transactional(readOnly = true)
    public List<User> findHighRiskUsers() {
        return userRepository.findHighRiskUsers();
    }

    /**
     * Met à jour le statut KYC d'un utilisateur
     */
    public void updateKycStatus(UUID userId, com.banking.transfers.model.KYCStatus status) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));

        user.setKycStatus(status);
        userRepository.save(user);

        // Auditer le changement de statut KYC
        auditService.logKycStatusChange(user, status);
    }

    /**
     * Met à jour le statut AML d'un utilisateur
     */
    public void updateAmlStatus(UUID userId, com.banking.transfers.model.AMLStatus status) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));

        user.setAmlStatus(status);
        userRepository.save(user);

        // Auditer le changement de statut AML
        auditService.logAmlStatusChange(user, status);
    }

    /**
     * Met à jour le score de risque d'un utilisateur
     */
    public void updateRiskScore(UUID userId, Integer riskScore) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new UserNotFoundException("Utilisateur non trouvé"));

        user.setRiskScore(riskScore);
        userRepository.save(user);

        // Auditer le changement de score de risque
        auditService.logRiskScoreChange(user, riskScore);
    }

    /**
     * Gère une tentative de connexion échouée
     */
    private void handleFailedLogin(User user, LoginRequest request) {
        user.incrementFailedLoginAttempts();
        userRepository.save(user);

        // Auditer la tentative échouée
        auditService.logLogin(user, request.getIpAddress(), request.getUserAgent(), false, "Mot de passe incorrect");
    }

    /**
     * Remplit les informations utilisateur dans la réponse
     */
    private void populateUserInfo(LoginResponse response, User user) {
        response.setUserId(user.getId());
        response.setUsername(user.getUsername());
        response.setEmail(user.getEmail());
        response.setFirstName(user.getFirstName());
        response.setLastName(user.getLastName());
        response.setFullName(user.getFullName());
        response.setPhone(user.getPhone());
        response.setNationality(user.getNationality());
        response.setCountry(user.getCountry());
        response.setKycStatus(user.getKycStatus());
        response.setAmlStatus(user.getAmlStatus());
        response.setRiskScore(user.getRiskScore());
        response.setIsActive(user.getIsActive());
        response.setIsLocked(user.getIsLocked());
        response.setMfaEnabled(user.getMfaEnabled());
        response.setMfaRequired(user.getMfaEnabled());
        response.setLoginTime(LocalDateTime.now());

        // TODO: Parser les rôles et permissions depuis JSON
        // response.setRoles(parseRoles(user.getRoles()));
        // response.setPermissions(parsePermissions(user.getPermissions()));
    }

    /**
     * Remplit les informations de session dans la réponse
     */
    private void populateSessionInfo(LoginResponse response, LoginRequest request) {
        response.setSessionId(UUID.randomUUID().toString());
        response.setDeviceId(request.getDeviceId());
        response.setUserAgent(request.getUserAgent());
        response.setIpAddress(request.getIpAddress());
    }

    // Exceptions personnalisées
    public static class AuthenticationException extends RuntimeException {
        public AuthenticationException(String message) {
            super(message);
        }
    }

    public static class UserExistsException extends RuntimeException {
        public UserExistsException(String message) {
            super(message);
        }
    }

    public static class UserNotFoundException extends RuntimeException {
        public UserNotFoundException(String message) {
            super(message);
        }
    }
}
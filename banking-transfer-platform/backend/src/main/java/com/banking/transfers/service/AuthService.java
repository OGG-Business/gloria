package com.banking.transfers.service;

import com.banking.transfers.model.*;
import com.banking.transfers.repository.UserRepository;
import com.banking.transfers.dto.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Service d'authentification et de gestion des utilisateurs
 */
@Service
@Transactional
public class AuthService implements UserDetailsService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private JwtService jwtService;

    @Autowired
    private RiskAssessmentService riskAssessmentService;

    @Autowired
    private AuditService auditService;

    /**
     * Charge un utilisateur par son nom d'utilisateur pour Spring Security
     */
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new UsernameNotFoundException("Utilisateur non trouvé: " + username));

        return createUserDetails(user);
    }

    /**
     * Authentifie un utilisateur
     */
    public AuthResponse authenticateUser(LoginRequest loginRequest) {
        User user = userRepository.findByUsername(loginRequest.getUsername())
                .orElseThrow(() -> new RuntimeException("Nom d'utilisateur ou mot de passe incorrect"));

        if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPasswordHash())) {
            handleFailedLogin(user);
            throw new RuntimeException("Nom d'utilisateur ou mot de passe incorrect");
        }

        if (!user.canLogin()) {
            throw new RuntimeException("Compte verrouillé ou inactif");
        }

        // Réinitialiser les tentatives échouées
        user.resetFailedLoginAttempts();
        user.setLastLoginDate(LocalDateTime.now());
        userRepository.save(user);

        // Générer le token JWT
        String token = jwtService.generateToken(user.getUsername());

        // Auditer la connexion
        auditService.logUserLogin(user.getId(), loginRequest.getUsername(), true, null);

        return new AuthResponse(token, user.getUsername(), user.getFullName(), user.getMfaEnabled());
    }

    /**
     * Enregistre un nouvel utilisateur
     */
    public UserRegistrationResponse registerUser(UserRegistrationRequest request) {
        // Vérifier si l'utilisateur existe déjà
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new RuntimeException("Le nom d'utilisateur existe déjà");
        }

        if (userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("L'email existe déjà");
        }

        if (request.getIdNumber() != null && userRepository.existsByIdNumber(request.getIdNumber())) {
            throw new RuntimeException("Le numéro d'identité existe déjà");
        }

        // Créer l'utilisateur
        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPasswordHash(passwordEncoder.encode(request.getPassword()));
        user.setFirstName(request.getFirstName());
        user.setLastName(request.getLastName());
        user.setPhone(request.getPhone());
        user.setDateOfBirth(request.getDateOfBirth());
        user.setNationality(request.getNationality());
        user.setIdNumber(request.getIdNumber());
        user.setIdType(request.getIdType());
        user.setAddressLine1(request.getAddressLine1());
        user.setAddressLine2(request.getAddressLine2());
        user.setCity(request.getCity());
        user.setState(request.getState());
        user.setPostalCode(request.getPostalCode());
        user.setCountry(request.getCountry());
        user.setOccupation(request.getOccupation());
        user.setEmployer(request.getEmployer());
        user.setAnnualIncome(request.getAnnualIncome());
        user.setSourceOfFunds(request.getSourceOfFunds());
        user.setPreferredLanguage(request.getPreferredLanguage());
        user.setTimezone(request.getTimezone());

        // Évaluer le risque initial
        int riskScore = riskAssessmentService.calculateInitialRiskScore(user);
        user.setRiskScore(riskScore);
        user.setRiskLevel(RiskLevel.fromScore(riskScore));

        // Sauvegarder l'utilisateur
        user = userRepository.save(user);

        // Auditer l'enregistrement
        auditService.logUserRegistration(user.getId(), request.getUsername(), true, null);

        return new UserRegistrationResponse(
                user.getId(),
                user.getUsername(),
                user.getEmail(),
                user.getFullName(),
                user.getKycStatus(),
                user.getAmlStatus(),
                user.getRiskLevel()
        );
    }

    /**
     * Met à jour le profil d'un utilisateur
     */
    public UserProfileResponse updateUserProfile(UUID userId, UserProfileUpdateRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        // Mettre à jour les champs autorisés
        if (request.getPhone() != null) user.setPhone(request.getPhone());
        if (request.getAddressLine1() != null) user.setAddressLine1(request.getAddressLine1());
        if (request.getAddressLine2() != null) user.setAddressLine2(request.getAddressLine2());
        if (request.getCity() != null) user.setCity(request.getCity());
        if (request.getState() != null) user.setState(request.getState());
        if (request.getPostalCode() != null) user.setPostalCode(request.getPostalCode());
        if (request.getCountry() != null) user.setCountry(request.getCountry());
        if (request.getOccupation() != null) user.setOccupation(request.getOccupation());
        if (request.getEmployer() != null) user.setEmployer(request.getEmployer());
        if (request.getAnnualIncome() != null) user.setAnnualIncome(request.getAnnualIncome());
        if (request.getSourceOfFunds() != null) user.setSourceOfFunds(request.getSourceOfFunds());
        if (request.getPreferredLanguage() != null) user.setPreferredLanguage(request.getPreferredLanguage());
        if (request.getTimezone() != null) user.setTimezone(request.getTimezone());

        // Recalculer le score de risque si nécessaire
        if (request.getAnnualIncome() != null || request.getSourceOfFunds() != null) {
            int newRiskScore = riskAssessmentService.calculateRiskScore(user);
            user.setRiskScore(newRiskScore);
            user.setRiskLevel(RiskLevel.fromScore(newRiskScore));
        }

        user = userRepository.save(user);

        // Auditer la mise à jour
        auditService.logUserProfileUpdate(userId, request.getUsername(), true, null);

        return createUserProfileResponse(user);
    }

    /**
     * Change le mot de passe d'un utilisateur
     */
    public void changePassword(UUID userId, PasswordChangeRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        // Vérifier l'ancien mot de passe
        if (!passwordEncoder.matches(request.getOldPassword(), user.getPasswordHash())) {
            throw new RuntimeException("Ancien mot de passe incorrect");
        }

        // Vérifier que le nouveau mot de passe est différent
        if (passwordEncoder.matches(request.getNewPassword(), user.getPasswordHash())) {
            throw new RuntimeException("Le nouveau mot de passe doit être différent de l'ancien");
        }

        // Encoder et sauvegarder le nouveau mot de passe
        user.setPasswordHash(passwordEncoder.encode(request.getNewPassword()));
        user.setPasswordChangedDate(LocalDateTime.now());
        userRepository.save(user);

        // Auditer le changement de mot de passe
        auditService.logPasswordChange(userId, user.getUsername(), true, null);
    }

    /**
     * Active ou désactive MFA pour un utilisateur
     */
    public void toggleMfa(UUID userId, MfaToggleRequest request) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        if (request.isEnable()) {
            // Générer un secret MFA
            String mfaSecret = generateMfaSecret();
            user.setMfaSecret(mfaSecret);
            user.setMfaEnabled(true);
        } else {
            user.setMfaSecret(null);
            user.setMfaEnabled(false);
        }

        userRepository.save(user);

        // Auditer le changement MFA
        auditService.logMfaToggle(userId, user.getUsername(), request.isEnable(), null);
    }

    /**
     * Déverrouille un compte utilisateur
     */
    public void unlockUserAccount(UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        user.resetFailedLoginAttempts();
        userRepository.save(user);

        // Auditer le déverrouillage
        auditService.logAccountUnlock(userId, user.getUsername(), true, null);
    }

    /**
     * Désactive un compte utilisateur
     */
    public void deactivateUserAccount(UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        user.setIsActive(false);
        userRepository.save(user);

        // Auditer la désactivation
        auditService.logAccountDeactivation(userId, user.getUsername(), true, null);
    }

    /**
     * Met à jour le statut KYC d'un utilisateur
     */
    public void updateKycStatus(UUID userId, KYCStatus kycStatus, String reason) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        user.setKycStatus(kycStatus);
        userRepository.save(user);

        // Auditer la mise à jour KYC
        auditService.logKycStatusUpdate(userId, user.getUsername(), kycStatus, reason);
    }

    /**
     * Met à jour le statut AML d'un utilisateur
     */
    public void updateAmlStatus(UUID userId, AMLStatus amlStatus, String reason) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("Utilisateur non trouvé"));

        user.setAmlStatus(amlStatus);
        userRepository.save(user);

        // Auditer la mise à jour AML
        auditService.logAmlStatusUpdate(userId, user.getUsername(), amlStatus, reason);
    }

    /**
     * Recherche des utilisateurs avec pagination
     */
    public Page<UserProfileResponse> searchUsers(UserSearchRequest request, Pageable pageable) {
        Page<User> users = userRepository.findUsersByCriteria(
                request.getUsername(),
                request.getEmail(),
                request.getFirstName(),
                request.getLastName(),
                request.getKycStatus(),
                request.getAmlStatus(),
                request.getRiskLevel(),
                request.getIsActive(),
                request.getIsLocked(),
                request.getNationality(),
                request.getCountry(),
                pageable
        );

        return users.map(this::createUserProfileResponse);
    }

    /**
     * Trouve les utilisateurs nécessitant une surveillance renforcée
     */
    public List<UserProfileResponse> findUsersRequiringEnhancedDueDiligence() {
        return userRepository.findUsersRequiringEnhancedDueDiligence()
                .stream()
                .map(this::createUserProfileResponse)
                .collect(Collectors.toList());
    }

    /**
     * Trouve les utilisateurs inactifs
     */
    public List<UserProfileResponse> findInactiveUsers(LocalDateTime cutoffDate) {
        return userRepository.findInactiveUsers(cutoffDate)
                .stream()
                .map(this::createUserProfileResponse)
                .collect(Collectors.toList());
    }

    /**
     * Obtient les statistiques des utilisateurs
     */
    public UserStatisticsResponse getUserStatistics() {
        long totalUsers = userRepository.count();
        long activeUsers = userRepository.findByIsActiveTrue().size();
        long lockedUsers = userRepository.findByIsLockedTrue().size();
        long mfaEnabledUsers = userRepository.findByMfaEnabledTrue().size();

        List<Object[]> kycStats = userRepository.countUsersByKycStatus();
        List<Object[]> riskStats = userRepository.countUsersByRiskLevel();

        return new UserStatisticsResponse(
                totalUsers,
                activeUsers,
                lockedUsers,
                mfaEnabledUsers,
                kycStats,
                riskStats
        );
    }

    // Méthodes privées utilitaires

    private UserDetails createUserDetails(User user) {
        List<SimpleGrantedAuthority> authorities = new ArrayList<>();
        authorities.add(new SimpleGrantedAuthority("ROLE_USER"));

        if (user.getRiskLevel() == RiskLevel.CRITICAL) {
            authorities.add(new SimpleGrantedAuthority("ROLE_HIGH_RISK"));
        }

        return new org.springframework.security.core.userdetails.User(
                user.getUsername(),
                user.getPasswordHash(),
                user.getIsActive() && !user.getIsLocked(),
                true, // account non-expired
                true, // credentials non-expired
                true, // account non-locked
                authorities
        );
    }

    private void handleFailedLogin(User user) {
        user.incrementFailedLoginAttempts();
        userRepository.save(user);

        // Auditer l'échec de connexion
        auditService.logUserLogin(user.getId(), user.getUsername(), false, "Mot de passe incorrect");
    }

    private String generateMfaSecret() {
        // Générer un secret TOTP de 32 caractères
        return UUID.randomUUID().toString().replace("-", "").substring(0, 32);
    }

    private UserProfileResponse createUserProfileResponse(User user) {
        return new UserProfileResponse(
                user.getId(),
                user.getUsername(),
                user.getEmail(),
                user.getFullName(),
                user.getPhone(),
                user.getDateOfBirth(),
                user.getNationality(),
                user.getIdNumber(),
                user.getIdType(),
                user.getAddressLine1(),
                user.getAddressLine2(),
                user.getCity(),
                user.getState(),
                user.getPostalCode(),
                user.getCountry(),
                user.getOccupation(),
                user.getEmployer(),
                user.getAnnualIncome(),
                user.getSourceOfFunds(),
                user.getKycStatus(),
                user.getAmlStatus(),
                user.getRiskScore(),
                user.getRiskLevel(),
                user.getIsActive(),
                user.getIsLocked(),
                user.getMfaEnabled(),
                user.getPreferredLanguage(),
                user.getTimezone(),
                user.getCreatedAt(),
                user.getUpdatedAt()
        );
    }
}
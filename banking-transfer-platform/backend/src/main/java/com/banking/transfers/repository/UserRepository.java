package com.banking.transfers.repository;

import com.banking.transfers.model.User;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.AMLStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository pour la gestion des utilisateurs
 */
@Repository
public interface UserRepository extends JpaRepository<User, UUID> {

    /**
     * Trouve un utilisateur par son nom d'utilisateur
     */
    Optional<User> findByUsername(String username);

    /**
     * Trouve un utilisateur par son email
     */
    Optional<User> findByEmail(String email);

    /**
     * Trouve un utilisateur par son nom d'utilisateur ou email
     */
    Optional<User> findByUsernameOrEmail(String username, String email);

    /**
     * Vérifie si un nom d'utilisateur existe
     */
    boolean existsByUsername(String username);

    /**
     * Vérifie si un email existe
     */
    boolean existsByEmail(String email);

    /**
     * Trouve les utilisateurs actifs
     */
    List<User> findByIsActiveTrue();

    /**
     * Trouve les utilisateurs verrouillés
     */
    List<User> findByIsLockedTrue();

    /**
     * Trouve les utilisateurs par statut KYC
     */
    List<User> findByKycStatus(KYCStatus kycStatus);

    /**
     * Trouve les utilisateurs par statut AML
     */
    List<User> findByAmlStatus(AMLStatus amlStatus);

    /**
     * Trouve les utilisateurs avec un score de risque élevé
     */
    @Query("SELECT u FROM User u WHERE u.riskScore >= :minRiskScore")
    List<User> findByRiskScoreGreaterThanEqual(@Param("minRiskScore") Integer minRiskScore);

    /**
     * Trouve les utilisateurs par nationalité
     */
    List<User> findByNationality(String nationality);

    /**
     * Trouve les utilisateurs par pays
     */
    List<User> findByCountry(String country);

    /**
     * Trouve les utilisateurs créés après une date donnée
     */
    List<User> findByCreatedAtAfter(LocalDateTime date);

    /**
     * Trouve les utilisateurs qui se sont connectés après une date donnée
     */
    List<User> findByLastLoginDateAfter(LocalDateTime date);

    /**
     * Trouve les utilisateurs qui ne se sont jamais connectés
     */
    List<User> findByLastLoginDateIsNull();

    /**
     * Trouve les utilisateurs avec MFA activé
     */
    List<User> findByMfaEnabledTrue();

    /**
     * Trouve les utilisateurs avec des tentatives de connexion échouées
     */
    @Query("SELECT u FROM User u WHERE u.failedLoginAttempts > 0")
    List<User> findUsersWithFailedLoginAttempts();

    /**
     * Trouve les utilisateurs avec des tentatives de connexion échouées supérieures à un seuil
     */
    @Query("SELECT u FROM User u WHERE u.failedLoginAttempts >= :threshold")
    List<User> findUsersWithFailedLoginAttemptsAbove(@Param("threshold") Integer threshold);

    /**
     * Recherche avancée d'utilisateurs
     */
    @Query("SELECT u FROM User u WHERE " +
           "(:username IS NULL OR LOWER(u.username) LIKE LOWER(CONCAT('%', :username, '%'))) AND " +
           "(:email IS NULL OR LOWER(u.email) LIKE LOWER(CONCAT('%', :email, '%'))) AND " +
           "(:firstName IS NULL OR LOWER(u.firstName) LIKE LOWER(CONCAT('%', :firstName, '%'))) AND " +
           "(:lastName IS NULL OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :lastName, '%'))) AND " +
           "(:kycStatus IS NULL OR u.kycStatus = :kycStatus) AND " +
           "(:amlStatus IS NULL OR u.amlStatus = :amlStatus) AND " +
           "(:isActive IS NULL OR u.isActive = :isActive) AND " +
           "(:isLocked IS NULL OR u.isLocked = :isLocked) AND " +
           "(:nationality IS NULL OR u.nationality = :nationality) AND " +
           "(:country IS NULL OR u.country = :country)")
    Page<User> findUsersByCriteria(
            @Param("username") String username,
            @Param("email") String email,
            @Param("firstName") String firstName,
            @Param("lastName") String lastName,
            @Param("kycStatus") KYCStatus kycStatus,
            @Param("amlStatus") AMLStatus amlStatus,
            @Param("isActive") Boolean isActive,
            @Param("isLocked") Boolean isLocked,
            @Param("nationality") String nationality,
            @Param("country") String country,
            Pageable pageable
    );

    /**
     * Compte les utilisateurs par statut KYC
     */
    @Query("SELECT u.kycStatus, COUNT(u) FROM User u GROUP BY u.kycStatus")
    List<Object[]> countUsersByKycStatus();

    /**
     * Compte les utilisateurs par statut AML
     */
    @Query("SELECT u.amlStatus, COUNT(u) FROM User u GROUP BY u.amlStatus")
    List<Object[]> countUsersByAmlStatus();

    /**
     * Compte les utilisateurs par nationalité
     */
    @Query("SELECT u.nationality, COUNT(u) FROM User u WHERE u.nationality IS NOT NULL GROUP BY u.nationality ORDER BY COUNT(u) DESC")
    List<Object[]> countUsersByNationality();

    /**
     * Trouve les utilisateurs avec un mot de passe expiré
     */
    @Query("SELECT u FROM User u WHERE u.passwordChangedDate IS NOT NULL AND u.passwordChangedDate < :expiryDate")
    List<User> findUsersWithExpiredPassword(@Param("expiryDate") LocalDateTime expiryDate);

    /**
     * Trouve les utilisateurs inactifs depuis une période donnée
     */
    @Query("SELECT u FROM User u WHERE u.lastLoginDate IS NOT NULL AND u.lastLoginDate < :inactiveDate")
    List<User> findInactiveUsers(@Param("inactiveDate") LocalDateTime inactiveDate);

    /**
     * Trouve les utilisateurs créés dans une période donnée
     */
    @Query("SELECT u FROM User u WHERE u.createdAt BETWEEN :startDate AND :endDate")
    List<User> findUsersCreatedBetween(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate);

    /**
     * Trouve les utilisateurs avec un score de risque dans une plage donnée
     */
    @Query("SELECT u FROM User u WHERE u.riskScore BETWEEN :minRisk AND :maxRisk")
    List<User> findUsersByRiskScoreRange(@Param("minRisk") Integer minRisk, @Param("maxRisk") Integer maxRisk);

    /**
     * Trouve les utilisateurs par langue préférée
     */
    List<User> findByPreferredLanguage(String preferredLanguage);

    /**
     * Trouve les utilisateurs par fuseau horaire
     */
    List<User> findByTimezone(String timezone);

    /**
     * Trouve les utilisateurs avec un numéro de téléphone
     */
    @Query("SELECT u FROM User u WHERE u.phone IS NOT NULL AND u.phone != ''")
    List<User> findUsersWithPhone();

    /**
     * Trouve les utilisateurs par type de document d'identité
     */
    @Query("SELECT u FROM User u WHERE u.idType = :idType")
    List<User> findByDocumentType(@Param("idType") String idType);

    /**
     * Trouve les utilisateurs avec des informations d'identité complètes
     */
    @Query("SELECT u FROM User u WHERE u.idNumber IS NOT NULL AND u.idType IS NOT NULL")
    List<User> findUsersWithCompleteIdentity();

    /**
     * Trouve les utilisateurs avec des informations d'adresse complètes
     */
    @Query("SELECT u FROM User u WHERE u.address IS NOT NULL AND u.city IS NOT NULL AND u.country IS NOT NULL")
    List<User> findUsersWithCompleteAddress();

    /**
     * Trouve les utilisateurs éligibles pour les transferts (KYC vérifié et AML passé)
     */
    @Query("SELECT u FROM User u WHERE u.kycStatus = 'VERIFIED' AND u.amlStatus = 'PASSED' AND u.isActive = true AND u.isLocked = false")
    List<User> findEligibleUsersForTransfers();

    /**
     * Trouve les utilisateurs nécessitant une vérification KYC
     */
    @Query("SELECT u FROM User u WHERE u.kycStatus IN ('NOT_VERIFIED', 'PENDING', 'EXPIRED')")
    List<User> findUsersNeedingKycVerification();

    /**
     * Trouve les utilisateurs nécessitant une vérification AML
     */
    @Query("SELECT u FROM User u WHERE u.amlStatus IN ('NOT_CHECKED', 'PENDING', 'PENDING_CLARIFICATION')")
    List<User> findUsersNeedingAmlVerification();
}
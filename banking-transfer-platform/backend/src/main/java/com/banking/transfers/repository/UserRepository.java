package com.banking.transfers.repository;

import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.RiskLevel;
import com.banking.transfers.model.User;
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
     * Trouve un utilisateur par son numéro d'identité
     */
    Optional<User> findByIdNumber(String idNumber);

    /**
     * Vérifie si un nom d'utilisateur existe
     */
    boolean existsByUsername(String username);

    /**
     * Vérifie si un email existe
     */
    boolean existsByEmail(String email);

    /**
     * Vérifie si un numéro d'identité existe
     */
    boolean existsByIdNumber(String idNumber);

    /**
     * Trouve tous les utilisateurs actifs
     */
    List<User> findByIsActiveTrue();

    /**
     * Trouve tous les utilisateurs verrouillés
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
     * Trouve les utilisateurs par niveau de risque
     */
    List<User> findByRiskLevel(RiskLevel riskLevel);

    /**
     * Trouve les utilisateurs avec un score de risque supérieur à la valeur donnée
     */
    List<User> findByRiskScoreGreaterThan(Integer riskScore);

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
     * Trouve les utilisateurs créés entre deux dates
     */
    List<User> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate);

    /**
     * Trouve les utilisateurs qui se sont connectés après une date donnée
     */
    List<User> findByLastLoginDateAfter(LocalDateTime date);

    /**
     * Trouve les utilisateurs avec MFA activé
     */
    List<User> findByMfaEnabledTrue();

    /**
     * Trouve les utilisateurs avec un nombre d'échecs de connexion supérieur à la valeur donnée
     */
    List<User> findByFailedLoginAttemptsGreaterThan(Integer attempts);

    /**
     * Recherche avancée d'utilisateurs avec pagination
     */
    @Query("SELECT u FROM User u WHERE " +
           "(:username IS NULL OR u.username LIKE %:username%) AND " +
           "(:email IS NULL OR u.email LIKE %:email%) AND " +
           "(:firstName IS NULL OR u.firstName LIKE %:firstName%) AND " +
           "(:lastName IS NULL OR u.lastName LIKE %:lastName%) AND " +
           "(:kycStatus IS NULL OR u.kycStatus = :kycStatus) AND " +
           "(:amlStatus IS NULL OR u.amlStatus = :amlStatus) AND " +
           "(:riskLevel IS NULL OR u.riskLevel = :riskLevel) AND " +
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
            @Param("riskLevel") RiskLevel riskLevel,
            @Param("isActive") Boolean isActive,
            @Param("isLocked") Boolean isLocked,
            @Param("nationality") String nationality,
            @Param("country") String country,
            Pageable pageable
    );

    /**
     * Trouve les utilisateurs à haut risque nécessitant une surveillance
     */
    @Query("SELECT u FROM User u WHERE u.riskLevel IN ('HIGH', 'CRITICAL') OR u.kycStatus = 'PENDING' OR u.amlStatus = 'PENDING_CLARIFICATION'")
    List<User> findUsersRequiringEnhancedDueDiligence();

    /**
     * Trouve les utilisateurs inactifs depuis une période donnée
     */
    @Query("SELECT u FROM User u WHERE u.lastLoginDate < :cutoffDate OR u.lastLoginDate IS NULL")
    List<User> findInactiveUsers(@Param("cutoffDate") LocalDateTime cutoffDate);

    /**
     * Compte les utilisateurs par statut KYC
     */
    @Query("SELECT u.kycStatus, COUNT(u) FROM User u GROUP BY u.kycStatus")
    List<Object[]> countUsersByKycStatus();

    /**
     * Compte les utilisateurs par niveau de risque
     */
    @Query("SELECT u.riskLevel, COUNT(u) FROM User u GROUP BY u.riskLevel")
    List<Object[]> countUsersByRiskLevel();

    /**
     * Trouve les utilisateurs par nationalité avec pagination
     */
    Page<User> findByNationality(String nationality, Pageable pageable);

    /**
     * Trouve les utilisateurs par pays avec pagination
     */
    Page<User> findByCountry(String country, Pageable pageable);

    /**
     * Trouve les utilisateurs avec un revenu annuel supérieur à la valeur donnée
     */
    @Query("SELECT u FROM User u WHERE u.annualIncome > :minIncome")
    List<User> findUsersByMinIncome(@Param("minIncome") Double minIncome);

    /**
     * Trouve les utilisateurs par source de fonds
     */
    @Query("SELECT u FROM User u WHERE u.sourceOfFunds = :sourceOfFunds")
    List<User> findBySourceOfFunds(@Param("sourceOfFunds") String sourceOfFunds);

    /**
     * Trouve les utilisateurs avec des revenus d'investissement
     */
    @Query("SELECT u FROM User u WHERE u.sourceOfFunds IN ('INVESTMENT_INCOME', 'DIVIDENDS', 'INTEREST')")
    List<User> findUsersWithInvestmentIncome();

    /**
     * Trouve les utilisateurs avec des sources de fonds à haut risque
     */
    @Query("SELECT u FROM User u WHERE u.sourceOfFunds IN ('CRYPTO_CURRENCY', 'GAMBLING_WINNINGS', 'GIFT', 'INHERITANCE', 'LEGAL_SETTLEMENT')")
    List<User> findUsersWithHighRiskSourceOfFunds();

    /**
     * Trouve les utilisateurs par type de document d'identité
     */
    @Query("SELECT u FROM User u WHERE u.idType = :idType")
    List<User> findByIdType(@Param("idType") String idType);

    /**
     * Trouve les utilisateurs avec des documents d'identité gouvernementaux
     */
    @Query("SELECT u FROM User u WHERE u.idType IN ('PASSPORT', 'NATIONAL_ID', 'DRIVERS_LICENSE', 'RESIDENCE_PERMIT', 'MILITARY_ID', 'WORK_PERMIT', 'REFUGEE_ID')")
    List<User> findUsersWithGovernmentIssuedIds();

    /**
     * Trouve les utilisateurs par langue préférée
     */
    List<User> findByPreferredLanguage(String preferredLanguage);

    /**
     * Trouve les utilisateurs par fuseau horaire
     */
    List<User> findByTimezone(String timezone);

    /**
     * Trouve les utilisateurs créés par un utilisateur spécifique
     */
    List<User> findByCreatedBy(String createdBy);

    /**
     * Trouve les utilisateurs modifiés par un utilisateur spécifique
     */
    List<User> findByUpdatedBy(String updatedBy);

    /**
     * Trouve les utilisateurs avec un nom d'utilisateur contenant le terme de recherche
     */
    List<User> findByUsernameContainingIgnoreCase(String username);

    /**
     * Trouve les utilisateurs avec un email contenant le terme de recherche
     */
    List<User> findByEmailContainingIgnoreCase(String email);

    /**
     * Trouve les utilisateurs avec un nom contenant le terme de recherche
     */
    @Query("SELECT u FROM User u WHERE LOWER(u.firstName) LIKE LOWER(CONCAT('%', :name, '%')) OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<User> findByNameContainingIgnoreCase(@Param("name") String name);

    /**
     * Trouve les utilisateurs par occupation
     */
    List<User> findByOccupation(String occupation);

    /**
     * Trouve les utilisateurs par employeur
     */
    List<User> findByEmployer(String employer);

    /**
     * Trouve les utilisateurs avec un numéro de téléphone contenant le terme de recherche
     */
    List<User> findByPhoneContaining(String phone);

    /**
     * Trouve les utilisateurs nés entre deux dates
     */
    @Query("SELECT u FROM User u WHERE u.dateOfBirth BETWEEN :startDate AND :endDate")
    List<User> findByDateOfBirthBetween(@Param("startDate") String startDate, @Param("endDate") String endDate);

    /**
     * Trouve les utilisateurs avec un âge supérieur à la valeur donnée
     */
    @Query("SELECT u FROM User u WHERE u.dateOfBirth < :cutoffDate")
    List<User> findUsersOlderThan(@Param("cutoffDate") String cutoffDate);

    /**
     * Trouve les utilisateurs avec un âge inférieur à la valeur donnée
     */
    @Query("SELECT u FROM User u WHERE u.dateOfBirth > :cutoffDate")
    List<User> findUsersYoungerThan(@Param("cutoffDate") String cutoffDate);
}
package com.banking.transfers.repository;

import com.banking.transfers.model.User;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.RiskLevel;
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

    // Recherche par nom d'utilisateur
    Optional<User> findByUsername(String username);

    // Recherche par email
    Optional<User> findByEmail(String email);

    // Recherche par numéro d'identité
    Optional<User> findByIdNumber(String idNumber);

    // Recherche par ID Keycloak
    Optional<User> findByKeycloakId(String keycloakId);

    // Recherche par nom d'utilisateur ou email
    Optional<User> findByUsernameOrEmail(String username, String email);

    // Vérification d'existence
    boolean existsByUsername(String username);
    boolean existsByEmail(String email);
    boolean existsByIdNumber(String idNumber);

    // Recherche par statut KYC
    List<User> findByKycStatus(KYCStatus kycStatus);
    Page<User> findByKycStatus(KYCStatus kycStatus, Pageable pageable);

    // Recherche par statut AML
    List<User> findByAmlStatus(AMLStatus amlStatus);
    Page<User> findByAmlStatus(AMLStatus amlStatus, Pageable pageable);

    // Recherche par niveau de risque
    List<User> findByRiskLevel(RiskLevel riskLevel);
    Page<User> findByRiskLevel(RiskLevel riskLevel, Pageable pageable);

    // Recherche par statut actif
    List<User> findByIsActiveTrue();
    List<User> findByIsActiveFalse();

    // Recherche par statut verrouillé
    List<User> findByIsLockedTrue();
    List<User> findByIsLockedFalse();

    // Recherche par nationalité
    List<User> findByNationality(String nationality);
    Page<User> findByNationality(String nationality, Pageable pageable);

    // Recherche par pays
    List<User> findByCountry(String country);
    Page<User> findByCountry(String country, Pageable pageable);

    // Recherche par nom (prénom ou nom de famille)
    @Query("SELECT u FROM User u WHERE LOWER(u.firstName) LIKE LOWER(CONCAT('%', :name, '%')) OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<User> findByNameContainingIgnoreCase(@Param("name") String name);

    @Query("SELECT u FROM User u WHERE LOWER(u.firstName) LIKE LOWER(CONCAT('%', :name, '%')) OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :name, '%'))")
    Page<User> findByNameContainingIgnoreCase(@Param("name") String name, Pageable pageable);

    // Recherche par plage de dates de création
    List<User> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate);
    Page<User> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate, Pageable pageable);

    // Recherche par dernière connexion
    List<User> findByLastLoginDateBefore(LocalDateTime date);
    List<User> findByLastLoginDateIsNull();

    // Recherche d'utilisateurs inactifs depuis longtemps
    @Query("SELECT u FROM User u WHERE u.lastLoginDate < :date OR u.lastLoginDate IS NULL")
    List<User> findInactiveUsers(@Param("date") LocalDateTime date);

    // Recherche d'utilisateurs à risque élevé
    @Query("SELECT u FROM User u WHERE u.riskLevel IN ('HIGH', 'CRITICAL') OR u.kycStatus = 'PENDING' OR u.amlStatus = 'PENDING'")
    List<User> findHighRiskUsers();

    @Query("SELECT u FROM User u WHERE u.riskLevel IN ('HIGH', 'CRITICAL') OR u.kycStatus = 'PENDING' OR u.amlStatus = 'PENDING'")
    Page<User> findHighRiskUsers(Pageable pageable);

    // Recherche d'utilisateurs nécessitant une vérification KYC
    @Query("SELECT u FROM User u WHERE u.kycStatus IN ('NOT_VERIFIED', 'PENDING')")
    List<User> findUsersRequiringKYC();

    @Query("SELECT u FROM User u WHERE u.kycStatus IN ('NOT_VERIFIED', 'PENDING')")
    Page<User> findUsersRequiringKYC(Pageable pageable);

    // Recherche d'utilisateurs nécessitant une vérification AML
    @Query("SELECT u FROM User u WHERE u.amlStatus IN ('NOT_CHECKED', 'PENDING')")
    List<User> findUsersRequiringAML();

    @Query("SELECT u FROM User u WHERE u.amlStatus IN ('NOT_CHECKED', 'PENDING')")
    Page<User> findUsersRequiringAML(Pageable pageable);

    // Recherche d'utilisateurs avec MFA activé
    List<User> findByMfaEnabledTrue();
    List<User> findByMfaEnabledFalse();

    // Recherche d'utilisateurs avec échecs de connexion
    @Query("SELECT u FROM User u WHERE u.failedLoginAttempts >= :threshold")
    List<User> findUsersWithFailedLogins(@Param("threshold") int threshold);

    // Recherche d'utilisateurs par plage de revenus
    @Query("SELECT u FROM User u WHERE u.annualIncome BETWEEN :minIncome AND :maxIncome")
    List<User> findByAnnualIncomeBetween(@Param("minIncome") Double minIncome, @Param("maxIncome") Double maxIncome);

    // Recherche d'utilisateurs par occupation
    List<User> findByOccupation(String occupation);
    Page<User> findByOccupation(String occupation, Pageable pageable);

    // Recherche d'utilisateurs par employeur
    List<User> findByEmployer(String employer);
    Page<User> findByEmployer(String employer, Pageable pageable);

    // Statistiques
    @Query("SELECT COUNT(u) FROM User u WHERE u.kycStatus = :status")
    long countByKycStatus(@Param("status") KYCStatus status);

    @Query("SELECT COUNT(u) FROM User u WHERE u.amlStatus = :status")
    long countByAmlStatus(@Param("status") AMLStatus status);

    @Query("SELECT COUNT(u) FROM User u WHERE u.riskLevel = :level")
    long countByRiskLevel(@Param("level") RiskLevel level);

    @Query("SELECT COUNT(u) FROM User u WHERE u.isActive = true")
    long countActiveUsers();

    @Query("SELECT COUNT(u) FROM User u WHERE u.isLocked = true")
    long countLockedUsers();

    @Query("SELECT COUNT(u) FROM User u WHERE u.mfaEnabled = true")
    long countUsersWithMFA();

    // Recherche complexe avec plusieurs critères
    @Query("SELECT u FROM User u WHERE " +
           "(:username IS NULL OR LOWER(u.username) LIKE LOWER(CONCAT('%', :username, '%'))) AND " +
           "(:email IS NULL OR LOWER(u.email) LIKE LOWER(CONCAT('%', :email, '%'))) AND " +
           "(:firstName IS NULL OR LOWER(u.firstName) LIKE LOWER(CONCAT('%', :firstName, '%'))) AND " +
           "(:lastName IS NULL OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :lastName, '%'))) AND " +
           "(:nationality IS NULL OR u.nationality = :nationality) AND " +
           "(:country IS NULL OR u.country = :country) AND " +
           "(:kycStatus IS NULL OR u.kycStatus = :kycStatus) AND " +
           "(:amlStatus IS NULL OR u.amlStatus = :amlStatus) AND " +
           "(:riskLevel IS NULL OR u.riskLevel = :riskLevel) AND " +
           "(:isActive IS NULL OR u.isActive = :isActive) AND " +
           "(:isLocked IS NULL OR u.isLocked = :isLocked)")
    Page<User> findByMultipleCriteria(
            @Param("username") String username,
            @Param("email") String email,
            @Param("firstName") String firstName,
            @Param("lastName") String lastName,
            @Param("nationality") String nationality,
            @Param("country") String country,
            @Param("kycStatus") KYCStatus kycStatus,
            @Param("amlStatus") AMLStatus amlStatus,
            @Param("riskLevel") RiskLevel riskLevel,
            @Param("isActive") Boolean isActive,
            @Param("isLocked") Boolean isLocked,
            Pageable pageable
    );

    // Recherche d'utilisateurs créés récemment
    @Query("SELECT u FROM User u WHERE u.createdAt >= :since")
    List<User> findRecentlyCreatedUsers(@Param("since") LocalDateTime since);

    // Recherche d'utilisateurs connectés récemment
    @Query("SELECT u FROM User u WHERE u.lastLoginDate >= :since")
    List<User> findRecentlyActiveUsers(@Param("since") LocalDateTime since);

    // Recherche d'utilisateurs par type de document d'identité
    @Query("SELECT u FROM User u WHERE u.idType = :idType")
    List<User> findByIdType(@Param("idType") String idType);

    // Recherche d'utilisateurs par source de fonds
    @Query("SELECT u FROM User u WHERE u.sourceOfFunds = :sourceOfFunds")
    List<User> findBySourceOfFunds(@Param("sourceOfFunds") String sourceOfFunds);
}
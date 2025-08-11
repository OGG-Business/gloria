package com.banking.transfers.repository;

import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.KYCStatus;
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
     * Trouve un utilisateur par son nom d'utilisateur et vérifie qu'il est actif
     */
    Optional<User> findByUsernameAndIsActiveTrue(String username);

    /**
     * Trouve un utilisateur par son email et vérifie qu'il est actif
     */
    Optional<User> findByEmailAndIsActiveTrue(String email);

    /**
     * Trouve un utilisateur par son numéro d'identité
     */
    Optional<User> findByIdNumber(String idNumber);

    /**
     * Trouve un utilisateur par son numéro d'identité et son type
     */
    Optional<User> findByIdNumberAndIdType(String idNumber, String idType);

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
     * Trouve tous les utilisateurs inactifs
     */
    List<User> findByIsActiveFalse();

    /**
     * Trouve tous les utilisateurs verrouillés
     */
    List<User> findByIsLockedTrue();

    /**
     * Trouve tous les utilisateurs avec un statut KYC spécifique
     */
    List<User> findByKycStatus(KYCStatus kycStatus);

    /**
     * Trouve tous les utilisateurs avec un statut AML spécifique
     */
    List<User> findByAmlStatus(AMLStatus amlStatus);

    /**
     * Trouve tous les utilisateurs avec un score de risque supérieur à une valeur donnée
     */
    List<User> findByRiskScoreGreaterThan(Integer riskScore);

    /**
     * Trouve tous les utilisateurs avec MFA activé
     */
    List<User> findByMfaEnabledTrue();

    /**
     * Trouve tous les utilisateurs avec MFA désactivé
     */
    List<User> findByMfaEnabledFalse();

    /**
     * Trouve tous les utilisateurs créés après une date donnée
     */
    List<User> findByCreatedAtAfter(LocalDateTime date);

    /**
     * Trouve tous les utilisateurs créés avant une date donnée
     */
    List<User> findByCreatedAtBefore(LocalDateTime date);

    /**
     * Trouve tous les utilisateurs qui se sont connectés après une date donnée
     */
    List<User> findByLastLoginDateAfter(LocalDateTime date);

    /**
     * Trouve tous les utilisateurs qui ne se sont jamais connectés
     */
    List<User> findByLastLoginDateIsNull();

    /**
     * Trouve tous les utilisateurs par nationalité
     */
    List<User> findByNationality(String nationality);

    /**
     * Trouve tous les utilisateurs par type de document d'identité
     */
    List<User> findByIdType(String idType);

    /**
     * Recherche d'utilisateurs par nom (prénom ou nom de famille)
     */
    @Query("SELECT u FROM User u WHERE LOWER(u.firstName) LIKE LOWER(CONCAT('%', :name, '%')) OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<User> findByNameContainingIgnoreCase(@Param("name") String name);

    /**
     * Recherche d'utilisateurs par nom avec pagination
     */
    @Query("SELECT u FROM User u WHERE LOWER(u.firstName) LIKE LOWER(CONCAT('%', :name, '%')) OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :name, '%'))")
    Page<User> findByNameContainingIgnoreCase(@Param("name") String name, Pageable pageable);

    /**
     * Trouve tous les utilisateurs avec un rôle spécifique
     */
    @Query("SELECT u FROM User u JOIN u.roles r WHERE r = :role")
    List<User> findByRole(@Param("role") String role);

    /**
     * Trouve tous les utilisateurs avec une permission spécifique
     */
    @Query("SELECT u FROM User u JOIN u.permissions p WHERE p = :permission")
    List<User> findByPermission(@Param("permission") String permission);

    /**
     * Trouve tous les utilisateurs avec plusieurs rôles
     */
    @Query("SELECT u FROM User u JOIN u.roles r WHERE r IN :roles")
    List<User> findByRolesIn(@Param("roles") List<String> roles);

    /**
     * Trouve tous les utilisateurs avec plusieurs permissions
     */
    @Query("SELECT u FROM User u JOIN u.permissions p WHERE p IN :permissions")
    List<User> findByPermissionsIn(@Param("permissions") List<String> permissions);

    /**
     * Trouve tous les utilisateurs non conformes (KYC non vérifié ou AML échoué)
     */
    @Query("SELECT u FROM User u WHERE u.kycStatus != 'VERIFIED' OR u.amlStatus = 'FAILED' OR u.amlStatus = 'BLOCKED'")
    List<User> findNonCompliantUsers();

    /**
     * Trouve tous les utilisateurs avec des tentatives de connexion échouées
     */
    @Query("SELECT u FROM User u WHERE u.failedLoginAttempts > 0")
    List<User> findUsersWithFailedLoginAttempts();

    /**
     * Trouve tous les utilisateurs avec des mots de passe expirés (plus de 90 jours)
     */
    @Query("SELECT u FROM User u WHERE u.passwordChangedDate < :expiryDate")
    List<User> findUsersWithExpiredPasswords(@Param("expiryDate") LocalDateTime expiryDate);

    /**
     * Trouve tous les utilisateurs inactifs depuis une date donnée
     */
    @Query("SELECT u FROM User u WHERE u.lastLoginDate < :inactiveDate OR u.lastLoginDate IS NULL")
    List<User> findInactiveUsers(@Param("inactiveDate") LocalDateTime inactiveDate);

    /**
     * Compte le nombre d'utilisateurs par statut KYC
     */
    @Query("SELECT u.kycStatus, COUNT(u) FROM User u GROUP BY u.kycStatus")
    List<Object[]> countUsersByKycStatus();

    /**
     * Compte le nombre d'utilisateurs par statut AML
     */
    @Query("SELECT u.amlStatus, COUNT(u) FROM User u GROUP BY u.amlStatus")
    List<Object[]> countUsersByAmlStatus();

    /**
     * Compte le nombre d'utilisateurs par nationalité
     */
    @Query("SELECT u.nationality, COUNT(u) FROM User u WHERE u.nationality IS NOT NULL GROUP BY u.nationality")
    List<Object[]> countUsersByNationality();

    /**
     * Trouve les utilisateurs avec un score de risque élevé (supérieur à 7)
     */
    @Query("SELECT u FROM User u WHERE u.riskScore >= 7 ORDER BY u.riskScore DESC")
    List<User> findHighRiskUsers();

    /**
     * Trouve les utilisateurs créés dans une période donnée
     */
    @Query("SELECT u FROM User u WHERE u.createdAt BETWEEN :startDate AND :endDate")
    List<User> findUsersCreatedBetween(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate);

    /**
     * Trouve les utilisateurs qui se sont connectés dans une période donnée
     */
    @Query("SELECT u FROM User u WHERE u.lastLoginDate BETWEEN :startDate AND :endDate")
    List<User> findUsersLoggedInBetween(@Param("startDate") LocalDateTime startDate, @Param("endDate") LocalDateTime endDate);

    /**
     * Recherche avancée d'utilisateurs avec plusieurs critères
     */
    @Query("SELECT u FROM User u WHERE " +
           "(:username IS NULL OR LOWER(u.username) LIKE LOWER(CONCAT('%', :username, '%'))) AND " +
           "(:email IS NULL OR LOWER(u.email) LIKE LOWER(CONCAT('%', :email, '%'))) AND " +
           "(:firstName IS NULL OR LOWER(u.firstName) LIKE LOWER(CONCAT('%', :firstName, '%'))) AND " +
           "(:lastName IS NULL OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :lastName, '%'))) AND " +
           "(:nationality IS NULL OR u.nationality = :nationality) AND " +
           "(:kycStatus IS NULL OR u.kycStatus = :kycStatus) AND " +
           "(:amlStatus IS NULL OR u.amlStatus = :amlStatus) AND " +
           "(:isActive IS NULL OR u.isActive = :isActive) AND " +
           "(:isLocked IS NULL OR u.isLocked = :isLocked)")
    Page<User> findUsersByCriteria(
            @Param("username") String username,
            @Param("email") String email,
            @Param("firstName") String firstName,
            @Param("lastName") String lastName,
            @Param("nationality") String nationality,
            @Param("kycStatus") KYCStatus kycStatus,
            @Param("amlStatus") AMLStatus amlStatus,
            @Param("isActive") Boolean isActive,
            @Param("isLocked") Boolean isLocked,
            Pageable pageable
    );
}
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
     * Trouve un utilisateur par son nom d'utilisateur ou email
     */
    @Query("SELECT u FROM User u WHERE u.username = :identifier OR u.email = :identifier")
    Optional<User> findByUsernameOrEmail(@Param("identifier") String identifier);

    /**
     * Trouve un utilisateur par son numéro d'identité
     */
    Optional<User> findByIdNumber(String idNumber);

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
     * Trouve les utilisateurs avec un score de risque supérieur ou égal à la valeur donnée
     */
    List<User> findByRiskScoreGreaterThanEqual(Integer riskScore);

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
     * Trouve les utilisateurs avec un nombre de tentatives de connexion échouées supérieur ou égal à la valeur donnée
     */
    List<User> findByFailedLoginAttemptsGreaterThanEqual(Integer attempts);

    /**
     * Trouve les utilisateurs par type de document d'identité
     */
    List<User> findByIdType(com.banking.transfers.model.IdType idType);

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
     * Trouve les utilisateurs par nom ou prénom (recherche insensible à la casse)
     */
    @Query("SELECT u FROM User u WHERE LOWER(u.firstName) LIKE LOWER(CONCAT('%', :name, '%')) OR LOWER(u.lastName) LIKE LOWER(CONCAT('%', :name, '%'))")
    List<User> findByFirstNameContainingIgnoreCaseOrLastNameContainingIgnoreCase(@Param("name") String name);

    /**
     * Trouve les utilisateurs par téléphone
     */
    List<User> findByPhone(String phone);

    /**
     * Trouve les utilisateurs avec un score de risque élevé (>= 70)
     */
    @Query("SELECT u FROM User u WHERE u.riskScore >= 70")
    List<User> findHighRiskUsers();

    /**
     * Trouve les utilisateurs nécessitant une vérification KYC
     */
    @Query("SELECT u FROM User u WHERE u.kycStatus IN ('NOT_VERIFIED', 'PENDING')")
    List<User> findUsersRequiringKYCVerification();

    /**
     * Trouve les utilisateurs nécessitant une vérification AML
     */
    @Query("SELECT u FROM User u WHERE u.amlStatus IN ('NOT_CHECKED', 'PENDING')")
    List<User> findUsersRequiringAMLVerification();

    /**
     * Trouve les utilisateurs inactifs depuis une date donnée
     */
    @Query("SELECT u FROM User u WHERE u.lastLoginDate < :date OR u.lastLoginDate IS NULL")
    List<User> findInactiveUsersSince(@Param("date") LocalDateTime date);

    /**
     * Trouve les utilisateurs par rôle (recherche dans le JSON des rôles)
     */
    @Query("SELECT u FROM User u WHERE u.roles LIKE %:role%")
    List<User> findByRole(@Param("role") String role);

    /**
     * Trouve les utilisateurs par permission (recherche dans le JSON des permissions)
     */
    @Query("SELECT u FROM User u WHERE u.permissions LIKE %:permission%")
    List<User> findByPermission(@Param("permission") String permission);

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
     * Trouve les utilisateurs avec pagination et filtres
     */
    @Query("SELECT u FROM User u WHERE " +
           "(:username IS NULL OR u.username LIKE %:username%) AND " +
           "(:email IS NULL OR u.email LIKE %:email%) AND " +
           "(:firstName IS NULL OR u.firstName LIKE %:firstName%) AND " +
           "(:lastName IS NULL OR u.lastName LIKE %:lastName%) AND " +
           "(:kycStatus IS NULL OR u.kycStatus = :kycStatus) AND " +
           "(:amlStatus IS NULL OR u.amlStatus = :amlStatus) AND " +
           "(:isActive IS NULL OR u.isActive = :isActive) AND " +
           "(:isLocked IS NULL OR u.isLocked = :isLocked)")
    Page<User> findUsersWithFilters(
            @Param("username") String username,
            @Param("email") String email,
            @Param("firstName") String firstName,
            @Param("lastName") String lastName,
            @Param("kycStatus") KYCStatus kycStatus,
            @Param("amlStatus") AMLStatus amlStatus,
            @Param("isActive") Boolean isActive,
            @Param("isLocked") Boolean isLocked,
            Pageable pageable
    );

    /**
     * Trouve les utilisateurs créés récemment (derniers 30 jours)
     */
    @Query("SELECT u FROM User u WHERE u.createdAt >= :thirtyDaysAgo ORDER BY u.createdAt DESC")
    List<User> findRecentlyCreatedUsers(@Param("thirtyDaysAgo") LocalDateTime thirtyDaysAgo);

    /**
     * Trouve les utilisateurs qui se sont connectés récemment (derniers 7 jours)
     */
    @Query("SELECT u FROM User u WHERE u.lastLoginDate >= :sevenDaysAgo ORDER BY u.lastLoginDate DESC")
    List<User> findRecentlyActiveUsers(@Param("sevenDaysAgo") LocalDateTime sevenDaysAgo);

    /**
     * Supprime les utilisateurs inactifs depuis plus d'un an
     */
    @Query("DELETE FROM User u WHERE u.lastLoginDate < :oneYearAgo AND u.isActive = false")
    int deleteInactiveUsers(@Param("oneYearAgo") LocalDateTime oneYearAgo);
}
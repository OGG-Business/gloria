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
 * Repository pour l'entité User
 */
@Repository
public interface UserRepository extends JpaRepository<User, UUID> {
    
    /**
     * Trouver un utilisateur par son nom d'utilisateur
     */
    Optional<User> findByUsername(String username);
    
    /**
     * Trouver un utilisateur par son email
     */
    Optional<User> findByEmail(String email);
    
    /**
     * Vérifier si un nom d'utilisateur existe
     */
    boolean existsByUsername(String username);
    
    /**
     * Vérifier si un email existe
     */
    boolean existsByEmail(String email);
    
    /**
     * Trouver des utilisateurs par statut KYC
     */
    List<User> findByKycStatus(KYCStatus kycStatus);
    
    /**
     * Trouver des utilisateurs par statut AML
     */
    List<User> findByAmlStatus(AMLStatus amlStatus);
    
    /**
     * Trouver des utilisateurs actifs
     */
    List<User> findByIsActiveTrue();
    
    /**
     * Trouver des utilisateurs verrouillés
     */
    List<User> findByIsLockedTrue();
    
    /**
     * Trouver des utilisateurs avec MFA activé
     */
    List<User> findByMfaEnabledTrue();
    
    /**
     * Trouver des utilisateurs par nationalité
     */
    List<User> findByNationality(String nationality);
    
    /**
     * Trouver des utilisateurs par pays
     */
    List<User> findByCountry(String country);
    
    /**
     * Trouver des utilisateurs avec un score de risque élevé
     */
    @Query("SELECT u FROM User u WHERE u.riskScore >= :minRiskScore")
    List<User> findByRiskScoreGreaterThanEqual(@Param("minRiskScore") Integer minRiskScore);
    
    /**
     * Trouver des utilisateurs créés après une date
     */
    List<User> findByCreatedAtAfter(LocalDateTime date);
    
    /**
     * Trouver des utilisateurs créés entre deux dates
     */
    List<User> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate);
    
    /**
     * Trouver des utilisateurs qui se sont connectés après une date
     */
    List<User> findByLastLoginDateAfter(LocalDateTime date);
    
    /**
     * Trouver des utilisateurs qui ne se sont jamais connectés
     */
    List<User> findByLastLoginDateIsNull();
    
    /**
     * Trouver des utilisateurs avec des tentatives de connexion échouées
     */
    @Query("SELECT u FROM User u WHERE u.failedLoginAttempts > 0")
    List<User> findUsersWithFailedLoginAttempts();
    
    /**
     * Trouver des utilisateurs avec des tentatives de connexion échouées supérieures à un seuil
     */
    @Query("SELECT u FROM User u WHERE u.failedLoginAttempts >= :threshold")
    List<User> findUsersWithFailedLoginAttemptsAbove(@Param("threshold") Integer threshold);
    
    /**
     * Recherche d'utilisateurs par nom ou email (recherche partielle)
     */
    @Query("SELECT u FROM User u WHERE " +
           "LOWER(u.firstName) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(u.lastName) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(u.username) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(u.email) LIKE LOWER(CONCAT('%', :searchTerm, '%'))")
    Page<User> searchUsers(@Param("searchTerm") String searchTerm, Pageable pageable);
    
    /**
     * Trouver des utilisateurs par type de document d'identité
     */
    @Query("SELECT u FROM User u WHERE u.idType = :idType")
    List<User> findByIdType(@Param("idType") String idType);
    
    /**
     * Trouver des utilisateurs avec des documents d'identité expirés ou manquants
     */
    @Query("SELECT u FROM User u WHERE u.idNumber IS NULL OR u.idType IS NULL")
    List<User> findUsersWithMissingIdDocuments();
    
    /**
     * Compter les utilisateurs par statut KYC
     */
    @Query("SELECT u.kycStatus, COUNT(u) FROM User u GROUP BY u.kycStatus")
    List<Object[]> countUsersByKycStatus();
    
    /**
     * Compter les utilisateurs par statut AML
     */
    @Query("SELECT u.amlStatus, COUNT(u) FROM User u GROUP BY u.amlStatus")
    List<Object[]> countUsersByAmlStatus();
    
    /**
     * Compter les utilisateurs par nationalité
     */
    @Query("SELECT u.nationality, COUNT(u) FROM User u WHERE u.nationality IS NOT NULL GROUP BY u.nationality")
    List<Object[]> countUsersByNationality();
    
    /**
     * Trouver des utilisateurs avec des rôles spécifiques
     */
    @Query("SELECT DISTINCT u FROM User u JOIN u.userRoles ur JOIN ur.role r WHERE r.code = :roleCode")
    List<User> findUsersByRoleCode(@Param("roleCode") String roleCode);
    
    /**
     * Trouver des utilisateurs avec des permissions spécifiques
     */
    @Query("SELECT DISTINCT u FROM User u JOIN u.userRoles ur JOIN ur.role r WHERE :permission MEMBER OF r.permissions")
    List<User> findUsersByPermission(@Param("permission") String permission);
    
    /**
     * Trouver des utilisateurs qui nécessitent une vérification KYC
     */
    @Query("SELECT u FROM User u WHERE u.kycStatus IN ('NOT_VERIFIED', 'PENDING')")
    List<User> findUsersRequiringKycVerification();
    
    /**
     * Trouver des utilisateurs qui nécessitent une vérification AML
     */
    @Query("SELECT u FROM User u WHERE u.amlStatus IN ('NOT_CHECKED', 'PENDING')")
    List<User> findUsersRequiringAmlVerification();
    
    /**
     * Trouver des utilisateurs à haut risque
     */
    @Query("SELECT u FROM User u WHERE u.riskScore >= 70")
    List<User> findHighRiskUsers();
    
    /**
     * Trouver des utilisateurs inactifs depuis une certaine date
     */
    @Query("SELECT u FROM User u WHERE u.lastLoginDate < :date OR u.lastLoginDate IS NULL")
    List<User> findInactiveUsers(@Param("date") LocalDateTime date);
    
    /**
     * Trouver des utilisateurs avec des mots de passe expirés
     */
    @Query("SELECT u FROM User u WHERE u.passwordChangedDate < :date")
    List<User> findUsersWithExpiredPasswords(@Param("date") LocalDateTime date);
    
    /**
     * Trouver des utilisateurs par langue préférée
     */
    List<User> findByPreferredLanguage(String language);
    
    /**
     * Trouver des utilisateurs par fuseau horaire
     */
    List<User> findByTimezone(String timezone);
    
    /**
     * Trouver des utilisateurs créés par un utilisateur spécifique
     */
    List<User> findByCreatedBy(String createdBy);
    
    /**
     * Trouver des utilisateurs modifiés par un utilisateur spécifique
     */
    List<User> findByUpdatedBy(String updatedBy);
    
    /**
     * Trouver des utilisateurs avec des adresses dans une ville spécifique
     */
    List<User> findByCity(String city);
    
    /**
     * Trouver des utilisateurs avec des codes postaux dans une plage
     */
    @Query("SELECT u FROM User u WHERE u.postalCode LIKE :postalCodePattern")
    List<User> findByPostalCodePattern(@Param("postalCodePattern") String postalCodePattern);
    
    /**
     * Trouver des utilisateurs avec des numéros de téléphone dans un pays spécifique
     */
    @Query("SELECT u FROM User u WHERE u.phone LIKE :phonePattern")
    List<User> findByPhonePattern(@Param("phonePattern") String phonePattern);
    
    /**
     * Trouver des utilisateurs avec des dates de naissance dans une plage
     */
    @Query("SELECT u FROM User u WHERE u.dateOfBirth BETWEEN :startDate AND :endDate")
    List<User> findByDateOfBirthBetween(@Param("startDate") java.time.LocalDate startDate, 
                                       @Param("endDate") java.time.LocalDate endDate);
    
    /**
     * Trouver des utilisateurs avec des numéros d'identité spécifiques
     */
    @Query("SELECT u FROM User u WHERE u.idNumber = :idNumber")
    Optional<User> findByIdNumber(@Param("idNumber") String idNumber);
    
    /**
     * Vérifier si un numéro d'identité existe
     */
    boolean existsByIdNumber(String idNumber);
    
    /**
     * Trouver des utilisateurs avec des numéros d'identité similaires
     */
    @Query("SELECT u FROM User u WHERE u.idNumber LIKE :idNumberPattern")
    List<User> findByIdNumberPattern(@Param("idNumberPattern") String idNumberPattern);
}
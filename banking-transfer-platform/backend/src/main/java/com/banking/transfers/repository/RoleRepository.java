package com.banking.transfers.repository;

import com.banking.transfers.model.Role;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository pour l'entité Role
 */
@Repository
public interface RoleRepository extends JpaRepository<Role, UUID> {
    
    /**
     * Trouver un rôle par son code
     */
    Optional<Role> findByCode(String code);
    
    /**
     * Trouver un rôle par son nom
     */
    Optional<Role> findByName(String name);
    
    /**
     * Vérifier si un code de rôle existe
     */
    boolean existsByCode(String code);
    
    /**
     * Vérifier si un nom de rôle existe
     */
    boolean existsByName(String name);
    
    /**
     * Trouver des rôles actifs
     */
    List<Role> findByIsActiveTrue();
    
    /**
     * Trouver des rôles système
     */
    List<Role> findByIsSystemRoleTrue();
    
    /**
     * Trouver des rôles non-système
     */
    List<Role> findByIsSystemRoleFalse();
    
    /**
     * Trouver des rôles par priorité
     */
    List<Role> findByPriority(Integer priority);
    
    /**
     * Trouver des rôles avec une priorité supérieure ou égale
     */
    List<Role> findByPriorityGreaterThanEqual(Integer priority);
    
    /**
     * Trouver des rôles avec une priorité inférieure ou égale
     */
    List<Role> findByPriorityLessThanEqual(Integer priority);
    
    /**
     * Trouver des rôles par plage de priorité
     */
    List<Role> findByPriorityBetween(Integer minPriority, Integer maxPriority);
    
    /**
     * Recherche de rôles par nom ou description (recherche partielle)
     */
    @Query("SELECT r FROM Role r WHERE " +
           "LOWER(r.name) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(r.code) LIKE LOWER(CONCAT('%', :searchTerm, '%')) OR " +
           "LOWER(r.description) LIKE LOWER(CONCAT('%', :searchTerm, '%'))")
    List<Role> searchRoles(@Param("searchTerm") String searchTerm);
    
    /**
     * Trouver des rôles avec une permission spécifique
     */
    @Query("SELECT r FROM Role r WHERE :permission MEMBER OF r.permissions")
    List<Role> findByPermission(@Param("permission") String permission);
    
    /**
     * Trouver des rôles avec plusieurs permissions
     */
    @Query("SELECT r FROM Role r WHERE r.permissions IN :permissions")
    List<Role> findByPermissions(@Param("permissions") List<String> permissions);
    
    /**
     * Trouver des rôles avec toutes les permissions spécifiées
     */
    @Query("SELECT r FROM Role r WHERE :permissions MEMBER OF r.permissions")
    List<Role> findByAllPermissions(@Param("permissions") List<String> permissions);
    
    /**
     * Trouver des rôles d'administration
     */
    @Query("SELECT r FROM Role r WHERE r.code IN ('ADMIN', 'SUPER_ADMIN', 'SYSTEM_ADMIN')")
    List<Role> findAdminRoles();
    
    /**
     * Trouver des rôles utilisateur
     */
    @Query("SELECT r FROM Role r WHERE r.code IN ('USER', 'CUSTOMER', 'CLIENT')")
    List<Role> findUserRoles();
    
    /**
     * Trouver des rôles avec des permissions de transfert
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%TRANSFER%'")
    List<Role> findTransferRoles();
    
    /**
     * Trouver des rôles avec des permissions de gestion des comptes
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%ACCOUNT%'")
    List<Role> findAccountManagementRoles();
    
    /**
     * Trouver des rôles avec des permissions de KYC/AML
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%KYC%' OR r.permissions LIKE '%AML%'")
    List<Role> findKycAmlRoles();
    
    /**
     * Trouver des rôles avec des permissions d'audit
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%AUDIT%'")
    List<Role> findAuditRoles();
    
    /**
     * Trouver des rôles avec des permissions de reporting
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%REPORT%'")
    List<Role> findReportingRoles();
    
    /**
     * Trouver des rôles avec des permissions de configuration système
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%CONFIG%' OR r.permissions LIKE '%SYSTEM%'")
    List<Role> findSystemConfigRoles();
    
    /**
     * Trouver des rôles créés par un utilisateur spécifique
     */
    List<Role> findByCreatedBy(String createdBy);
    
    /**
     * Trouver des rôles modifiés par un utilisateur spécifique
     */
    List<Role> findByUpdatedBy(String updatedBy);
    
    /**
     * Trouver des rôles créés après une date
     */
    List<Role> findByCreatedAtAfter(java.time.LocalDateTime date);
    
    /**
     * Trouver des rôles modifiés après une date
     */
    List<Role> findByUpdatedAtAfter(java.time.LocalDateTime date);
    
    /**
     * Trouver des rôles par description
     */
    List<Role> findByDescriptionContainingIgnoreCase(String description);
    
    /**
     * Trouver des rôles avec un nombre minimum de permissions
     */
    @Query("SELECT r FROM Role r WHERE SIZE(r.permissions) >= :minPermissions")
    List<Role> findByMinPermissions(@Param("minPermissions") int minPermissions);
    
    /**
     * Trouver des rôles avec un nombre maximum de permissions
     */
    @Query("SELECT r FROM Role r WHERE SIZE(r.permissions) <= :maxPermissions")
    List<Role> findByMaxPermissions(@Param("maxPermissions") int maxPermissions);
    
    /**
     * Trouver des rôles avec un nombre exact de permissions
     */
    @Query("SELECT r FROM Role r WHERE SIZE(r.permissions) = :exactPermissions")
    List<Role> findByExactPermissions(@Param("exactPermissions") int exactPermissions);
    
    /**
     * Trouver des rôles avec des permissions spécifiques et actifs
     */
    @Query("SELECT r FROM Role r WHERE :permission MEMBER OF r.permissions AND r.isActive = true")
    List<Role> findActiveRolesByPermission(@Param("permission") String permission);
    
    /**
     * Trouver des rôles système avec des permissions spécifiques
     */
    @Query("SELECT r FROM Role r WHERE :permission MEMBER OF r.permissions AND r.isSystemRole = true")
    List<Role> findSystemRolesByPermission(@Param("permission") String permission);
    
    /**
     * Trouver des rôles non-système avec des permissions spécifiques
     */
    @Query("SELECT r FROM Role r WHERE :permission MEMBER OF r.permissions AND r.isSystemRole = false")
    List<Role> findNonSystemRolesByPermission(@Param("permission") String permission);
    
    /**
     * Trouver des rôles par priorité et statut actif
     */
    List<Role> findByPriorityAndIsActiveTrue(Integer priority);
    
    /**
     * Trouver des rôles par priorité et statut système
     */
    List<Role> findByPriorityAndIsSystemRoleTrue(Integer priority);
    
    /**
     * Trouver des rôles par priorité et statut non-système
     */
    List<Role> findByPriorityAndIsSystemRoleFalse(Integer priority);
    
    /**
     * Trouver des rôles avec des permissions de sécurité
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%SECURITY%' OR r.permissions LIKE '%AUTH%'")
    List<Role> findSecurityRoles();
    
    /**
     * Trouver des rôles avec des permissions de gestion des utilisateurs
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%USER%' OR r.permissions LIKE '%MANAGE%'")
    List<Role> findUserManagementRoles();
    
    /**
     * Trouver des rôles avec des permissions de monitoring
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%MONITOR%' OR r.permissions LIKE '%LOG%'")
    List<Role> findMonitoringRoles();
    
    /**
     * Trouver des rôles avec des permissions de support
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%SUPPORT%' OR r.permissions LIKE '%HELP%'")
    List<Role> findSupportRoles();
    
    /**
     * Trouver des rôles avec des permissions de développement
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%DEV%' OR r.permissions LIKE '%DEVELOP%'")
    List<Role> findDevelopmentRoles();
    
    /**
     * Trouver des rôles avec des permissions de test
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%TEST%' OR r.permissions LIKE '%DEBUG%'")
    List<Role> findTestRoles();
    
    /**
     * Trouver des rôles avec des permissions de déploiement
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%DEPLOY%' OR r.permissions LIKE '%RELEASE%'")
    List<Role> findDeploymentRoles();
    
    /**
     * Trouver des rôles avec des permissions de sauvegarde
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%BACKUP%' OR r.permissions LIKE '%RESTORE%'")
    List<Role> findBackupRoles();
    
    /**
     * Trouver des rôles avec des permissions de maintenance
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%MAINTENANCE%' OR r.permissions LIKE '%SERVICE%'")
    List<Role> findMaintenanceRoles();
    
    /**
     * Trouver des rôles avec des permissions de facturation
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%BILLING%' OR r.permissions LIKE '%INVOICE%'")
    List<Role> findBillingRoles();
    
    /**
     * Trouver des rôles avec des permissions de conformité
     */
    @Query("SELECT r FROM Role r WHERE r.permissions LIKE '%COMPLIANCE%' OR r.permissions LIKE '%REGULATORY%'")
    List<Role> findComplianceRoles();
}
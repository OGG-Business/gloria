package com.banking.transfers.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;

/**
 * Entité représentant un rôle utilisateur
 */
@Entity
@Table(name = "roles", indexes = {
    @Index(name = "idx_role_name", columnList = "name"),
    @Index(name = "idx_role_code", columnList = "code")
})
@EntityListeners(AuditingEntityListener.class)
public class Role {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    @Column(name = "name", unique = true, nullable = false, length = 100)
    @NotBlank(message = "Le nom du rôle est obligatoire")
    @Size(min = 2, max = 100, message = "Le nom du rôle doit contenir entre 2 et 100 caractères")
    private String name;
    
    @Column(name = "code", unique = true, nullable = false, length = 50)
    @NotBlank(message = "Le code du rôle est obligatoire")
    @Size(min = 2, max = 50, message = "Le code du rôle doit contenir entre 2 et 50 caractères")
    private String code;
    
    @Column(name = "description", length = 500)
    @Size(max = 500, message = "La description ne peut pas dépasser 500 caractères")
    private String description;
    
    @ElementCollection(fetch = FetchType.EAGER)
    @CollectionTable(
        name = "role_permissions",
        joinColumns = @JoinColumn(name = "role_id"),
        indexes = @Index(name = "idx_role_permissions_role_id", columnList = "role_id")
    )
    @Column(name = "permission", length = 100)
    private Set<String> permissions = new HashSet<>();
    
    @Column(name = "is_system_role", nullable = false)
    private Boolean isSystemRole = false;
    
    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;
    
    @Column(name = "priority", nullable = false)
    private Integer priority = 0;
    
    @Column(name = "created_at", nullable = false, updatable = false)
    @CreatedDate
    private LocalDateTime createdAt;
    
    @Column(name = "updated_at", nullable = false)
    @LastModifiedDate
    private LocalDateTime updatedAt;
    
    @Column(name = "created_by", length = 100)
    private String createdBy;
    
    @Column(name = "updated_by", length = 100)
    private String updatedBy;
    
    // Constructeurs
    public Role() {}
    
    public Role(String name, String code, String description) {
        this.name = name;
        this.code = code;
        this.description = description;
    }
    
    // Getters et Setters
    public UUID getId() {
        return id;
    }
    
    public void setId(UUID id) {
        this.id = id;
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public String getCode() {
        return code;
    }
    
    public void setCode(String code) {
        this.code = code;
    }
    
    public String getDescription() {
        return description;
    }
    
    public void setDescription(String description) {
        this.description = description;
    }
    
    public Set<String> getPermissions() {
        return permissions;
    }
    
    public void setPermissions(Set<String> permissions) {
        this.permissions = permissions;
    }
    
    public Boolean getIsSystemRole() {
        return isSystemRole;
    }
    
    public void setIsSystemRole(Boolean isSystemRole) {
        this.isSystemRole = isSystemRole;
    }
    
    public Boolean getIsActive() {
        return isActive;
    }
    
    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
    
    public Integer getPriority() {
        return priority;
    }
    
    public void setPriority(Integer priority) {
        this.priority = priority;
    }
    
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
    
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
    
    public String getCreatedBy() {
        return createdBy;
    }
    
    public void setCreatedBy(String createdBy) {
        this.createdBy = createdBy;
    }
    
    public String getUpdatedBy() {
        return updatedBy;
    }
    
    public void setUpdatedBy(String updatedBy) {
        this.updatedBy = updatedBy;
    }
    
    // Méthodes utilitaires
    public void addPermission(String permission) {
        this.permissions.add(permission);
    }
    
    public void removePermission(String permission) {
        this.permissions.remove(permission);
    }
    
    public boolean hasPermission(String permission) {
        return this.permissions.contains(permission);
    }
    
    public boolean hasAnyPermission(Set<String> permissions) {
        return this.permissions.stream().anyMatch(permissions::contains);
    }
    
    public boolean hasAllPermissions(Set<String> permissions) {
        return this.permissions.containsAll(permissions);
    }
    
    public boolean isAdminRole() {
        return "ADMIN".equals(this.code) || "SUPER_ADMIN".equals(this.code);
    }
    
    public boolean isUserRole() {
        return "USER".equals(this.code) || "CUSTOMER".equals(this.code);
    }
    
    public boolean isSystemRole() {
        return this.isSystemRole;
    }
    
    public boolean canBeDeleted() {
        return !this.isSystemRole;
    }
    
    public boolean canBeModified() {
        return !this.isSystemRole || "ADMIN".equals(this.code);
    }
    
    @Override
    public String toString() {
        return "Role{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", code='" + code + '\'' +
                ", description='" + description + '\'' +
                ", permissions=" + permissions +
                ", isActive=" + isActive +
                '}';
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Role role = (Role) o;
        return id != null && id.equals(role.getId());
    }
    
    @Override
    public int hashCode() {
        return id != null ? id.hashCode() : 0;
    }
}
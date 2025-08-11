package com.banking.transfers.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entité représentant un utilisateur du système
 */
@Entity
@Table(name = "users", indexes = {
    @Index(name = "idx_user_username", columnList = "username"),
    @Index(name = "idx_user_email", columnList = "email"),
    @Index(name = "idx_user_kyc_status", columnList = "kyc_status"),
    @Index(name = "idx_user_aml_status", columnList = "aml_status"),
    @Index(name = "idx_user_created_at", columnList = "created_at")
})
@EntityListeners(AuditingEntityListener.class)
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;
    
    @Column(name = "username", unique = true, nullable = false, length = 50)
    @NotBlank(message = "Le nom d'utilisateur est obligatoire")
    @Pattern(regexp = "^[a-zA-Z0-9_]{3,50}$", message = "Le nom d'utilisateur doit contenir entre 3 et 50 caractères alphanumériques et underscores")
    private String username;
    
    @Column(name = "email", unique = true, nullable = false, length = 100)
    @NotBlank(message = "L'email est obligatoire")
    @Email(message = "Format d'email invalide")
    private String email;
    
    @Column(name = "password_hash", nullable = false)
    @NotBlank(message = "Le mot de passe est obligatoire")
    private String passwordHash;
    
    @Column(name = "first_name", nullable = false, length = 50)
    @NotBlank(message = "Le prénom est obligatoire")
    @Size(min = 2, max = 50, message = "Le prénom doit contenir entre 2 et 50 caractères")
    private String firstName;
    
    @Column(name = "last_name", nullable = false, length = 50)
    @NotBlank(message = "Le nom de famille est obligatoire")
    @Size(min = 2, max = 50, message = "Le nom de famille doit contenir entre 2 et 50 caractères")
    private String lastName;
    
    @Column(name = "phone", length = 20)
    @Pattern(regexp = "^\\+?[0-9\\s\\-\\(\\)]{7,20}$", message = "Format de téléphone invalide")
    private String phone;
    
    @Column(name = "date_of_birth")
    @Past(message = "La date de naissance doit être dans le passé")
    private LocalDate dateOfBirth;
    
    @Column(name = "nationality", length = 2)
    @Pattern(regexp = "^[A-Z]{2}$", message = "Le code de nationalité doit être un code pays ISO 3166-1 alpha-2")
    private String nationality;
    
    @Column(name = "id_number", length = 50)
    private String idNumber;
    
    @Column(name = "id_type", length = 20)
    @Enumerated(EnumType.STRING)
    private IdType idType;
    
    @Column(name = "address", length = 500)
    @Size(max = 500, message = "L'adresse ne peut pas dépasser 500 caractères")
    private String address;
    
    @Column(name = "city", length = 100)
    @Size(max = 100, message = "La ville ne peut pas dépasser 100 caractères")
    private String city;
    
    @Column(name = "country", length = 2)
    @Pattern(regexp = "^[A-Z]{2}$", message = "Le code pays doit être un code ISO 3166-1 alpha-2")
    private String country;
    
    @Column(name = "postal_code", length = 20)
    private String postalCode;
    
    @Column(name = "kyc_status", nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    private KYCStatus kycStatus = KYCStatus.NOT_VERIFIED;
    
    @Column(name = "aml_status", nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    private AMLStatus amlStatus = AMLStatus.NOT_CHECKED;
    
    @Column(name = "risk_score", nullable = false)
    @Min(value = 0, message = "Le score de risque ne peut pas être négatif")
    @Max(value = 100, message = "Le score de risque ne peut pas dépasser 100")
    private Integer riskScore = 0;
    
    @Column(name = "is_active", nullable = false)
    private Boolean isActive = true;
    
    @Column(name = "is_locked", nullable = false)
    private Boolean isLocked = false;
    
    @Column(name = "failed_login_attempts", nullable = false)
    @Min(value = 0, message = "Le nombre de tentatives de connexion échouées ne peut pas être négatif")
    private Integer failedLoginAttempts = 0;
    
    @Column(name = "last_login_date")
    private LocalDateTime lastLoginDate;
    
    @Column(name = "password_changed_date")
    private LocalDateTime passwordChangedDate;
    
    @Column(name = "mfa_enabled", nullable = false)
    private Boolean mfaEnabled = false;
    
    @Column(name = "mfa_secret", length = 100)
    private String mfaSecret;
    
    @Column(name = "preferred_language", length = 5)
    @Pattern(regexp = "^[a-z]{2}(-[A-Z]{2})?$", message = "Format de langue invalide (ex: fr, en-US)")
    private String preferredLanguage = "fr";
    
    @Column(name = "timezone", length = 50)
    private String timezone = "Africa/Kinshasa";
    
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
    public User() {}
    
    public User(String username, String email, String passwordHash, String firstName, String lastName) {
        this.username = username;
        this.email = email;
        this.passwordHash = passwordHash;
        this.firstName = firstName;
        this.lastName = lastName;
    }
    
    // Getters et Setters
    public UUID getId() {
        return id;
    }
    
    public void setId(UUID id) {
        this.id = id;
    }
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public String getPasswordHash() {
        return passwordHash;
    }
    
    public void setPasswordHash(String passwordHash) {
        this.passwordHash = passwordHash;
    }
    
    public String getFirstName() {
        return firstName;
    }
    
    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }
    
    public String getLastName() {
        return lastName;
    }
    
    public void setLastName(String lastName) {
        this.lastName = lastName;
    }
    
    public String getPhone() {
        return phone;
    }
    
    public void setPhone(String phone) {
        this.phone = phone;
    }
    
    public LocalDate getDateOfBirth() {
        return dateOfBirth;
    }
    
    public void setDateOfBirth(LocalDate dateOfBirth) {
        this.dateOfBirth = dateOfBirth;
    }
    
    public String getNationality() {
        return nationality;
    }
    
    public void setNationality(String nationality) {
        this.nationality = nationality;
    }
    
    public String getIdNumber() {
        return idNumber;
    }
    
    public void setIdNumber(String idNumber) {
        this.idNumber = idNumber;
    }
    
    public IdType getIdType() {
        return idType;
    }
    
    public void setIdType(IdType idType) {
        this.idType = idType;
    }
    
    public String getAddress() {
        return address;
    }
    
    public void setAddress(String address) {
        this.address = address;
    }
    
    public String getCity() {
        return city;
    }
    
    public void setCity(String city) {
        this.city = city;
    }
    
    public String getCountry() {
        return country;
    }
    
    public void setCountry(String country) {
        this.country = country;
    }
    
    public String getPostalCode() {
        return postalCode;
    }
    
    public void setPostalCode(String postalCode) {
        this.postalCode = postalCode;
    }
    
    public KYCStatus getKycStatus() {
        return kycStatus;
    }
    
    public void setKycStatus(KYCStatus kycStatus) {
        this.kycStatus = kycStatus;
    }
    
    public AMLStatus getAmlStatus() {
        return amlStatus;
    }
    
    public void setAmlStatus(AMLStatus amlStatus) {
        this.amlStatus = amlStatus;
    }
    
    public Integer getRiskScore() {
        return riskScore;
    }
    
    public void setRiskScore(Integer riskScore) {
        this.riskScore = riskScore;
    }
    
    public Boolean getIsActive() {
        return isActive;
    }
    
    public void setIsActive(Boolean isActive) {
        this.isActive = isActive;
    }
    
    public Boolean getIsLocked() {
        return isLocked;
    }
    
    public void setIsLocked(Boolean isLocked) {
        this.isLocked = isLocked;
    }
    
    public Integer getFailedLoginAttempts() {
        return failedLoginAttempts;
    }
    
    public void setFailedLoginAttempts(Integer failedLoginAttempts) {
        this.failedLoginAttempts = failedLoginAttempts;
    }
    
    public LocalDateTime getLastLoginDate() {
        return lastLoginDate;
    }
    
    public void setLastLoginDate(LocalDateTime lastLoginDate) {
        this.lastLoginDate = lastLoginDate;
    }
    
    public LocalDateTime getPasswordChangedDate() {
        return passwordChangedDate;
    }
    
    public void setPasswordChangedDate(LocalDateTime passwordChangedDate) {
        this.passwordChangedDate = passwordChangedDate;
    }
    
    public Boolean getMfaEnabled() {
        return mfaEnabled;
    }
    
    public void setMfaEnabled(Boolean mfaEnabled) {
        this.mfaEnabled = mfaEnabled;
    }
    
    public String getMfaSecret() {
        return mfaSecret;
    }
    
    public void setMfaSecret(String mfaSecret) {
        this.mfaSecret = mfaSecret;
    }
    
    public String getPreferredLanguage() {
        return preferredLanguage;
    }
    
    public void setPreferredLanguage(String preferredLanguage) {
        this.preferredLanguage = preferredLanguage;
    }
    
    public String getTimezone() {
        return timezone;
    }
    
    public void setTimezone(String timezone) {
        this.timezone = timezone;
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
    public String getFullName() {
        return firstName + " " + lastName;
    }
    
    public boolean isAccountLocked() {
        return isLocked || !isActive;
    }
    
    public boolean canLogin() {
        return isActive && !isLocked && kycStatus.isValid() && amlStatus.isValid();
    }
    
    public void incrementFailedLoginAttempts() {
        this.failedLoginAttempts++;
        if (this.failedLoginAttempts >= 5) {
            this.isLocked = true;
        }
    }
    
    public void resetFailedLoginAttempts() {
        this.failedLoginAttempts = 0;
        this.isLocked = false;
    }
    
    public void updateLastLogin() {
        this.lastLoginDate = LocalDateTime.now();
        this.failedLoginAttempts = 0;
    }
    
    public boolean isHighRisk() {
        return riskScore >= 70;
    }
    
    public boolean requiresKYCVerification() {
        return kycStatus == KYCStatus.NOT_VERIFIED || kycStatus == KYCStatus.PENDING;
    }
    
    public boolean requiresAMLVerification() {
        return amlStatus == AMLStatus.NOT_CHECKED || amlStatus == AMLStatus.PENDING;
    }
    
    @Override
    public String toString() {
        return "User{" +
                "id=" + id +
                ", username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", firstName='" + firstName + '\'' +
                ", lastName='" + lastName + '\'' +
                ", kycStatus=" + kycStatus +
                ", amlStatus=" + amlStatus +
                ", isActive=" + isActive +
                ", isLocked=" + isLocked +
                '}';
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User user = (User) o;
        return id != null && id.equals(user.getId());
    }
    
    @Override
    public int hashCode() {
        return id != null ? id.hashCode() : 0;
    }
}
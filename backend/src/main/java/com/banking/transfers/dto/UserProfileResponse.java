package com.banking.transfers.dto;

import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.IdType;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.RiskLevel;
import com.banking.transfers.model.SourceOfFunds;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public class UserProfileResponse {

    private UUID userId;
    private String username;
    private String email;
    private String firstName;
    private String lastName;
    private String fullName;
    private String phone;
    private LocalDate dateOfBirth;
    private String nationality;
    private String country;
    private String address;
    private String city;
    private String postalCode;

    // Informations d'identité
    private IdType idType;
    private String idNumber;
    private LocalDate idExpiryDate;

    // Informations professionnelles
    private String occupation;
    private String employer;
    private Double annualIncome;
    private SourceOfFunds sourceOfFunds;
    private String sourceOfFundsDetails;

    // Statuts de conformité
    private KYCStatus kycStatus;
    private AMLStatus amlStatus;
    private RiskLevel riskLevel;
    private Integer riskScore;
    private String kycRejectionReason;
    private String amlRejectionReason;

    // Informations de sécurité
    private Boolean mfaEnabled;
    private String mfaType;
    private Boolean emailVerified;
    private Boolean phoneVerified;
    private LocalDateTime emailVerifiedAt;
    private LocalDateTime phoneVerifiedAt;

    // Statut du compte
    private Boolean isActive;
    private Boolean isLocked;
    private Integer failedLoginAttempts;
    private LocalDateTime lastLoginDate;
    private LocalDateTime passwordChangedAt;
    private LocalDateTime accountLockedAt;
    private String lockReason;

    // Informations de session
    private String currentSessionId;
    private LocalDateTime sessionExpiresAt;
    private Integer activeSessionsCount;

    // Préférences
    private String preferredLanguage;
    private String preferredCurrency;
    private Boolean marketingConsent;
    private Boolean notificationsEnabled;
    private List<String> notificationPreferences;

    // Limites et restrictions
    private Double dailyTransferLimit;
    private Double monthlyTransferLimit;
    private Double singleTransferLimit;
    private List<String> restrictedCountries;
    private List<String> restrictedCurrencies;

    // Informations d'audit
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    private String createdBy;
    private String updatedBy;

    // Actions requises
    private List<String> requiredActions;
    private List<String> warnings;
    private List<String> recommendations;

    // Constructeurs
    public UserProfileResponse() {}

    public UserProfileResponse(UUID userId, String username, String email, String firstName, String lastName) {
        this.userId = userId;
        this.username = username;
        this.email = email;
        this.firstName = firstName;
        this.lastName = lastName;
        this.fullName = firstName + " " + lastName;
    }

    // Getters et Setters
    public UUID getUserId() { return userId; }
    public void setUserId(UUID userId) { this.userId = userId; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public String getFullName() { return fullName; }
    public void setFullName(String fullName) { this.fullName = fullName; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public LocalDate getDateOfBirth() { return dateOfBirth; }
    public void setDateOfBirth(LocalDate dateOfBirth) { this.dateOfBirth = dateOfBirth; }

    public String getNationality() { return nationality; }
    public void setNationality(String nationality) { this.nationality = nationality; }

    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }

    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public String getPostalCode() { return postalCode; }
    public void setPostalCode(String postalCode) { this.postalCode = postalCode; }

    public IdType getIdType() { return idType; }
    public void setIdType(IdType idType) { this.idType = idType; }

    public String getIdNumber() { return idNumber; }
    public void setIdNumber(String idNumber) { this.idNumber = idNumber; }

    public LocalDate getIdExpiryDate() { return idExpiryDate; }
    public void setIdExpiryDate(LocalDate idExpiryDate) { this.idExpiryDate = idExpiryDate; }

    public String getOccupation() { return occupation; }
    public void setOccupation(String occupation) { this.occupation = occupation; }

    public String getEmployer() { return employer; }
    public void setEmployer(String employer) { this.employer = employer; }

    public Double getAnnualIncome() { return annualIncome; }
    public void setAnnualIncome(Double annualIncome) { this.annualIncome = annualIncome; }

    public SourceOfFunds getSourceOfFunds() { return sourceOfFunds; }
    public void setSourceOfFunds(SourceOfFunds sourceOfFunds) { this.sourceOfFunds = sourceOfFunds; }

    public String getSourceOfFundsDetails() { return sourceOfFundsDetails; }
    public void setSourceOfFundsDetails(String sourceOfFundsDetails) { this.sourceOfFundsDetails = sourceOfFundsDetails; }

    public KYCStatus getKycStatus() { return kycStatus; }
    public void setKycStatus(KYCStatus kycStatus) { this.kycStatus = kycStatus; }

    public AMLStatus getAmlStatus() { return amlStatus; }
    public void setAmlStatus(AMLStatus amlStatus) { this.amlStatus = amlStatus; }

    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }

    public Integer getRiskScore() { return riskScore; }
    public void setRiskScore(Integer riskScore) { this.riskScore = riskScore; }

    public String getKycRejectionReason() { return kycRejectionReason; }
    public void setKycRejectionReason(String kycRejectionReason) { this.kycRejectionReason = kycRejectionReason; }

    public String getAmlRejectionReason() { return amlRejectionReason; }
    public void setAmlRejectionReason(String amlRejectionReason) { this.amlRejectionReason = amlRejectionReason; }

    public Boolean getMfaEnabled() { return mfaEnabled; }
    public void setMfaEnabled(Boolean mfaEnabled) { this.mfaEnabled = mfaEnabled; }

    public String getMfaType() { return mfaType; }
    public void setMfaType(String mfaType) { this.mfaType = mfaType; }

    public Boolean getEmailVerified() { return emailVerified; }
    public void setEmailVerified(Boolean emailVerified) { this.emailVerified = emailVerified; }

    public Boolean getPhoneVerified() { return phoneVerified; }
    public void setPhoneVerified(Boolean phoneVerified) { this.phoneVerified = phoneVerified; }

    public LocalDateTime getEmailVerifiedAt() { return emailVerifiedAt; }
    public void setEmailVerifiedAt(LocalDateTime emailVerifiedAt) { this.emailVerifiedAt = emailVerifiedAt; }

    public LocalDateTime getPhoneVerifiedAt() { return phoneVerifiedAt; }
    public void setPhoneVerifiedAt(LocalDateTime phoneVerifiedAt) { this.phoneVerifiedAt = phoneVerifiedAt; }

    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }

    public Boolean getIsLocked() { return isLocked; }
    public void setIsLocked(Boolean isLocked) { this.isLocked = isLocked; }

    public Integer getFailedLoginAttempts() { return failedLoginAttempts; }
    public void setFailedLoginAttempts(Integer failedLoginAttempts) { this.failedLoginAttempts = failedLoginAttempts; }

    public LocalDateTime getLastLoginDate() { return lastLoginDate; }
    public void setLastLoginDate(LocalDateTime lastLoginDate) { this.lastLoginDate = lastLoginDate; }

    public LocalDateTime getPasswordChangedAt() { return passwordChangedAt; }
    public void setPasswordChangedAt(LocalDateTime passwordChangedAt) { this.passwordChangedAt = passwordChangedAt; }

    public LocalDateTime getAccountLockedAt() { return accountLockedAt; }
    public void setAccountLockedAt(LocalDateTime accountLockedAt) { this.accountLockedAt = accountLockedAt; }

    public String getLockReason() { return lockReason; }
    public void setLockReason(String lockReason) { this.lockReason = lockReason; }

    public String getCurrentSessionId() { return currentSessionId; }
    public void setCurrentSessionId(String currentSessionId) { this.currentSessionId = currentSessionId; }

    public LocalDateTime getSessionExpiresAt() { return sessionExpiresAt; }
    public void setSessionExpiresAt(LocalDateTime sessionExpiresAt) { this.sessionExpiresAt = sessionExpiresAt; }

    public Integer getActiveSessionsCount() { return activeSessionsCount; }
    public void setActiveSessionsCount(Integer activeSessionsCount) { this.activeSessionsCount = activeSessionsCount; }

    public String getPreferredLanguage() { return preferredLanguage; }
    public void setPreferredLanguage(String preferredLanguage) { this.preferredLanguage = preferredLanguage; }

    public String getPreferredCurrency() { return preferredCurrency; }
    public void setPreferredCurrency(String preferredCurrency) { this.preferredCurrency = preferredCurrency; }

    public Boolean getMarketingConsent() { return marketingConsent; }
    public void setMarketingConsent(Boolean marketingConsent) { this.marketingConsent = marketingConsent; }

    public Boolean getNotificationsEnabled() { return notificationsEnabled; }
    public void setNotificationsEnabled(Boolean notificationsEnabled) { this.notificationsEnabled = notificationsEnabled; }

    public List<String> getNotificationPreferences() { return notificationPreferences; }
    public void setNotificationPreferences(List<String> notificationPreferences) { this.notificationPreferences = notificationPreferences; }

    public Double getDailyTransferLimit() { return dailyTransferLimit; }
    public void setDailyTransferLimit(Double dailyTransferLimit) { this.dailyTransferLimit = dailyTransferLimit; }

    public Double getMonthlyTransferLimit() { return monthlyTransferLimit; }
    public void setMonthlyTransferLimit(Double monthlyTransferLimit) { this.monthlyTransferLimit = monthlyTransferLimit; }

    public Double getSingleTransferLimit() { return singleTransferLimit; }
    public void setSingleTransferLimit(Double singleTransferLimit) { this.singleTransferLimit = singleTransferLimit; }

    public List<String> getRestrictedCountries() { return restrictedCountries; }
    public void setRestrictedCountries(List<String> restrictedCountries) { this.restrictedCountries = restrictedCountries; }

    public List<String> getRestrictedCurrencies() { return restrictedCurrencies; }
    public void setRestrictedCurrencies(List<String> restrictedCurrencies) { this.restrictedCurrencies = restrictedCurrencies; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }

    public String getUpdatedBy() { return updatedBy; }
    public void setUpdatedBy(String updatedBy) { this.updatedBy = updatedBy; }

    public List<String> getRequiredActions() { return requiredActions; }
    public void setRequiredActions(List<String> requiredActions) { this.requiredActions = requiredActions; }

    public List<String> getWarnings() { return warnings; }
    public void setWarnings(List<String> warnings) { this.warnings = warnings; }

    public List<String> getRecommendations() { return recommendations; }
    public void setRecommendations(List<String> recommendations) { this.recommendations = recommendations; }

    // Méthodes utilitaires
    public boolean isProfileComplete() {
        return firstName != null && lastName != null && email != null && phone != null &&
               dateOfBirth != null && nationality != null && country != null &&
               address != null && city != null && postalCode != null &&
               idType != null && idNumber != null && occupation != null &&
               annualIncome != null && sourceOfFunds != null;
    }

    public boolean isVerified() {
        return emailVerified != null && emailVerified && 
               phoneVerified != null && phoneVerified &&
               kycStatus == KYCStatus.VERIFIED && 
               amlStatus == AMLStatus.PASSED;
    }

    public boolean canPerformTransactions() {
        return isActive != null && isActive && 
               isLocked != null && !isLocked && 
               isVerified();
    }

    public boolean isHighRisk() {
        return riskLevel == RiskLevel.HIGH || riskLevel == RiskLevel.CRITICAL;
    }

    public boolean isIdExpired() {
        return idExpiryDate != null && idExpiryDate.isBefore(LocalDate.now());
    }

    public boolean isIdExpiringSoon() {
        if (idExpiryDate == null) return false;
        LocalDate threeMonthsFromNow = LocalDate.now().plusMonths(3);
        return idExpiryDate.isBefore(threeMonthsFromNow);
    }

    public int getAge() {
        if (dateOfBirth == null) return 0;
        return LocalDate.now().getYear() - dateOfBirth.getYear();
    }

    public boolean isAdult() {
        return getAge() >= 18;
    }

    @Override
    public String toString() {
        return "UserProfileResponse{" +
                "userId=" + userId +
                ", username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", fullName='" + fullName + '\'' +
                ", kycStatus=" + kycStatus +
                ", amlStatus=" + amlStatus +
                ", riskLevel=" + riskLevel +
                ", isActive=" + isActive +
                ", isLocked=" + isLocked +
                ", isVerified=" + isVerified() +
                '}';
    }
}
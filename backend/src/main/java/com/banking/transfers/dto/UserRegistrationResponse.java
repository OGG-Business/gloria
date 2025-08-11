package com.banking.transfers.dto;

import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.RiskLevel;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

public class UserRegistrationResponse {

    private boolean success;
    private String message;
    private String errorCode;

    // Informations utilisateur
    private UUID userId;
    private String username;
    private String email;
    private String firstName;
    private String lastName;
    private String fullName;
    private String phone;
    private String nationality;
    private String country;

    // Statuts de conformité
    private KYCStatus kycStatus;
    private AMLStatus amlStatus;
    private RiskLevel riskLevel;
    private Integer riskScore;

    // Informations de sécurité
    private Boolean mfaEnabled;
    private Boolean mfaRequired;
    private String mfaSecret;
    private String mfaQrCode;
    private List<String> backupCodes;

    // Informations de session
    private String accessToken;
    private String refreshToken;
    private String tokenType;
    private Long expiresIn;
    private LocalDateTime expiresAt;

    // Informations de vérification
    private Boolean emailVerified;
    private Boolean phoneVerified;
    private LocalDateTime emailVerificationExpiresAt;
    private LocalDateTime phoneVerificationExpiresAt;

    // Actions requises
    private List<String> requiredActions;
    private List<String> warnings;
    private List<String> nextSteps;

    // Informations de compte
    private Boolean isActive;
    private Boolean isLocked;
    private LocalDateTime createdAt;
    private LocalDateTime lastLoginDate;

    // Constructeurs
    public UserRegistrationResponse() {}

    public UserRegistrationResponse(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    public UserRegistrationResponse(boolean success, String message, UUID userId, String username) {
        this.success = success;
        this.message = message;
        this.userId = userId;
        this.username = username;
    }

    // Getters et Setters
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }

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

    public String getNationality() { return nationality; }
    public void setNationality(String nationality) { this.nationality = nationality; }

    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }

    public KYCStatus getKycStatus() { return kycStatus; }
    public void setKycStatus(KYCStatus kycStatus) { this.kycStatus = kycStatus; }

    public AMLStatus getAmlStatus() { return amlStatus; }
    public void setAmlStatus(AMLStatus amlStatus) { this.amlStatus = amlStatus; }

    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }

    public Integer getRiskScore() { return riskScore; }
    public void setRiskScore(Integer riskScore) { this.riskScore = riskScore; }

    public Boolean getMfaEnabled() { return mfaEnabled; }
    public void setMfaEnabled(Boolean mfaEnabled) { this.mfaEnabled = mfaEnabled; }

    public Boolean getMfaRequired() { return mfaRequired; }
    public void setMfaRequired(Boolean mfaRequired) { this.mfaRequired = mfaRequired; }

    public String getMfaSecret() { return mfaSecret; }
    public void setMfaSecret(String mfaSecret) { this.mfaSecret = mfaSecret; }

    public String getMfaQrCode() { return mfaQrCode; }
    public void setMfaQrCode(String mfaQrCode) { this.mfaQrCode = mfaQrCode; }

    public List<String> getBackupCodes() { return backupCodes; }
    public void setBackupCodes(List<String> backupCodes) { this.backupCodes = backupCodes; }

    public String getAccessToken() { return accessToken; }
    public void setAccessToken(String accessToken) { this.accessToken = accessToken; }

    public String getRefreshToken() { return refreshToken; }
    public void setRefreshToken(String refreshToken) { this.refreshToken = refreshToken; }

    public String getTokenType() { return tokenType; }
    public void setTokenType(String tokenType) { this.tokenType = tokenType; }

    public Long getExpiresIn() { return expiresIn; }
    public void setExpiresIn(Long expiresIn) { this.expiresIn = expiresIn; }

    public LocalDateTime getExpiresAt() { return expiresAt; }
    public void setExpiresAt(LocalDateTime expiresAt) { this.expiresAt = expiresAt; }

    public Boolean getEmailVerified() { return emailVerified; }
    public void setEmailVerified(Boolean emailVerified) { this.emailVerified = emailVerified; }

    public Boolean getPhoneVerified() { return phoneVerified; }
    public void setPhoneVerified(Boolean phoneVerified) { this.phoneVerified = phoneVerified; }

    public LocalDateTime getEmailVerificationExpiresAt() { return emailVerificationExpiresAt; }
    public void setEmailVerificationExpiresAt(LocalDateTime emailVerificationExpiresAt) { this.emailVerificationExpiresAt = emailVerificationExpiresAt; }

    public LocalDateTime getPhoneVerificationExpiresAt() { return phoneVerificationExpiresAt; }
    public void setPhoneVerificationExpiresAt(LocalDateTime phoneVerificationExpiresAt) { this.phoneVerificationExpiresAt = phoneVerificationExpiresAt; }

    public List<String> getRequiredActions() { return requiredActions; }
    public void setRequiredActions(List<String> requiredActions) { this.requiredActions = requiredActions; }

    public List<String> getWarnings() { return warnings; }
    public void setWarnings(List<String> warnings) { this.warnings = warnings; }

    public List<String> getNextSteps() { return nextSteps; }
    public void setNextSteps(List<String> nextSteps) { this.nextSteps = nextSteps; }

    public Boolean getIsActive() { return isActive; }
    public void setIsActive(Boolean isActive) { this.isActive = isActive; }

    public Boolean getIsLocked() { return isLocked; }
    public void setIsLocked(Boolean isLocked) { this.isLocked = isLocked; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getLastLoginDate() { return lastLoginDate; }
    public void setLastLoginDate(LocalDateTime lastLoginDate) { this.lastLoginDate = lastLoginDate; }

    // Méthodes utilitaires
    public boolean requiresEmailVerification() {
        return emailVerified != null && !emailVerified;
    }

    public boolean requiresPhoneVerification() {
        return phoneVerified != null && !phoneVerified;
    }

    public boolean requiresMfaSetup() {
        return mfaRequired != null && mfaRequired && (mfaEnabled == null || !mfaEnabled);
    }

    public boolean requiresKycVerification() {
        return kycStatus == KYCStatus.PENDING || kycStatus == KYCStatus.REJECTED;
    }

    public boolean isHighRisk() {
        return riskLevel == RiskLevel.HIGH || riskLevel == RiskLevel.CRITICAL;
    }

    public boolean canPerformTransactions() {
        return isActive != null && isActive && 
               isLocked != null && !isLocked && 
               kycStatus == KYCStatus.VERIFIED && 
               amlStatus == AMLStatus.PASSED;
    }

    public static UserRegistrationResponse success(UUID userId, String username, String message) {
        UserRegistrationResponse response = new UserRegistrationResponse(true, message, userId, username);
        response.setIsActive(true);
        response.setIsLocked(false);
        response.setCreatedAt(LocalDateTime.now());
        return response;
    }

    public static UserRegistrationResponse error(String message, String errorCode) {
        UserRegistrationResponse response = new UserRegistrationResponse(false, message);
        response.setErrorCode(errorCode);
        return response;
    }

    @Override
    public String toString() {
        return "UserRegistrationResponse{" +
                "success=" + success +
                ", message='" + message + '\'' +
                ", userId=" + userId +
                ", username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", kycStatus=" + kycStatus +
                ", amlStatus=" + amlStatus +
                ", riskLevel=" + riskLevel +
                ", isActive=" + isActive +
                ", isLocked=" + isLocked +
                '}';
    }
}
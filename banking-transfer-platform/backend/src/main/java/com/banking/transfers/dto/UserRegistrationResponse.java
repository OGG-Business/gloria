package com.banking.transfers.dto;

import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.RiskLevel;
import java.time.LocalDateTime;
import java.util.List;

/**
 * DTO pour les réponses d'inscription d'utilisateur
 */
public class UserRegistrationResponse {

    private boolean success;
    private String message;
    private String userId;
    private String username;
    private String email;
    private String firstName;
    private String lastName;
    private KYCStatus kycStatus;
    private AMLStatus amlStatus;
    private RiskLevel riskLevel;
    private String mfaSecret;
    private String mfaQrCode;
    private List<String> backupCodes;
    private String accessToken;
    private String refreshToken;
    private LocalDateTime tokenExpiresAt;
    private boolean requiresKycVerification;
    private boolean requiresDocumentUpload;
    private List<String> requiredActions;
    private String accountStatus;

    // Constructeurs
    public UserRegistrationResponse() {}

    public UserRegistrationResponse(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    // Getters et Setters
    public boolean isSuccess() { return success; }
    public void setSuccess(boolean success) { this.success = success; }

    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }

    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public KYCStatus getKycStatus() { return kycStatus; }
    public void setKycStatus(KYCStatus kycStatus) { this.kycStatus = kycStatus; }

    public AMLStatus getAmlStatus() { return amlStatus; }
    public void setAmlStatus(AMLStatus amlStatus) { this.amlStatus = amlStatus; }

    public RiskLevel getRiskLevel() { return riskLevel; }
    public void setRiskLevel(RiskLevel riskLevel) { this.riskLevel = riskLevel; }

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

    public LocalDateTime getTokenExpiresAt() { return tokenExpiresAt; }
    public void setTokenExpiresAt(LocalDateTime tokenExpiresAt) { this.tokenExpiresAt = tokenExpiresAt; }

    public boolean isRequiresKycVerification() { return requiresKycVerification; }
    public void setRequiresKycVerification(boolean requiresKycVerification) { this.requiresKycVerification = requiresKycVerification; }

    public boolean isRequiresDocumentUpload() { return requiresDocumentUpload; }
    public void setRequiresDocumentUpload(boolean requiresDocumentUpload) { this.requiresDocumentUpload = requiresDocumentUpload; }

    public List<String> getRequiredActions() { return requiredActions; }
    public void setRequiredActions(List<String> requiredActions) { this.requiredActions = requiredActions; }

    public String getAccountStatus() { return accountStatus; }
    public void setAccountStatus(String accountStatus) { this.accountStatus = accountStatus; }
}
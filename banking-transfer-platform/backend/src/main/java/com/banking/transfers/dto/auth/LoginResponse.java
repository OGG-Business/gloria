package com.banking.transfers.dto.auth;

import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.AMLStatus;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * DTO pour les réponses de connexion
 */
public class LoginResponse {

    private UUID userId;
    private String username;
    private String email;
    private String firstName;
    private String lastName;
    private String fullName;
    private String accessToken;
    private String refreshToken;
    private String tokenType = "Bearer";
    private Long expiresIn;
    private LocalDateTime expiresAt;
    private KYCStatus kycStatus;
    private AMLStatus amlStatus;
    private Integer riskScore;
    private Boolean mfaEnabled;
    private Boolean mfaRequired;
    private String preferredLanguage;
    private String timezone;
    private Boolean isFirstLogin;
    private String sessionId;
    private LocalDateTime lastLoginDate;
    private String message;

    // Constructeurs
    public LoginResponse() {}

    public LoginResponse(UUID userId, String username, String email, String firstName, String lastName) {
        this.userId = userId;
        this.username = username;
        this.email = email;
        this.firstName = firstName;
        this.lastName = lastName;
        this.fullName = firstName + " " + lastName;
    }

    // Getters et Setters
    public UUID getUserId() {
        return userId;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
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

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getAccessToken() {
        return accessToken;
    }

    public void setAccessToken(String accessToken) {
        this.accessToken = accessToken;
    }

    public String getRefreshToken() {
        return refreshToken;
    }

    public void setRefreshToken(String refreshToken) {
        this.refreshToken = refreshToken;
    }

    public String getTokenType() {
        return tokenType;
    }

    public void setTokenType(String tokenType) {
        this.tokenType = tokenType;
    }

    public Long getExpiresIn() {
        return expiresIn;
    }

    public void setExpiresIn(Long expiresIn) {
        this.expiresIn = expiresIn;
    }

    public LocalDateTime getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(LocalDateTime expiresAt) {
        this.expiresAt = expiresAt;
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

    public Boolean getMfaEnabled() {
        return mfaEnabled;
    }

    public void setMfaEnabled(Boolean mfaEnabled) {
        this.mfaEnabled = mfaEnabled;
    }

    public Boolean getMfaRequired() {
        return mfaRequired;
    }

    public void setMfaRequired(Boolean mfaRequired) {
        this.mfaRequired = mfaRequired;
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

    public Boolean getIsFirstLogin() {
        return isFirstLogin;
    }

    public void setIsFirstLogin(Boolean isFirstLogin) {
        this.isFirstLogin = isFirstLogin;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public LocalDateTime getLastLoginDate() {
        return lastLoginDate;
    }

    public void setLastLoginDate(LocalDateTime lastLoginDate) {
        this.lastLoginDate = lastLoginDate;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    // Méthodes utilitaires
    public boolean isKycVerified() {
        return kycStatus == KYCStatus.VERIFIED;
    }

    public boolean isAmlPassed() {
        return amlStatus == AMLStatus.PASSED;
    }

    public boolean isCompliant() {
        return isKycVerified() && isAmlPassed();
    }

    public boolean isHighRisk() {
        return riskScore != null && riskScore >= 70;
    }

    public boolean requiresMfaSetup() {
        return mfaEnabled != null && mfaEnabled && mfaRequired != null && mfaRequired;
    }

    public boolean isTokenValid() {
        return accessToken != null && !accessToken.trim().isEmpty() && 
               expiresAt != null && expiresAt.isAfter(LocalDateTime.now());
    }

    public boolean hasRefreshToken() {
        return refreshToken != null && !refreshToken.trim().isEmpty();
    }

    public String getTokenHeader() {
        return tokenType + " " + accessToken;
    }

    @Override
    public String toString() {
        return "LoginResponse{" +
                "userId=" + userId +
                ", username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", fullName='" + fullName + '\'' +
                ", accessToken='" + (accessToken != null ? "***" : "null") + '\'' +
                ", refreshToken='" + (refreshToken != null ? "***" : "null") + '\'' +
                ", expiresIn=" + expiresIn +
                ", expiresAt=" + expiresAt +
                ", kycStatus=" + kycStatus +
                ", amlStatus=" + amlStatus +
                ", riskScore=" + riskScore +
                ", mfaEnabled=" + mfaEnabled +
                ", mfaRequired=" + mfaRequired +
                ", sessionId='" + sessionId + '\'' +
                ", message='" + message + '\'' +
                '}';
    }
}
package com.banking.transfers.dto.auth;

import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.KYCStatus;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

/**
 * DTO pour la réponse de connexion
 */
public class LoginResponse {

    private String accessToken;
    private String refreshToken;
    private String tokenType = "Bearer";
    private Long expiresIn; // en secondes
    private LocalDateTime expiresAt;
    private String scope;

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
    private Integer riskScore;
    private Boolean isActive;
    private Boolean isLocked;
    private Boolean mfaEnabled;
    private Boolean mfaRequired;

    // Rôles et permissions
    private List<String> roles;
    private List<String> permissions;

    // Informations de session
    private String sessionId;
    private LocalDateTime loginTime;
    private String deviceId;
    private String userAgent;
    private String ipAddress;

    // Messages et avertissements
    private String message;
    private List<String> warnings;
    private List<String> requiredActions;

    // Constructeurs
    public LoginResponse() {}

    public LoginResponse(String accessToken, String refreshToken, Long expiresIn) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        this.expiresIn = expiresIn;
        this.expiresAt = LocalDateTime.now().plusSeconds(expiresIn);
    }

    // Getters et Setters
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
        if (expiresIn != null) {
            this.expiresAt = LocalDateTime.now().plusSeconds(expiresIn);
        }
    }

    public LocalDateTime getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(LocalDateTime expiresAt) {
        this.expiresAt = expiresAt;
    }

    public String getScope() {
        return scope;
    }

    public void setScope(String scope) {
        this.scope = scope;
    }

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

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getNationality() {
        return nationality;
    }

    public void setNationality(String nationality) {
        this.nationality = nationality;
    }

    public String getCountry() {
        return country;
    }

    public void setCountry(String country) {
        this.country = country;
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

    public List<String> getRoles() {
        return roles;
    }

    public void setRoles(List<String> roles) {
        this.roles = roles;
    }

    public List<String> getPermissions() {
        return permissions;
    }

    public void setPermissions(List<String> permissions) {
        this.permissions = permissions;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public LocalDateTime getLoginTime() {
        return loginTime;
    }

    public void setLoginTime(LocalDateTime loginTime) {
        this.loginTime = loginTime;
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public String getUserAgent() {
        return userAgent;
    }

    public void setUserAgent(String userAgent) {
        this.userAgent = userAgent;
    }

    public String getIpAddress() {
        return ipAddress;
    }

    public void setIpAddress(String ipAddress) {
        this.ipAddress = ipAddress;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public List<String> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }

    public List<String> getRequiredActions() {
        return requiredActions;
    }

    public void setRequiredActions(List<String> requiredActions) {
        this.requiredActions = requiredActions;
    }

    // Méthodes utilitaires
    public boolean isTokenExpired() {
        return expiresAt != null && LocalDateTime.now().isAfter(expiresAt);
    }

    public boolean hasRole(String role) {
        return roles != null && roles.contains(role);
    }

    public boolean hasPermission(String permission) {
        return permissions != null && permissions.contains(permission);
    }

    public boolean requiresKYCVerification() {
        return kycStatus == KYCStatus.NOT_VERIFIED || kycStatus == KYCStatus.PENDING;
    }

    public boolean requiresAMLVerification() {
        return amlStatus == AMLStatus.NOT_CHECKED || amlStatus == AMLStatus.PENDING;
    }

    public boolean isHighRisk() {
        return riskScore != null && riskScore >= 70;
    }

    public boolean isAccountLocked() {
        return isLocked != null && isLocked;
    }

    public boolean isAccountActive() {
        return isActive != null && isActive;
    }

    @Override
    public String toString() {
        return "LoginResponse{" +
                "userId=" + userId +
                ", username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", fullName='" + fullName + '\'' +
                ", kycStatus=" + kycStatus +
                ", amlStatus=" + amlStatus +
                ", riskScore=" + riskScore +
                ", isActive=" + isActive +
                ", isLocked=" + isLocked +
                ", mfaEnabled=" + mfaEnabled +
                ", mfaRequired=" + mfaRequired +
                ", roles=" + roles +
                ", sessionId='" + sessionId + '\'' +
                ", loginTime=" + loginTime +
                ", expiresAt=" + expiresAt +
                ", message='" + message + '\'' +
                '}';
    }
}
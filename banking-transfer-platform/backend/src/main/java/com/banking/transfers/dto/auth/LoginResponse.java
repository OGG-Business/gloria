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
    
    private Long expiresIn;
    
    private Long refreshExpiresIn;
    
    private String scope;
    
    private UUID userId;
    
    private String username;
    
    private String email;
    
    private String firstName;
    
    private String lastName;
    
    private String fullName;
    
    private List<String> roles;
    
    private List<String> permissions;
    
    private KYCStatus kycStatus;
    
    private AMLStatus amlStatus;
    
    private Integer riskScore;
    
    private Boolean mfaEnabled;
    
    private Boolean mfaRequired;
    
    private String mfaType;
    
    private String preferredLanguage;
    
    private String timezone;
    
    private LocalDateTime lastLoginDate;
    
    private LocalDateTime tokenIssuedAt;
    
    private LocalDateTime tokenExpiresAt;
    
    private String sessionId;
    
    private String clientId;
    
    private String redirectUri;
    
    private String state;
    
    private String nonce;
    
    private String codeVerifier;
    
    private String authorizationCode;
    
    private String idToken;
    
    private String error;
    
    private String errorDescription;
    
    private String errorUri;
    
    // Constructeurs
    public LoginResponse() {}
    
    public LoginResponse(String accessToken, String refreshToken, UUID userId, String username) {
        this.accessToken = accessToken;
        this.refreshToken = refreshToken;
        this.userId = userId;
        this.username = username;
        this.tokenIssuedAt = LocalDateTime.now();
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
    }
    
    public Long getRefreshExpiresIn() {
        return refreshExpiresIn;
    }
    
    public void setRefreshExpiresIn(Long refreshExpiresIn) {
        this.refreshExpiresIn = refreshExpiresIn;
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
    
    public String getMfaType() {
        return mfaType;
    }
    
    public void setMfaType(String mfaType) {
        this.mfaType = mfaType;
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
    
    public LocalDateTime getLastLoginDate() {
        return lastLoginDate;
    }
    
    public void setLastLoginDate(LocalDateTime lastLoginDate) {
        this.lastLoginDate = lastLoginDate;
    }
    
    public LocalDateTime getTokenIssuedAt() {
        return tokenIssuedAt;
    }
    
    public void setTokenIssuedAt(LocalDateTime tokenIssuedAt) {
        this.tokenIssuedAt = tokenIssuedAt;
    }
    
    public LocalDateTime getTokenExpiresAt() {
        return tokenExpiresAt;
    }
    
    public void setTokenExpiresAt(LocalDateTime tokenExpiresAt) {
        this.tokenExpiresAt = tokenExpiresAt;
    }
    
    public String getSessionId() {
        return sessionId;
    }
    
    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }
    
    public String getClientId() {
        return clientId;
    }
    
    public void setClientId(String clientId) {
        this.clientId = clientId;
    }
    
    public String getRedirectUri() {
        return redirectUri;
    }
    
    public void setRedirectUri(String redirectUri) {
        this.redirectUri = redirectUri;
    }
    
    public String getState() {
        return state;
    }
    
    public void setState(String state) {
        this.state = state;
    }
    
    public String getNonce() {
        return nonce;
    }
    
    public void setNonce(String nonce) {
        this.nonce = nonce;
    }
    
    public String getCodeVerifier() {
        return codeVerifier;
    }
    
    public void setCodeVerifier(String codeVerifier) {
        this.codeVerifier = codeVerifier;
    }
    
    public String getAuthorizationCode() {
        return authorizationCode;
    }
    
    public void setAuthorizationCode(String authorizationCode) {
        this.authorizationCode = authorizationCode;
    }
    
    public String getIdToken() {
        return idToken;
    }
    
    public void setIdToken(String idToken) {
        this.idToken = idToken;
    }
    
    public String getError() {
        return error;
    }
    
    public void setError(String error) {
        this.error = error;
    }
    
    public String getErrorDescription() {
        return errorDescription;
    }
    
    public void setErrorDescription(String errorDescription) {
        this.errorDescription = errorDescription;
    }
    
    public String getErrorUri() {
        return errorUri;
    }
    
    public void setErrorUri(String errorUri) {
        this.errorUri = errorUri;
    }
    
    // Méthodes utilitaires
    public boolean isSuccess() {
        return error == null && accessToken != null;
    }
    
    public boolean isError() {
        return error != null;
    }
    
    public boolean isMfaRequired() {
        return mfaRequired != null && mfaRequired;
    }
    
    public boolean isOAuth2Response() {
        return clientId != null && authorizationCode != null;
    }
    
    public boolean isOpenIDConnectResponse() {
        return idToken != null;
    }
    
    public boolean hasRole(String role) {
        return roles != null && roles.contains(role);
    }
    
    public boolean hasPermission(String permission) {
        return permissions != null && permissions.contains(permission);
    }
    
    public boolean hasAnyRole(List<String> requiredRoles) {
        return roles != null && roles.stream().anyMatch(requiredRoles::contains);
    }
    
    public boolean hasAnyPermission(List<String> requiredPermissions) {
        return permissions != null && permissions.stream().anyMatch(requiredPermissions::contains);
    }
    
    public boolean hasAllRoles(List<String> requiredRoles) {
        return roles != null && roles.containsAll(requiredRoles);
    }
    
    public boolean hasAllPermissions(List<String> requiredPermissions) {
        return permissions != null && permissions.containsAll(requiredPermissions);
    }
    
    public boolean isKycVerified() {
        return kycStatus != null && kycStatus.isValid();
    }
    
    public boolean isAmlVerified() {
        return amlStatus != null && amlStatus.isValid();
    }
    
    public boolean isHighRisk() {
        return riskScore != null && riskScore >= 70;
    }
    
    public boolean isTokenExpired() {
        return tokenExpiresAt != null && LocalDateTime.now().isAfter(tokenExpiresAt);
    }
    
    public long getTokenExpiresInSeconds() {
        if (tokenExpiresAt == null) {
            return -1;
        }
        return java.time.Duration.between(LocalDateTime.now(), tokenExpiresAt).getSeconds();
    }
    
    public void calculateExpiresIn() {
        if (tokenExpiresAt != null) {
            this.expiresIn = java.time.Duration.between(LocalDateTime.now(), tokenExpiresAt).getSeconds();
        }
    }
    
    public void setFullNameFromParts() {
        if (firstName != null && lastName != null) {
            this.fullName = firstName + " " + lastName;
        } else if (firstName != null) {
            this.fullName = firstName;
        } else if (lastName != null) {
            this.fullName = lastName;
        }
    }
    
    @Override
    public String toString() {
        return "LoginResponse{" +
                "userId=" + userId +
                ", username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", fullName='" + fullName + '\'' +
                ", roles=" + roles +
                ", kycStatus=" + kycStatus +
                ", amlStatus=" + amlStatus +
                ", mfaRequired=" + mfaRequired +
                ", isSuccess=" + isSuccess() +
                ", isError=" + isError() +
                ", error='" + error + '\'' +
                '}';
    }
}
package com.banking.transfers.dto.auth;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * DTO pour la requête de connexion
 */
public class LoginRequest {
    
    @NotBlank(message = "Le nom d'utilisateur ou l'email est obligatoire")
    @Size(min = 3, max = 100, message = "Le nom d'utilisateur ou l'email doit contenir entre 3 et 100 caractères")
    private String usernameOrEmail;
    
    @NotBlank(message = "Le mot de passe est obligatoire")
    @Size(min = 8, max = 128, message = "Le mot de passe doit contenir entre 8 et 128 caractères")
    private String password;
    
    private String mfaCode;
    
    private Boolean rememberMe = false;
    
    private String clientId;
    
    private String clientSecret;
    
    private String grantType = "password";
    
    private String scope = "read write";
    
    private String redirectUri;
    
    private String state;
    
    private String nonce;
    
    private String codeChallenge;
    
    private String codeChallengeMethod;
    
    // Constructeurs
    public LoginRequest() {}
    
    public LoginRequest(String usernameOrEmail, String password) {
        this.usernameOrEmail = usernameOrEmail;
        this.password = password;
    }
    
    public LoginRequest(String usernameOrEmail, String password, String mfaCode) {
        this.usernameOrEmail = usernameOrEmail;
        this.password = password;
        this.mfaCode = mfaCode;
    }
    
    // Getters et Setters
    public String getUsernameOrEmail() {
        return usernameOrEmail;
    }
    
    public void setUsernameOrEmail(String usernameOrEmail) {
        this.usernameOrEmail = usernameOrEmail;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    public String getMfaCode() {
        return mfaCode;
    }
    
    public void setMfaCode(String mfaCode) {
        this.mfaCode = mfaCode;
    }
    
    public Boolean getRememberMe() {
        return rememberMe;
    }
    
    public void setRememberMe(Boolean rememberMe) {
        this.rememberMe = rememberMe;
    }
    
    public String getClientId() {
        return clientId;
    }
    
    public void setClientId(String clientId) {
        this.clientId = clientId;
    }
    
    public String getClientSecret() {
        return clientSecret;
    }
    
    public void setClientSecret(String clientSecret) {
        this.clientSecret = clientSecret;
    }
    
    public String getGrantType() {
        return grantType;
    }
    
    public void setGrantType(String grantType) {
        this.grantType = grantType;
    }
    
    public String getScope() {
        return scope;
    }
    
    public void setScope(String scope) {
        this.scope = scope;
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
    
    public String getCodeChallenge() {
        return codeChallenge;
    }
    
    public void setCodeChallenge(String codeChallenge) {
        this.codeChallenge = codeChallenge;
    }
    
    public String getCodeChallengeMethod() {
        return codeChallengeMethod;
    }
    
    public void setCodeChallengeMethod(String codeChallengeMethod) {
        this.codeChallengeMethod = codeChallengeMethod;
    }
    
    // Méthodes utilitaires
    public boolean isMfaRequired() {
        return mfaCode != null && !mfaCode.trim().isEmpty();
    }
    
    public boolean isOAuth2Request() {
        return clientId != null && !clientId.trim().isEmpty();
    }
    
    public boolean isPKCERequest() {
        return codeChallenge != null && !codeChallenge.trim().isEmpty();
    }
    
    public boolean isEmailLogin() {
        return usernameOrEmail != null && usernameOrEmail.contains("@");
    }
    
    public boolean isUsernameLogin() {
        return usernameOrEmail != null && !usernameOrEmail.contains("@");
    }
    
    @Override
    public String toString() {
        return "LoginRequest{" +
                "usernameOrEmail='" + usernameOrEmail + '\'' +
                ", mfaCode='" + (mfaCode != null ? "***" : "null") + '\'' +
                ", rememberMe=" + rememberMe +
                ", clientId='" + clientId + '\'' +
                ", grantType='" + grantType + '\'' +
                ", scope='" + scope + '\'' +
                ", isOAuth2Request=" + isOAuth2Request() +
                ", isMfaRequired=" + isMfaRequired() +
                '}';
    }
}
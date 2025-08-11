package com.banking.transfers.dto.auth;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * DTO pour les demandes de connexion
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

    private String clientIp;

    private String userAgent;

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

    public String getClientIp() {
        return clientIp;
    }

    public void setClientIp(String clientIp) {
        this.clientIp = clientIp;
    }

    public String getUserAgent() {
        return userAgent;
    }

    public void setUserAgent(String userAgent) {
        this.userAgent = userAgent;
    }

    // Méthodes utilitaires
    public boolean isMfaRequired() {
        return mfaCode != null && !mfaCode.trim().isEmpty();
    }

    public boolean isRememberMeEnabled() {
        return rememberMe != null && rememberMe;
    }

    public String getUsernameOrEmailTrimmed() {
        return usernameOrEmail != null ? usernameOrEmail.trim() : null;
    }

    public String getPasswordTrimmed() {
        return password != null ? password.trim() : null;
    }

    public String getMfaCodeTrimmed() {
        return mfaCode != null ? mfaCode.trim() : null;
    }

    @Override
    public String toString() {
        return "LoginRequest{" +
                "usernameOrEmail='" + usernameOrEmail + '\'' +
                ", mfaCode='" + (mfaCode != null ? "***" : "null") + '\'' +
                ", rememberMe=" + rememberMe +
                ", clientIp='" + clientIp + '\'' +
                ", userAgent='" + userAgent + '\'' +
                '}';
    }
}
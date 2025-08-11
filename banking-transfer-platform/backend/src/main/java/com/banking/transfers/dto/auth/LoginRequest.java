package com.banking.transfers.dto.auth;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/**
 * DTO pour la requête de connexion
 */
public class LoginRequest {

    @NotBlank(message = "L'identifiant (nom d'utilisateur ou email) est obligatoire")
    @Size(min = 3, max = 100, message = "L'identifiant doit contenir entre 3 et 100 caractères")
    private String identifier; // username ou email

    @NotBlank(message = "Le mot de passe est obligatoire")
    @Size(min = 8, max = 128, message = "Le mot de passe doit contenir entre 8 et 128 caractères")
    private String password;

    private String mfaCode; // Code MFA si activé

    private String deviceId; // Identifiant de l'appareil pour la sécurité

    private String userAgent; // User-Agent du navigateur

    private String ipAddress; // Adresse IP du client

    private Boolean rememberMe = false; // Se souvenir de l'utilisateur

    // Constructeurs
    public LoginRequest() {}

    public LoginRequest(String identifier, String password) {
        this.identifier = identifier;
        this.password = password;
    }

    public LoginRequest(String identifier, String password, String mfaCode) {
        this.identifier = identifier;
        this.password = password;
        this.mfaCode = mfaCode;
    }

    // Getters et Setters
    public String getIdentifier() {
        return identifier;
    }

    public void setIdentifier(String identifier) {
        this.identifier = identifier;
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

    public Boolean getRememberMe() {
        return rememberMe;
    }

    public void setRememberMe(Boolean rememberMe) {
        this.rememberMe = rememberMe;
    }

    // Méthodes utilitaires
    public boolean isMfaRequired() {
        return mfaCode != null && !mfaCode.trim().isEmpty();
    }

    public boolean isRememberMeEnabled() {
        return rememberMe != null && rememberMe;
    }

    @Override
    public String toString() {
        return "LoginRequest{" +
                "identifier='" + identifier + '\'' +
                ", mfaCode='" + (mfaCode != null ? "***" : "null") + '\'' +
                ", deviceId='" + deviceId + '\'' +
                ", userAgent='" + userAgent + '\'' +
                ", ipAddress='" + ipAddress + '\'' +
                ", rememberMe=" + rememberMe +
                '}';
    }
}
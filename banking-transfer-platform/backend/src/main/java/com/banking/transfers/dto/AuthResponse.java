package com.banking.transfers.dto;

import java.time.LocalDateTime;

/**
 * DTO pour les réponses d'authentification
 */
public class AuthResponse {

    private String token;
    private String username;
    private String fullName;
    private boolean mfaEnabled;
    private LocalDateTime expiresAt;
    private String sessionId;
    private String message;

    // Constructeurs
    public AuthResponse() {}

    public AuthResponse(String token, String username, String fullName, boolean mfaEnabled) {
        this.token = token;
        this.username = username;
        this.fullName = fullName;
        this.mfaEnabled = mfaEnabled;
        this.message = "Authentification réussie";
    }

    // Getters et Setters
    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public boolean isMfaEnabled() {
        return mfaEnabled;
    }

    public void setMfaEnabled(boolean mfaEnabled) {
        this.mfaEnabled = mfaEnabled;
    }

    public LocalDateTime getExpiresAt() {
        return expiresAt;
    }

    public void setExpiresAt(LocalDateTime expiresAt) {
        this.expiresAt = expiresAt;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    @Override
    public String toString() {
        return "AuthResponse{" +
                "token='" + (token != null ? "***" : "null") + '\'' +
                ", username='" + username + '\'' +
                ", fullName='" + fullName + '\'' +
                ", mfaEnabled=" + mfaEnabled +
                ", expiresAt=" + expiresAt +
                ", sessionId='" + sessionId + '\'' +
                ", message='" + message + '\'' +
                '}';
    }
}
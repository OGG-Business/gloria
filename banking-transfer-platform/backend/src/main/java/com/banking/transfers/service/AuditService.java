package com.banking.transfers.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Service d'audit pour enregistrer les actions importantes
 */
@Service
@Transactional
public class AuditService {

    /**
     * Enregistre une connexion réussie
     */
    public void logLoginSuccess(UUID userId, String clientIp, String userAgent) {
        logAction("LOGIN_SUCCESS", userId, "Connexion réussie", clientIp, userAgent, null);
    }

    /**
     * Enregistre un échec de connexion
     */
    public void logLoginFailed(String username, String reason, String clientIp, String userAgent) {
        logAction("LOGIN_FAILED", null, "Échec de connexion: " + reason, clientIp, userAgent, username);
    }

    /**
     * Enregistre une déconnexion
     */
    public void logLogout(UUID userId, String clientIp) {
        logAction("LOGOUT", userId, "Déconnexion", clientIp, null, null);
    }

    /**
     * Enregistre un rafraîchissement de token
     */
    public void logTokenRefresh(UUID userId, String clientIp) {
        logAction("TOKEN_REFRESH", userId, "Rafraîchissement de token", clientIp, null, null);
    }

    /**
     * Enregistre un changement de mot de passe
     */
    public void logPasswordChange(UUID userId, String clientIp) {
        logAction("PASSWORD_CHANGE", userId, "Changement de mot de passe", clientIp, null, null);
    }

    /**
     * Enregistre l'activation de MFA
     */
    public void logMfaEnable(UUID userId, String clientIp) {
        logAction("MFA_ENABLE", userId, "Activation MFA", clientIp, null, null);
    }

    /**
     * Enregistre la désactivation de MFA
     */
    public void logMfaDisable(UUID userId, String clientIp) {
        logAction("MFA_DISABLE", userId, "Désactivation MFA", clientIp, null, null);
    }

    /**
     * Enregistre une erreur
     */
    public void logError(String action, String message, String clientIp) {
        logAction("ERROR", null, action + ": " + message, clientIp, null, null);
    }

    /**
     * Méthode générique pour enregistrer une action
     */
    private void logAction(String action, UUID userId, String description, String clientIp, String userAgent, String details) {
        // En production, sauvegarder dans la base de données
        System.out.println(String.format("[AUDIT] %s - User: %s - Action: %s - IP: %s - %s", 
            LocalDateTime.now(), userId, action, clientIp, description));
    }
}
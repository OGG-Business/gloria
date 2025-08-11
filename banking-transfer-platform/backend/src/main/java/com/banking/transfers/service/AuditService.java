package com.banking.transfers.service;

import com.banking.transfers.model.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Service d'audit pour tracer les actions d'authentification et de sécurité
 */
@Service
public class AuditService {

    private static final Logger logger = LoggerFactory.getLogger(AuditService.class);

    /**
     * Trace une tentative de connexion
     */
    public void logLogin(User user, String clientIp, String userAgent, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("AUTH_SUCCESS - User: {} (ID: {}) logged in successfully from IP: {} with User-Agent: {}", 
                username, userId, clientIp, userAgent);
        } else {
            logger.warn("AUTH_FAILURE - Failed login attempt for user: {} from IP: {} with User-Agent: {}. Error: {}", 
                username, clientIp, userAgent, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données pour un audit complet
        // saveAuditLog("LOGIN", user, clientIp, userAgent, success, errorMessage);
    }

    /**
     * Trace une déconnexion
     */
    public void logLogout(User user, String clientIp, String userAgent, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("AUTH_LOGOUT - User: {} (ID: {}) logged out from IP: {} with User-Agent: {}", 
                username, userId, clientIp, userAgent);
        } else {
            logger.warn("AUTH_LOGOUT_ERROR - Error during logout for user: {} from IP: {}. Error: {}", 
                username, clientIp, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("LOGOUT", user, clientIp, userAgent, success, errorMessage);
    }

    /**
     * Trace un échec de connexion
     */
    public void logFailedLogin(User user, String reason) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        logger.warn("AUTH_FAILED_LOGIN - User: {} (ID: {}) failed login attempt. Reason: {}", 
            username, userId, reason);
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("FAILED_LOGIN", user, null, null, false, reason);
    }

    /**
     * Trace un rafraîchissement de token
     */
    public void logTokenRefresh(User user, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("TOKEN_REFRESH - User: {} (ID: {}) refreshed their access token", username, userId);
        } else {
            logger.warn("TOKEN_REFRESH_ERROR - Failed token refresh for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("TOKEN_REFRESH", user, null, null, success, errorMessage);
    }

    /**
     * Trace un changement de mot de passe
     */
    public void logPasswordChange(User user, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("PASSWORD_CHANGE - User: {} (ID: {}) changed their password", username, userId);
        } else {
            logger.warn("PASSWORD_CHANGE_ERROR - Failed password change for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("PASSWORD_CHANGE", user, null, null, success, errorMessage);
    }

    /**
     * Trace une demande de réinitialisation de mot de passe
     */
    public void logPasswordResetRequest(User user, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("PASSWORD_RESET_REQUEST - User: {} (ID: {}) requested password reset", username, userId);
        } else {
            logger.warn("PASSWORD_RESET_REQUEST_ERROR - Failed password reset request for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("PASSWORD_RESET_REQUEST", user, null, null, success, errorMessage);
    }

    /**
     * Trace une réinitialisation de mot de passe
     */
    public void logPasswordReset(User user, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("PASSWORD_RESET - User: {} (ID: {}) reset their password", username, userId);
        } else {
            logger.warn("PASSWORD_RESET_ERROR - Failed password reset for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("PASSWORD_RESET", user, null, null, success, errorMessage);
    }

    /**
     * Trace une activation/désactivation de MFA
     */
    public void logMfaToggle(User user, boolean enabled, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("MFA_TOGGLE - User: {} (ID: {}) {} MFA", username, userId, enabled ? "enabled" : "disabled");
        } else {
            logger.warn("MFA_TOGGLE_ERROR - Failed to {} MFA for user: {}. Error: {}", 
                enabled ? "enable" : "disable", username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("MFA_TOGGLE", user, null, null, success, errorMessage);
    }

    /**
     * Trace une vérification MFA
     */
    public void logMfaVerification(User user, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("MFA_VERIFICATION - User: {} (ID: {}) successfully verified MFA code", username, userId);
        } else {
            logger.warn("MFA_VERIFICATION_ERROR - Failed MFA verification for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("MFA_VERIFICATION", user, null, null, success, errorMessage);
    }

    /**
     * Trace un verrouillage de compte
     */
    public void logAccountLock(User user, String reason) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        logger.warn("ACCOUNT_LOCK - User: {} (ID: {}) account locked. Reason: {}", 
            username, userId, reason);
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("ACCOUNT_LOCK", user, null, null, false, reason);
    }

    /**
     * Trace un déverrouillage de compte
     */
    public void logAccountUnlock(User user, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("ACCOUNT_UNLOCK - User: {} (ID: {}) account unlocked", username, userId);
        } else {
            logger.warn("ACCOUNT_UNLOCK_ERROR - Failed to unlock account for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("ACCOUNT_UNLOCK", user, null, null, success, errorMessage);
    }

    /**
     * Trace un changement de statut de compte
     */
    public void logAccountStatusChange(User user, boolean active, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("ACCOUNT_STATUS_CHANGE - User: {} (ID: {}) account status changed to {}", 
                username, userId, active ? "ACTIVE" : "INACTIVE");
        } else {
            logger.warn("ACCOUNT_STATUS_CHANGE_ERROR - Failed to change account status for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("ACCOUNT_STATUS_CHANGE", user, null, null, success, errorMessage);
    }

    /**
     * Trace une tentative d'accès non autorisé
     */
    public void logUnauthorizedAccess(String resource, String clientIp, String userAgent, String reason) {
        logger.warn("UNAUTHORIZED_ACCESS - Unauthorized access attempt to resource: {} from IP: {} with User-Agent: {}. Reason: {}", 
            resource, clientIp, userAgent, reason);
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("UNAUTHORIZED_ACCESS", null, clientIp, userAgent, false, reason);
    }

    /**
     * Trace une tentative d'accès à une ressource interdite
     */
    public void logForbiddenAccess(String resource, String clientIp, String userAgent, String reason) {
        logger.warn("FORBIDDEN_ACCESS - Forbidden access attempt to resource: {} from IP: {} with User-Agent: {}. Reason: {}", 
            resource, clientIp, userAgent, reason);
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("FORBIDDEN_ACCESS", null, clientIp, userAgent, false, reason);
    }

    /**
     * Trace une erreur de sécurité
     */
    public void logSecurityError(String operation, String clientIp, String userAgent, String errorMessage) {
        logger.error("SECURITY_ERROR - Security error during operation: {} from IP: {} with User-Agent: {}. Error: {}", 
            operation, clientIp, userAgent, errorMessage);
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("SECURITY_ERROR", null, clientIp, userAgent, false, errorMessage);
    }

    /**
     * Trace une activité suspecte
     */
    public void logSuspiciousActivity(User user, String activity, String clientIp, String userAgent, String details) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        logger.warn("SUSPICIOUS_ACTIVITY - User: {} (ID: {}) suspicious activity detected: {} from IP: {} with User-Agent: {}. Details: {}", 
            username, userId, activity, clientIp, userAgent, details);
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("SUSPICIOUS_ACTIVITY", user, clientIp, userAgent, false, details);
    }

    /**
     * Trace une modification de profil utilisateur
     */
    public void logProfileUpdate(User user, String field, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("PROFILE_UPDATE - User: {} (ID: {}) updated field: {}", username, userId, field);
        } else {
            logger.warn("PROFILE_UPDATE_ERROR - Failed to update field: {} for user: {}. Error: {}", 
                field, username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("PROFILE_UPDATE", user, null, null, success, errorMessage);
    }

    /**
     * Trace une création de compte
     */
    public void logAccountCreation(User user, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("ACCOUNT_CREATION - New user account created: {} (ID: {})", username, userId);
        } else {
            logger.warn("ACCOUNT_CREATION_ERROR - Failed to create account for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("ACCOUNT_CREATION", user, null, null, success, errorMessage);
    }

    /**
     * Trace une suppression de compte
     */
    public void logAccountDeletion(User user, boolean success, String errorMessage) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        if (success) {
            logger.info("ACCOUNT_DELETION - User account deleted: {} (ID: {})", username, userId);
        } else {
            logger.warn("ACCOUNT_DELETION_ERROR - Failed to delete account for user: {}. Error: {}", 
                username, errorMessage);
        }
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("ACCOUNT_DELETION", user, null, null, success, errorMessage);
    }

    /**
     * Trace une session expirée
     */
    public void logSessionExpired(User user, String sessionId) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        logger.info("SESSION_EXPIRED - Session expired for user: {} (ID: {}) with session ID: {}", 
            username, userId, sessionId);
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("SESSION_EXPIRED", user, null, null, true, "Session ID: " + sessionId);
    }

    /**
     * Trace une session invalidée
     */
    public void logSessionInvalidated(User user, String sessionId, String reason) {
        String username = user != null ? user.getUsername() : "UNKNOWN";
        String userId = user != null ? user.getId().toString() : "UNKNOWN";
        
        logger.warn("SESSION_INVALIDATED - Session invalidated for user: {} (ID: {}) with session ID: {}. Reason: {}", 
            username, userId, sessionId, reason);
        
        // TODO: Sauvegarder dans la base de données
        // saveAuditLog("SESSION_INVALIDATED", user, null, null, false, reason);
    }

    /**
     * Méthode générique pour sauvegarder un log d'audit dans la base de données
     * Cette méthode sera implémentée plus tard avec l'entité AuditLog
     */
    private void saveAuditLog(String action, User user, String clientIp, String userAgent, 
                             boolean success, String details) {
        // TODO: Implémenter la sauvegarde dans la base de données
        // AuditLog auditLog = new AuditLog();
        // auditLog.setAction(action);
        // auditLog.setUserId(user != null ? user.getId() : null);
        // auditLog.setUsername(user != null ? user.getUsername() : "UNKNOWN");
        // auditLog.setClientIp(clientIp);
        // auditLog.setUserAgent(userAgent);
        // auditLog.setSuccess(success);
        // auditLog.setDetails(details);
        // auditLog.setTimestamp(LocalDateTime.now());
        // auditLogRepository.save(auditLog);
    }
}
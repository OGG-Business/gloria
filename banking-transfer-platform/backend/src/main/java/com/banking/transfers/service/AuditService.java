package com.banking.transfers.service;

import com.banking.transfers.model.User;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Service d'audit pour la journalisation des événements de sécurité
 */
@Service
public class AuditService {

    private static final Logger logger = LoggerFactory.getLogger(AuditService.class);
    private static final Logger auditLogger = LoggerFactory.getLogger("AUDIT");

    /**
     * Journalise une tentative de connexion
     */
    public void logLogin(User user, String ipAddress, String userAgent, boolean success, String errorMessage) {
        String eventType = success ? "LOGIN_SUCCESS" : "LOGIN_FAILED";
        String message = String.format(
            "Event: %s | User: %s | IP: %s | UserAgent: %s | Success: %s | Error: %s",
            eventType,
            user != null ? user.getUsername() : "UNKNOWN",
            ipAddress != null ? ipAddress : "UNKNOWN",
            userAgent != null ? userAgent : "UNKNOWN",
            success,
            errorMessage != null ? errorMessage : "N/A"
        );

        if (success) {
            auditLogger.info(message);
        } else {
            auditLogger.warn(message);
        }

        // Log détaillé pour le debugging
        logger.debug("Login attempt - User: {}, IP: {}, Success: {}, Error: {}", 
            user != null ? user.getUsername() : "UNKNOWN", 
            ipAddress, 
            success, 
            errorMessage);
    }

    /**
     * Journalise une déconnexion
     */
    public void logLogout(User user, String ipAddress, boolean success, String errorMessage) {
        String eventType = success ? "LOGOUT_SUCCESS" : "LOGOUT_FAILED";
        String message = String.format(
            "Event: %s | User: %s | IP: %s | Success: %s | Error: %s",
            eventType,
            user != null ? user.getUsername() : "UNKNOWN",
            ipAddress != null ? ipAddress : "UNKNOWN",
            success,
            errorMessage != null ? errorMessage : "N/A"
        );

        auditLogger.info(message);
        logger.debug("Logout attempt - User: {}, IP: {}, Success: {}", 
            user != null ? user.getUsername() : "UNKNOWN", 
            ipAddress, 
            success);
    }

    /**
     * Journalise un changement de mot de passe
     */
    public void logPasswordChange(User user, boolean success, String errorMessage) {
        String eventType = success ? "PASSWORD_CHANGE_SUCCESS" : "PASSWORD_CHANGE_FAILED";
        String message = String.format(
            "Event: %s | User: %s | Success: %s | Error: %s",
            eventType,
            user.getUsername(),
            success,
            errorMessage != null ? errorMessage : "N/A"
        );

        auditLogger.info(message);
        logger.debug("Password change - User: {}, Success: {}", user.getUsername(), success);
    }

    /**
     * Journalise un changement de statut MFA
     */
    public void logMfaToggle(User user, boolean enabled, boolean success, String errorMessage) {
        String eventType = success ? "MFA_TOGGLE_SUCCESS" : "MFA_TOGGLE_FAILED";
        String action = enabled ? "ENABLED" : "DISABLED";
        String message = String.format(
            "Event: %s | User: %s | Action: %s | Success: %s | Error: %s",
            eventType,
            user.getUsername(),
            action,
            success,
            errorMessage != null ? errorMessage : "N/A"
        );

        auditLogger.info(message);
        logger.debug("MFA toggle - User: {}, Action: {}, Success: {}", 
            user.getUsername(), action, success);
    }

    /**
     * Journalise un déverrouillage de compte
     */
    public void logAccountUnlock(User user, boolean success, String errorMessage) {
        String eventType = success ? "ACCOUNT_UNLOCK_SUCCESS" : "ACCOUNT_UNLOCK_FAILED";
        String message = String.format(
            "Event: %s | User: %s | Success: %s | Error: %s",
            eventType,
            user.getUsername(),
            success,
            errorMessage != null ? errorMessage : "N/A"
        );

        auditLogger.info(message);
        logger.debug("Account unlock - User: {}, Success: {}", user.getUsername(), success);
    }

    /**
     * Journalise un changement de statut de compte
     */
    public void logAccountStatusChange(User user, boolean active, boolean success, String errorMessage) {
        String eventType = success ? "ACCOUNT_STATUS_CHANGE_SUCCESS" : "ACCOUNT_STATUS_CHANGE_FAILED";
        String action = active ? "ACTIVATED" : "DEACTIVATED";
        String message = String.format(
            "Event: %s | User: %s | Action: %s | Success: %s | Error: %s",
            eventType,
            user.getUsername(),
            action,
            success,
            errorMessage != null ? errorMessage : "N/A"
        );

        auditLogger.info(message);
        logger.debug("Account status change - User: {}, Action: {}, Success: {}", 
            user.getUsername(), action, success);
    }

    /**
     * Journalise une création d'utilisateur
     */
    public void logUserCreation(User user) {
        String message = String.format(
            "Event: USER_CREATED | User: %s | Email: %s | CreatedBy: %s",
            user.getUsername(),
            user.getEmail(),
            user.getCreatedBy() != null ? user.getCreatedBy() : "SYSTEM"
        );

        auditLogger.info(message);
        logger.debug("User created - Username: {}, Email: {}", user.getUsername(), user.getEmail());
    }

    /**
     * Journalise une modification d'utilisateur
     */
    public void logUserUpdate(User user) {
        String message = String.format(
            "Event: USER_UPDATED | User: %s | UpdatedBy: %s | UpdatedAt: %s",
            user.getUsername(),
            user.getUpdatedBy() != null ? user.getUpdatedBy() : "SYSTEM",
            user.getUpdatedAt()
        );

        auditLogger.info(message);
        logger.debug("User updated - Username: {}, UpdatedBy: {}", 
            user.getUsername(), user.getUpdatedBy());
    }

    /**
     * Journalise une suppression d'utilisateur
     */
    public void logUserDeletion(User user, String deletedBy) {
        String message = String.format(
            "Event: USER_DELETED | User: %s | DeletedBy: %s | DeletedAt: %s",
            user.getUsername(),
            deletedBy != null ? deletedBy : "SYSTEM",
            LocalDateTime.now()
        );

        auditLogger.warn(message);
        logger.debug("User deleted - Username: {}, DeletedBy: {}", user.getUsername(), deletedBy);
    }

    /**
     * Journalise un changement de statut KYC
     */
    public void logKycStatusChange(User user, String oldStatus, String newStatus) {
        String message = String.format(
            "Event: KYC_STATUS_CHANGE | User: %s | OldStatus: %s | NewStatus: %s | ChangedAt: %s",
            user.getUsername(),
            oldStatus,
            newStatus,
            LocalDateTime.now()
        );

        auditLogger.info(message);
        logger.debug("KYC status change - User: {}, OldStatus: {}, NewStatus: {}", 
            user.getUsername(), oldStatus, newStatus);
    }

    /**
     * Journalise un changement de statut AML
     */
    public void logAmlStatusChange(User user, String oldStatus, String newStatus) {
        String message = String.format(
            "Event: AML_STATUS_CHANGE | User: %s | OldStatus: %s | NewStatus: %s | ChangedAt: %s",
            user.getUsername(),
            oldStatus,
            newStatus,
            LocalDateTime.now()
        );

        auditLogger.info(message);
        logger.debug("AML status change - User: {}, OldStatus: {}, NewStatus: {}", 
            user.getUsername(), oldStatus, newStatus);
    }

    /**
     * Journalise un changement de score de risque
     */
    public void logRiskScoreChange(User user, Integer oldScore, Integer newScore) {
        String message = String.format(
            "Event: RISK_SCORE_CHANGE | User: %s | OldScore: %d | NewScore: %d | ChangedAt: %s",
            user.getUsername(),
            oldScore != null ? oldScore : 0,
            newScore != null ? newScore : 0,
            LocalDateTime.now()
        );

        auditLogger.info(message);
        logger.debug("Risk score change - User: {}, OldScore: {}, NewScore: {}", 
            user.getUsername(), oldScore, newScore);
    }

    /**
     * Journalise un accès à une ressource sensible
     */
    public void logSensitiveResourceAccess(User user, String resource, String action, boolean success) {
        String eventType = success ? "SENSITIVE_ACCESS_SUCCESS" : "SENSITIVE_ACCESS_FAILED";
        String message = String.format(
            "Event: %s | User: %s | Resource: %s | Action: %s | Success: %s",
            eventType,
            user.getUsername(),
            resource,
            action,
            success
        );

        auditLogger.warn(message);
        logger.debug("Sensitive resource access - User: {}, Resource: {}, Action: {}, Success: {}", 
            user.getUsername(), resource, action, success);
    }

    /**
     * Journalise une tentative d'accès non autorisé
     */
    public void logUnauthorizedAccess(String username, String resource, String ipAddress) {
        String message = String.format(
            "Event: UNAUTHORIZED_ACCESS | User: %s | Resource: %s | IP: %s | Timestamp: %s",
            username != null ? username : "ANONYMOUS",
            resource,
            ipAddress != null ? ipAddress : "UNKNOWN",
            LocalDateTime.now()
        );

        auditLogger.warn(message);
        logger.warn("Unauthorized access attempt - User: {}, Resource: {}, IP: {}", 
            username, resource, ipAddress);
    }

    /**
     * Journalise une activité suspecte
     */
    public void logSuspiciousActivity(User user, String activity, String details) {
        String message = String.format(
            "Event: SUSPICIOUS_ACTIVITY | User: %s | Activity: %s | Details: %s | Timestamp: %s",
            user != null ? user.getUsername() : "UNKNOWN",
            activity,
            details,
            LocalDateTime.now()
        );

        auditLogger.warn(message);
        logger.warn("Suspicious activity detected - User: {}, Activity: {}, Details: {}", 
            user != null ? user.getUsername() : "UNKNOWN", activity, details);
    }

    /**
     * Journalise un événement de sécurité critique
     */
    public void logSecurityEvent(String eventType, String details, String severity) {
        String message = String.format(
            "Event: %s | Details: %s | Severity: %s | Timestamp: %s",
            eventType,
            details,
            severity,
            LocalDateTime.now()
        );

        switch (severity.toUpperCase()) {
            case "CRITICAL":
                auditLogger.error(message);
                logger.error("Critical security event - Type: {}, Details: {}", eventType, details);
                break;
            case "HIGH":
                auditLogger.warn(message);
                logger.warn("High severity security event - Type: {}, Details: {}", eventType, details);
                break;
            case "MEDIUM":
                auditLogger.info(message);
                logger.info("Medium severity security event - Type: {}, Details: {}", eventType, details);
                break;
            case "LOW":
                auditLogger.info(message);
                logger.debug("Low severity security event - Type: {}, Details: {}", eventType, details);
                break;
            default:
                auditLogger.info(message);
                logger.info("Security event - Type: {}, Details: {}", eventType, details);
        }
    }

    /**
     * Journalise un événement de transfert
     */
    public void logTransferEvent(String transferId, String eventType, String details, User user) {
        String message = String.format(
            "Event: TRANSFER_%s | TransferId: %s | User: %s | Details: %s | Timestamp: %s",
            eventType.toUpperCase(),
            transferId,
            user != null ? user.getUsername() : "SYSTEM",
            details,
            LocalDateTime.now()
        );

        auditLogger.info(message);
        logger.debug("Transfer event - TransferId: {}, EventType: {}, User: {}, Details: {}", 
            transferId, eventType, user != null ? user.getUsername() : "SYSTEM", details);
    }

    /**
     * Journalise un événement de compte
     */
    public void logAccountEvent(String accountId, String eventType, String details, User user) {
        String message = String.format(
            "Event: ACCOUNT_%s | AccountId: %s | User: %s | Details: %s | Timestamp: %s",
            eventType.toUpperCase(),
            accountId,
            user != null ? user.getUsername() : "SYSTEM",
            details,
            LocalDateTime.now()
        );

        auditLogger.info(message);
        logger.debug("Account event - AccountId: {}, EventType: {}, User: {}, Details: {}", 
            accountId, eventType, user != null ? user.getUsername() : "SYSTEM", details);
    }

    /**
     * Journalise un événement système
     */
    public void logSystemEvent(String eventType, String details, String severity) {
        String message = String.format(
            "Event: SYSTEM_%s | Details: %s | Severity: %s | Timestamp: %s",
            eventType.toUpperCase(),
            details,
            severity,
            LocalDateTime.now()
        );

        auditLogger.info(message);
        logger.info("System event - Type: {}, Details: {}, Severity: {}", eventType, details, severity);
    }

    /**
     * Génère un ID de corrélation pour le suivi des événements
     */
    public String generateCorrelationId() {
        return UUID.randomUUID().toString();
    }

    /**
     * Journalise un événement avec un ID de corrélation
     */
    public void logEventWithCorrelation(String correlationId, String eventType, String details) {
        String message = String.format(
            "Event: %s | CorrelationId: %s | Details: %s | Timestamp: %s",
            eventType,
            correlationId,
            details,
            LocalDateTime.now()
        );

        auditLogger.info(message);
        logger.debug("Event with correlation - CorrelationId: {}, EventType: {}, Details: {}", 
            correlationId, eventType, details);
    }
}
package com.banking.transfers.service;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.model.User;

import java.util.Optional;
import java.util.UUID;

/**
 * Service d'authentification
 */
public interface AuthService {
    
    /**
     * Authentifier un utilisateur
     */
    LoginResponse authenticate(LoginRequest loginRequest);
    
    /**
     * Authentifier un utilisateur avec MFA
     */
    LoginResponse authenticateWithMfa(LoginRequest loginRequest);
    
    /**
     * Rafraîchir un token d'accès
     */
    LoginResponse refreshToken(String refreshToken);
    
    /**
     * Révoquer un token
     */
    void revokeToken(String token);
    
    /**
     * Déconnecter un utilisateur
     */
    void logout(String token);
    
    /**
     * Valider un token d'accès
     */
    boolean validateToken(String token);
    
    /**
     * Obtenir les informations de l'utilisateur à partir du token
     */
    Optional<User> getUserFromToken(String token);
    
    /**
     * Obtenir l'ID de l'utilisateur à partir du token
     */
    Optional<UUID> getUserIdFromToken(String token);
    
    /**
     * Générer un token d'accès pour un utilisateur
     */
    String generateAccessToken(User user);
    
    /**
     * Générer un token de rafraîchissement pour un utilisateur
     */
    String generateRefreshToken(User user);
    
    /**
     * Générer un code d'autorisation OAuth2
     */
    String generateAuthorizationCode(User user, String clientId, String redirectUri, String scope);
    
    /**
     * Échanger un code d'autorisation contre un token d'accès
     */
    LoginResponse exchangeAuthorizationCode(String authorizationCode, String clientId, String clientSecret, String redirectUri);
    
    /**
     * Générer un ID Token OpenID Connect
     */
    String generateIdToken(User user, String clientId, String nonce);
    
    /**
     * Valider un code MFA
     */
    boolean validateMfaCode(User user, String mfaCode);
    
    /**
     * Générer un secret MFA pour un utilisateur
     */
    String generateMfaSecret(User user);
    
    /**
     * Activer MFA pour un utilisateur
     */
    void enableMfa(User user, String mfaSecret);
    
    /**
     * Désactiver MFA pour un utilisateur
     */
    void disableMfa(User user);
    
    /**
     * Vérifier si un utilisateur a besoin de MFA
     */
    boolean isMfaRequired(User user);
    
    /**
     * Vérifier si un utilisateur peut se connecter
     */
    boolean canUserLogin(User user);
    
    /**
     * Incrémenter le compteur de tentatives de connexion échouées
     */
    void incrementFailedLoginAttempts(User user);
    
    /**
     * Réinitialiser le compteur de tentatives de connexion échouées
     */
    void resetFailedLoginAttempts(User user);
    
    /**
     * Verrouiller un compte utilisateur
     */
    void lockUserAccount(User user);
    
    /**
     * Déverrouiller un compte utilisateur
     */
    void unlockUserAccount(User user);
    
    /**
     * Mettre à jour la date de dernière connexion
     */
    void updateLastLoginDate(User user);
    
    /**
     * Vérifier si un token est expiré
     */
    boolean isTokenExpired(String token);
    
    /**
     * Obtenir la date d'expiration d'un token
     */
    java.time.LocalDateTime getTokenExpirationDate(String token);
    
    /**
     * Obtenir les rôles d'un utilisateur
     */
    java.util.List<String> getUserRoles(User user);
    
    /**
     * Obtenir les permissions d'un utilisateur
     */
    java.util.List<String> getUserPermissions(User user);
    
    /**
     * Vérifier si un utilisateur a un rôle spécifique
     */
    boolean hasRole(User user, String role);
    
    /**
     * Vérifier si un utilisateur a une permission spécifique
     */
    boolean hasPermission(User user, String permission);
    
    /**
     * Vérifier si un utilisateur a au moins un des rôles spécifiés
     */
    boolean hasAnyRole(User user, java.util.List<String> roles);
    
    /**
     * Vérifier si un utilisateur a au moins une des permissions spécifiées
     */
    boolean hasAnyPermission(User user, java.util.List<String> permissions);
    
    /**
     * Vérifier si un utilisateur a tous les rôles spécifiés
     */
    boolean hasAllRoles(User user, java.util.List<String> roles);
    
    /**
     * Vérifier si un utilisateur a toutes les permissions spécifiées
     */
    boolean hasAllPermissions(User user, java.util.List<String> permissions);
    
    /**
     * Créer une session pour un utilisateur
     */
    String createSession(User user, String clientId, String userAgent, String ipAddress);
    
    /**
     * Valider une session
     */
    boolean validateSession(String sessionId);
    
    /**
     * Supprimer une session
     */
    void removeSession(String sessionId);
    
    /**
     * Obtenir les informations de session
     */
    java.util.Map<String, Object> getSessionInfo(String sessionId);
    
    /**
     * Renouveler une session
     */
    void renewSession(String sessionId);
    
    /**
     * Obtenir toutes les sessions actives d'un utilisateur
     */
    java.util.List<String> getUserActiveSessions(UUID userId);
    
    /**
     * Supprimer toutes les sessions d'un utilisateur
     */
    void removeAllUserSessions(UUID userId);
    
    /**
     * Supprimer toutes les sessions sauf la session actuelle
     */
    void removeOtherUserSessions(UUID userId, String currentSessionId);
    
    /**
     * Obtenir les statistiques d'authentification
     */
    java.util.Map<String, Object> getAuthStatistics();
    
    /**
     * Nettoyer les sessions expirées
     */
    void cleanupExpiredSessions();
    
    /**
     * Nettoyer les tokens expirés
     */
    void cleanupExpiredTokens();
    
    /**
     * Obtenir l'historique des connexions d'un utilisateur
     */
    java.util.List<java.util.Map<String, Object>> getUserLoginHistory(UUID userId, int limit);
    
    /**
     * Enregistrer une tentative de connexion
     */
    void logLoginAttempt(String username, String ipAddress, String userAgent, boolean success, String reason);
    
    /**
     * Obtenir les tentatives de connexion récentes
     */
    java.util.List<java.util.Map<String, Object>> getRecentLoginAttempts(String username, int limit);
    
    /**
     * Vérifier si un utilisateur est bloqué par IP
     */
    boolean isIpBlocked(String ipAddress);
    
    /**
     * Bloquer une adresse IP
     */
    void blockIpAddress(String ipAddress, String reason, int durationMinutes);
    
    /**
     * Débloquer une adresse IP
     */
    void unblockIpAddress(String ipAddress);
    
    /**
     * Obtenir les adresses IP bloquées
     */
    java.util.List<java.util.Map<String, Object>> getBlockedIpAddresses();
}
package com.banking.transfers.service.impl;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.model.User;
import com.banking.transfers.repository.UserRepository;
import com.banking.transfers.service.AuthService;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import javax.crypto.SecretKey;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.*;
import java.util.concurrent.TimeUnit;

/**
 * Implémentation du service d'authentification
 */
@Service
@Transactional
public class AuthServiceImpl implements AuthService {
    
    private static final Logger logger = LoggerFactory.getLogger(AuthServiceImpl.class);
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    @Autowired
    private RedisTemplate<String, Object> redisTemplate;
    
    @Value("${app.jwt.secret}")
    private String jwtSecret;
    
    @Value("${app.jwt.access-token.expiration:3600}")
    private long accessTokenExpiration;
    
    @Value("${app.jwt.refresh-token.expiration:86400}")
    private long refreshTokenExpiration;
    
    @Value("${app.jwt.authorization-code.expiration:600}")
    private long authorizationCodeExpiration;
    
    @Value("${app.session.expiration:3600}")
    private long sessionExpiration;
    
    @Value("${app.mfa.max-attempts:3}")
    private int maxMfaAttempts;
    
    @Value("${app.login.max-failed-attempts:5}")
    private int maxFailedLoginAttempts;
    
    @Value("${app.ip.block-duration:30}")
    private int ipBlockDuration;
    
    private final SecretKey secretKey;
    
    public AuthServiceImpl(@Value("${app.jwt.secret}") String jwtSecret) {
        this.jwtSecret = jwtSecret;
        this.secretKey = Keys.hmacShaKeyFor(jwtSecret.getBytes());
    }
    
    @Override
    public LoginResponse authenticate(LoginRequest loginRequest) {
        logger.info("Tentative d'authentification pour: {}", loginRequest.getUsernameOrEmail());
        
        try {
            // Vérifier si l'IP est bloquée
            String clientIp = getClientIpAddress();
            if (isIpBlocked(clientIp)) {
                logger.warn("Tentative de connexion depuis une IP bloquée: {}", clientIp);
                return createErrorResponse("access_denied", "IP address is blocked");
            }
            
            // Trouver l'utilisateur
            Optional<User> userOpt = findUser(loginRequest.getUsernameOrEmail());
            if (userOpt.isEmpty()) {
                logger.warn("Tentative de connexion avec un utilisateur inexistant: {}", loginRequest.getUsernameOrEmail());
                logLoginAttempt(loginRequest.getUsernameOrEmail(), clientIp, "Unknown", false, "User not found");
                return createErrorResponse("invalid_credentials", "Invalid username or password");
            }
            
            User user = userOpt.get();
            
            // Vérifier si l'utilisateur peut se connecter
            if (!canUserLogin(user)) {
                logger.warn("Tentative de connexion pour un compte verrouillé/inactif: {}", user.getUsername());
                logLoginAttempt(user.getUsername(), clientIp, "Unknown", false, "Account locked or inactive");
                return createErrorResponse("account_locked", "Account is locked or inactive");
            }
            
            // Vérifier le mot de passe
            if (!passwordEncoder.matches(loginRequest.getPassword(), user.getPasswordHash())) {
                logger.warn("Tentative de connexion avec un mot de passe incorrect pour: {}", user.getUsername());
                incrementFailedLoginAttempts(user);
                logLoginAttempt(user.getUsername(), clientIp, "Unknown", false, "Invalid password");
                return createErrorResponse("invalid_credentials", "Invalid username or password");
            }
            
            // Vérifier si MFA est requis
            if (isMfaRequired(user) && !loginRequest.isMfaRequired()) {
                logger.info("MFA requis pour l'utilisateur: {}", user.getUsername());
                return createMfaRequiredResponse(user);
            }
            
            // Valider le code MFA si fourni
            if (loginRequest.isMfaRequired()) {
                if (!validateMfaCode(user, loginRequest.getMfaCode())) {
                    logger.warn("Code MFA invalide pour l'utilisateur: {}", user.getUsername());
                    logLoginAttempt(user.getUsername(), clientIp, "Unknown", false, "Invalid MFA code");
                    return createErrorResponse("invalid_mfa", "Invalid MFA code");
                }
            }
            
            // Authentification réussie
            logger.info("Authentification réussie pour l'utilisateur: {}", user.getUsername());
            
            // Réinitialiser les tentatives échouées et mettre à jour la dernière connexion
            resetFailedLoginAttempts(user);
            updateLastLoginDate(user);
            
            // Créer la session
            String sessionId = createSession(user, loginRequest.getClientId(), "Unknown", clientIp);
            
            // Générer les tokens
            String accessToken = generateAccessToken(user);
            String refreshToken = generateRefreshToken(user);
            
            // Créer la réponse
            LoginResponse response = new LoginResponse(accessToken, refreshToken, user.getId(), user.getUsername());
            response.setEmail(user.getEmail());
            response.setFirstName(user.getFirstName());
            response.setLastName(user.getLastName());
            response.setFullName(user.getFullName());
            response.setRoles(getUserRoles(user));
            response.setPermissions(getUserPermissions(user));
            response.setKycStatus(user.getKycStatus());
            response.setAmlStatus(user.getAmlStatus());
            response.setRiskScore(user.getRiskScore());
            response.setMfaEnabled(user.getMfaEnabled());
            response.setMfaRequired(false);
            response.setPreferredLanguage(user.getPreferredLanguage());
            response.setTimezone(user.getTimezone());
            response.setLastLoginDate(user.getLastLoginDate());
            response.setSessionId(sessionId);
            response.setClientId(loginRequest.getClientId());
            response.setScope(loginRequest.getScope());
            
            // Calculer l'expiration
            LocalDateTime expiresAt = LocalDateTime.now().plusSeconds(accessTokenExpiration);
            response.setTokenExpiresAt(expiresAt);
            response.calculateExpiresIn();
            
            // Enregistrer la tentative de connexion réussie
            logLoginAttempt(user.getUsername(), clientIp, "Unknown", true, "Success");
            
            return response;
            
        } catch (Exception e) {
            logger.error("Erreur lors de l'authentification", e);
            return createErrorResponse("server_error", "Internal server error");
        }
    }
    
    @Override
    public LoginResponse authenticateWithMfa(LoginRequest loginRequest) {
        // Cette méthode est identique à authenticate() car la validation MFA est déjà incluse
        return authenticate(loginRequest);
    }
    
    @Override
    public LoginResponse refreshToken(String refreshToken) {
        logger.info("Tentative de rafraîchissement de token");
        
        try {
            // Valider le refresh token
            if (!validateToken(refreshToken)) {
                logger.warn("Refresh token invalide");
                return createErrorResponse("invalid_token", "Invalid refresh token");
            }
            
            // Extraire les informations du token
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(refreshToken)
                    .getBody();
            
            String userId = claims.getSubject();
            String tokenType = claims.get("type", String.class);
            
            if (!"refresh".equals(tokenType)) {
                logger.warn("Token n'est pas un refresh token");
                return createErrorResponse("invalid_token", "Invalid token type");
            }
            
            // Trouver l'utilisateur
            Optional<User> userOpt = userRepository.findById(UUID.fromString(userId));
            if (userOpt.isEmpty()) {
                logger.warn("Utilisateur non trouvé pour le refresh token: {}", userId);
                return createErrorResponse("invalid_token", "User not found");
            }
            
            User user = userOpt.get();
            
            // Vérifier si l'utilisateur peut toujours se connecter
            if (!canUserLogin(user)) {
                logger.warn("Utilisateur verrouillé/inactif lors du refresh: {}", user.getUsername());
                return createErrorResponse("account_locked", "Account is locked or inactive");
            }
            
            // Générer de nouveaux tokens
            String newAccessToken = generateAccessToken(user);
            String newRefreshToken = generateRefreshToken(user);
            
            // Créer la réponse
            LoginResponse response = new LoginResponse(newAccessToken, newRefreshToken, user.getId(), user.getUsername());
            response.setEmail(user.getEmail());
            response.setFirstName(user.getFirstName());
            response.setLastName(user.getLastName());
            response.setFullName(user.getFullName());
            response.setRoles(getUserRoles(user));
            response.setPermissions(getUserPermissions(user));
            response.setKycStatus(user.getKycStatus());
            response.setAmlStatus(user.getAmlStatus());
            response.setRiskScore(user.getRiskScore());
            response.setMfaEnabled(user.getMfaEnabled());
            response.setMfaRequired(false);
            response.setPreferredLanguage(user.getPreferredLanguage());
            response.setTimezone(user.getTimezone());
            response.setLastLoginDate(user.getLastLoginDate());
            
            // Calculer l'expiration
            LocalDateTime expiresAt = LocalDateTime.now().plusSeconds(accessTokenExpiration);
            response.setTokenExpiresAt(expiresAt);
            response.calculateExpiresIn();
            
            // Révoquer l'ancien refresh token
            revokeToken(refreshToken);
            
            logger.info("Token rafraîchi avec succès pour l'utilisateur: {}", user.getUsername());
            return response;
            
        } catch (Exception e) {
            logger.error("Erreur lors du rafraîchissement du token", e);
            return createErrorResponse("server_error", "Internal server error");
        }
    }
    
    @Override
    public void revokeToken(String token) {
        try {
            // Ajouter le token à la liste noire dans Redis
            String tokenKey = "revoked_token:" + token;
            redisTemplate.opsForValue().set(tokenKey, "revoked", accessTokenExpiration, TimeUnit.SECONDS);
            logger.info("Token révoqué");
        } catch (Exception e) {
            logger.error("Erreur lors de la révocation du token", e);
        }
    }
    
    @Override
    public void logout(String token) {
        try {
            // Révoquer le token
            revokeToken(token);
            
            // Supprimer la session si elle existe
            Optional<User> userOpt = getUserFromToken(token);
            if (userOpt.isPresent()) {
                User user = userOpt.get();
                // Note: La sessionId devrait être extraite du token ou passée en paramètre
                // Pour simplifier, on supprime toutes les sessions de l'utilisateur
                removeAllUserSessions(user.getId());
            }
            
            logger.info("Déconnexion réussie");
        } catch (Exception e) {
            logger.error("Erreur lors de la déconnexion", e);
        }
    }
    
    @Override
    public boolean validateToken(String token) {
        try {
            // Vérifier si le token est dans la liste noire
            String tokenKey = "revoked_token:" + token;
            if (Boolean.TRUE.equals(redisTemplate.hasKey(tokenKey))) {
                logger.warn("Token trouvé dans la liste noire");
                return false;
            }
            
            // Valider le token JWT
            Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(token);
            
            return true;
        } catch (Exception e) {
            logger.warn("Token invalide: {}", e.getMessage());
            return false;
        }
    }
    
    @Override
    public Optional<User> getUserFromToken(String token) {
        try {
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();
            
            String userId = claims.getSubject();
            return userRepository.findById(UUID.fromString(userId));
        } catch (Exception e) {
            logger.warn("Impossible d'extraire l'utilisateur du token: {}", e.getMessage());
            return Optional.empty();
        }
    }
    
    @Override
    public Optional<UUID> getUserIdFromToken(String token) {
        try {
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();
            
            String userId = claims.getSubject();
            return Optional.of(UUID.fromString(userId));
        } catch (Exception e) {
            logger.warn("Impossible d'extraire l'ID utilisateur du token: {}", e.getMessage());
            return Optional.empty();
        }
    }
    
    @Override
    public String generateAccessToken(User user) {
        Date now = new Date();
        Date expiration = Date.from(LocalDateTime.now().plusSeconds(accessTokenExpiration)
                .atZone(ZoneId.systemDefault()).toInstant());
        
        return Jwts.builder()
                .setSubject(user.getId().toString())
                .claim("username", user.getUsername())
                .claim("email", user.getEmail())
                .claim("type", "access")
                .claim("roles", getUserRoles(user))
                .claim("permissions", getUserPermissions(user))
                .setIssuedAt(now)
                .setExpiration(expiration)
                .signWith(secretKey)
                .compact();
    }
    
    @Override
    public String generateRefreshToken(User user) {
        Date now = new Date();
        Date expiration = Date.from(LocalDateTime.now().plusSeconds(refreshTokenExpiration)
                .atZone(ZoneId.systemDefault()).toInstant());
        
        return Jwts.builder()
                .setSubject(user.getId().toString())
                .claim("username", user.getUsername())
                .claim("type", "refresh")
                .setIssuedAt(now)
                .setExpiration(expiration)
                .signWith(secretKey)
                .compact();
    }
    
    // Méthodes utilitaires privées
    private Optional<User> findUser(String usernameOrEmail) {
        if (usernameOrEmail.contains("@")) {
            return userRepository.findByEmail(usernameOrEmail);
        } else {
            return userRepository.findByUsername(usernameOrEmail);
        }
    }
    
    private String getClientIpAddress() {
        // Cette méthode devrait être implémentée pour récupérer l'IP du client
        // Pour l'instant, on retourne une valeur par défaut
        return "127.0.0.1";
    }
    
    private LoginResponse createErrorResponse(String error, String errorDescription) {
        LoginResponse response = new LoginResponse();
        response.setError(error);
        response.setErrorDescription(errorDescription);
        return response;
    }
    
    private LoginResponse createMfaRequiredResponse(User user) {
        LoginResponse response = new LoginResponse();
        response.setUserId(user.getId());
        response.setUsername(user.getUsername());
        response.setMfaRequired(true);
        response.setMfaType("TOTP");
        return response;
    }
    
    // Implémentations des autres méthodes...
    // Note: Pour des raisons de concision, toutes les méthodes ne sont pas implémentées ici
    // Les méthodes manquantes devraient être implémentées selon les besoins spécifiques
    
    @Override
    public String generateAuthorizationCode(User user, String clientId, String redirectUri, String scope) {
        // Implémentation pour OAuth2
        return null;
    }
    
    @Override
    public LoginResponse exchangeAuthorizationCode(String authorizationCode, String clientId, String clientSecret, String redirectUri) {
        // Implémentation pour OAuth2
        return null;
    }
    
    @Override
    public String generateIdToken(User user, String clientId, String nonce) {
        // Implémentation pour OpenID Connect
        return null;
    }
    
    @Override
    public boolean validateMfaCode(User user, String mfaCode) {
        // Implémentation pour la validation MFA
        return false;
    }
    
    @Override
    public String generateMfaSecret(User user) {
        // Implémentation pour la génération du secret MFA
        return null;
    }
    
    @Override
    public void enableMfa(User user, String mfaSecret) {
        // Implémentation pour activer MFA
    }
    
    @Override
    public void disableMfa(User user) {
        // Implémentation pour désactiver MFA
    }
    
    @Override
    public boolean isMfaRequired(User user) {
        return user.getMfaEnabled() != null && user.getMfaEnabled();
    }
    
    @Override
    public boolean canUserLogin(User user) {
        return user.getIsActive() && !user.getIsLocked() && 
               user.getKycStatus().isValid() && user.getAmlStatus().isValid();
    }
    
    @Override
    public void incrementFailedLoginAttempts(User user) {
        user.incrementFailedLoginAttempts();
        userRepository.save(user);
    }
    
    @Override
    public void resetFailedLoginAttempts(User user) {
        user.resetFailedLoginAttempts();
        userRepository.save(user);
    }
    
    @Override
    public void lockUserAccount(User user) {
        user.setIsLocked(true);
        userRepository.save(user);
    }
    
    @Override
    public void unlockUserAccount(User user) {
        user.setIsLocked(false);
        user.setFailedLoginAttempts(0);
        userRepository.save(user);
    }
    
    @Override
    public void updateLastLoginDate(User user) {
        user.updateLastLogin();
        userRepository.save(user);
    }
    
    @Override
    public boolean isTokenExpired(String token) {
        try {
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();
            
            return claims.getExpiration().before(new Date());
        } catch (Exception e) {
            return true;
        }
    }
    
    @Override
    public LocalDateTime getTokenExpirationDate(String token) {
        try {
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(secretKey)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();
            
            return claims.getExpiration().toInstant()
                    .atZone(ZoneId.systemDefault())
                    .toLocalDateTime();
        } catch (Exception e) {
            return null;
        }
    }
    
    @Override
    public List<String> getUserRoles(User user) {
        // Implémentation pour récupérer les rôles de l'utilisateur
        return new ArrayList<>();
    }
    
    @Override
    public List<String> getUserPermissions(User user) {
        // Implémentation pour récupérer les permissions de l'utilisateur
        return new ArrayList<>();
    }
    
    @Override
    public boolean hasRole(User user, String role) {
        return getUserRoles(user).contains(role);
    }
    
    @Override
    public boolean hasPermission(User user, String permission) {
        return getUserPermissions(user).contains(permission);
    }
    
    @Override
    public boolean hasAnyRole(User user, List<String> roles) {
        List<String> userRoles = getUserRoles(user);
        return userRoles.stream().anyMatch(roles::contains);
    }
    
    @Override
    public boolean hasAnyPermission(User user, List<String> permissions) {
        List<String> userPermissions = getUserPermissions(user);
        return userPermissions.stream().anyMatch(permissions::contains);
    }
    
    @Override
    public boolean hasAllRoles(User user, List<String> roles) {
        List<String> userRoles = getUserRoles(user);
        return userRoles.containsAll(roles);
    }
    
    @Override
    public boolean hasAllPermissions(User user, List<String> permissions) {
        List<String> userPermissions = getUserPermissions(user);
        return userPermissions.containsAll(permissions);
    }
    
    @Override
    public String createSession(User user, String clientId, String userAgent, String ipAddress) {
        String sessionId = UUID.randomUUID().toString();
        Map<String, Object> sessionData = new HashMap<>();
        sessionData.put("userId", user.getId().toString());
        sessionData.put("username", user.getUsername());
        sessionData.put("clientId", clientId);
        sessionData.put("userAgent", userAgent);
        sessionData.put("ipAddress", ipAddress);
        sessionData.put("createdAt", LocalDateTime.now());
        sessionData.put("lastActivity", LocalDateTime.now());
        
        String sessionKey = "session:" + sessionId;
        redisTemplate.opsForHash().putAll(sessionKey, sessionData);
        redisTemplate.expire(sessionKey, sessionExpiration, TimeUnit.SECONDS);
        
        return sessionId;
    }
    
    @Override
    public boolean validateSession(String sessionId) {
        String sessionKey = "session:" + sessionId;
        return Boolean.TRUE.equals(redisTemplate.hasKey(sessionKey));
    }
    
    @Override
    public void removeSession(String sessionId) {
        String sessionKey = "session:" + sessionId;
        redisTemplate.delete(sessionKey);
    }
    
    @Override
    public Map<String, Object> getSessionInfo(String sessionId) {
        String sessionKey = "session:" + sessionId;
        return redisTemplate.opsForHash().entries(sessionKey);
    }
    
    @Override
    public void renewSession(String sessionId) {
        String sessionKey = "session:" + sessionId;
        redisTemplate.opsForHash().put(sessionKey, "lastActivity", LocalDateTime.now());
        redisTemplate.expire(sessionKey, sessionExpiration, TimeUnit.SECONDS);
    }
    
    @Override
    public List<String> getUserActiveSessions(UUID userId) {
        // Implémentation pour récupérer les sessions actives d'un utilisateur
        return new ArrayList<>();
    }
    
    @Override
    public void removeAllUserSessions(UUID userId) {
        // Implémentation pour supprimer toutes les sessions d'un utilisateur
    }
    
    @Override
    public void removeOtherUserSessions(UUID userId, String currentSessionId) {
        // Implémentation pour supprimer les autres sessions d'un utilisateur
    }
    
    @Override
    public Map<String, Object> getAuthStatistics() {
        // Implémentation pour les statistiques d'authentification
        return new HashMap<>();
    }
    
    @Override
    public void cleanupExpiredSessions() {
        // Implémentation pour nettoyer les sessions expirées
    }
    
    @Override
    public void cleanupExpiredTokens() {
        // Implémentation pour nettoyer les tokens expirés
    }
    
    @Override
    public List<Map<String, Object>> getUserLoginHistory(UUID userId, int limit) {
        // Implémentation pour l'historique des connexions
        return new ArrayList<>();
    }
    
    @Override
    public void logLoginAttempt(String username, String ipAddress, String userAgent, boolean success, String reason) {
        // Implémentation pour enregistrer les tentatives de connexion
    }
    
    @Override
    public List<Map<String, Object>> getRecentLoginAttempts(String username, int limit) {
        // Implémentation pour récupérer les tentatives récentes
        return new ArrayList<>();
    }
    
    @Override
    public boolean isIpBlocked(String ipAddress) {
        String blockKey = "ip_blocked:" + ipAddress;
        return Boolean.TRUE.equals(redisTemplate.hasKey(blockKey));
    }
    
    @Override
    public void blockIpAddress(String ipAddress, String reason, int durationMinutes) {
        String blockKey = "ip_blocked:" + ipAddress;
        Map<String, Object> blockData = new HashMap<>();
        blockData.put("reason", reason);
        blockData.put("blockedAt", LocalDateTime.now());
        blockData.put("expiresAt", LocalDateTime.now().plusMinutes(durationMinutes));
        
        redisTemplate.opsForHash().putAll(blockKey, blockData);
        redisTemplate.expire(blockKey, durationMinutes, TimeUnit.MINUTES);
    }
    
    @Override
    public void unblockIpAddress(String ipAddress) {
        String blockKey = "ip_blocked:" + ipAddress;
        redisTemplate.delete(blockKey);
    }
    
    @Override
    public List<Map<String, Object>> getBlockedIpAddresses() {
        // Implémentation pour récupérer les IPs bloquées
        return new ArrayList<>();
    }
}
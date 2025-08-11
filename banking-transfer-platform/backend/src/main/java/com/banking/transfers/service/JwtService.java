package com.banking.transfers.service;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

/**
 * Service pour la gestion des tokens JWT
 */
@Service
public class JwtService {

    @Value("${jwt.secret:defaultSecretKeyForDevelopmentOnly}")
    private String secret;

    @Value("${jwt.expiration:86400}")
    private long expiration;

    @Value("${jwt.refresh-expiration:604800}")
    private long refreshExpiration;

    private SecretKey getSigningKey() {
        byte[] keyBytes = secret.getBytes();
        return Keys.hmacShaKeyFor(keyBytes);
    }

    /**
     * Extrait le nom d'utilisateur depuis un token
     */
    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    /**
     * Extrait la date d'expiration depuis un token
     */
    public Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    /**
     * Extrait une claim spécifique depuis un token
     */
    public <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    /**
     * Extrait toutes les claims depuis un token
     */
    private Claims extractAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    /**
     * Vérifie si un token est expiré
     */
    private Boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    /**
     * Génère un token pour un utilisateur
     */
    public String generateToken(String username) {
        Map<String, Object> claims = new HashMap<>();
        return createToken(claims, username, expiration);
    }

    /**
     * Génère un token avec des claims personnalisées
     */
    public String generateToken(String username, Map<String, Object> claims) {
        return createToken(claims, username, expiration);
    }

    /**
     * Génère un refresh token
     */
    public String generateRefreshToken(String username) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("type", "refresh");
        return createToken(claims, username, refreshExpiration);
    }

    /**
     * Crée un token JWT
     */
    private String createToken(Map<String, Object> claims, String subject, long expiration) {
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(subject)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + expiration * 1000))
                .setIssuer("banking-transfer-platform")
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    /**
     * Valide un token
     */
    public Boolean validateToken(String token, String username) {
        final String extractedUsername = extractUsername(token);
        return (username.equals(extractedUsername) && !isTokenExpired(token));
    }

    /**
     * Valide un token sans vérifier le nom d'utilisateur
     */
    public Boolean validateToken(String token) {
        try {
            return !isTokenExpired(token);
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * Valide un refresh token
     */
    public Boolean validateRefreshToken(String token) {
        try {
            Claims claims = extractAllClaims(token);
            String type = claims.get("type", String.class);
            return "refresh".equals(type) && !isTokenExpired(token);
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * Extrait les rôles depuis un token
     */
    public String[] extractRoles(String token) {
        Claims claims = extractAllClaims(token);
        Object rolesObj = claims.get("roles");
        if (rolesObj instanceof String[]) {
            return (String[]) rolesObj;
        }
        return new String[0];
    }

    /**
     * Extrait l'ID utilisateur depuis un token
     */
    public String extractUserId(String token) {
        Claims claims = extractAllClaims(token);
        return claims.get("userId", String.class);
    }

    /**
     * Extrait la session ID depuis un token
     */
    public String extractSessionId(String token) {
        Claims claims = extractAllClaims(token);
        return claims.get("sessionId", String.class);
    }

    /**
     * Génère un token avec des informations utilisateur complètes
     */
    public String generateTokenWithUserInfo(String username, String userId, String[] roles, String sessionId) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", userId);
        claims.put("roles", roles);
        claims.put("sessionId", sessionId);
        claims.put("type", "access");
        return createToken(claims, username, expiration);
    }

    /**
     * Génère un token de réinitialisation de mot de passe
     */
    public String generatePasswordResetToken(String username) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("type", "password_reset");
        return createToken(claims, username, 3600); // 1 heure
    }

    /**
     * Valide un token de réinitialisation de mot de passe
     */
    public Boolean validatePasswordResetToken(String token) {
        try {
            Claims claims = extractAllClaims(token);
            String type = claims.get("type", String.class);
            return "password_reset".equals(type) && !isTokenExpired(token);
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * Invalide un token (ajoute à une liste noire)
     * Note: Dans une implémentation complète, vous devriez utiliser Redis ou une base de données
     */
    public void invalidateToken(String token) {
        // TODO: Implémenter l'invalidation de token avec Redis
        // Pour l'instant, on ne fait rien car les tokens JWT sont stateless
    }

    /**
     * Vérifie si un token est dans la liste noire
     */
    public Boolean isTokenBlacklisted(String token) {
        // TODO: Implémenter la vérification de liste noire avec Redis
        return false;
    }

    /**
     * Obtient la durée d'expiration du token d'accès
     */
    public long getAccessTokenExpiration() {
        return expiration;
    }

    /**
     * Obtient la durée d'expiration du refresh token
     */
    public long getRefreshTokenExpiration() {
        return refreshExpiration;
    }

    /**
     * Extrait les informations de base d'un token
     */
    public TokenInfo extractTokenInfo(String token) {
        try {
            Claims claims = extractAllClaims(token);
            return new TokenInfo(
                    claims.getSubject(),
                    claims.get("userId", String.class),
                    extractRoles(token),
                    claims.get("sessionId", String.class),
                    claims.get("type", String.class),
                    claims.getIssuedAt(),
                    claims.getExpiration()
            );
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Classe pour encapsuler les informations d'un token
     */
    public static class TokenInfo {
        private final String username;
        private final String userId;
        private final String[] roles;
        private final String sessionId;
        private final String type;
        private final Date issuedAt;
        private final Date expiresAt;

        public TokenInfo(String username, String userId, String[] roles, String sessionId, 
                        String type, Date issuedAt, Date expiresAt) {
            this.username = username;
            this.userId = userId;
            this.roles = roles;
            this.sessionId = sessionId;
            this.type = type;
            this.issuedAt = issuedAt;
            this.expiresAt = expiresAt;
        }

        // Getters
        public String getUsername() { return username; }
        public String getUserId() { return userId; }
        public String[] getRoles() { return roles; }
        public String getSessionId() { return sessionId; }
        public String getType() { return type; }
        public Date getIssuedAt() { return issuedAt; }
        public Date getExpiresAt() { return expiresAt; }

        public boolean isExpired() {
            return expiresAt.before(new Date());
        }

        public boolean isAccessToken() {
            return "access".equals(type);
        }

        public boolean isRefreshToken() {
            return "refresh".equals(type);
        }

        public boolean isPasswordResetToken() {
            return "password_reset".equals(type);
        }
    }
}
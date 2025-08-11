package com.banking.transfers.service;

import com.banking.transfers.model.User;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Service de gestion des tokens JWT
 */
@Service
public class JwtService {

    @Value("${jwt.secret:default-secret-key-for-development-only}")
    private String jwtSecret;

    @Value("${jwt.access-token.expiration:3600}")
    private Long accessTokenExpiration;

    @Value("${jwt.refresh-token.expiration:86400}")
    private Long refreshTokenExpiration;

    @Value("${jwt.password-reset.expiration:1800}")
    private Long passwordResetExpiration;

    @Value("${jwt.issuer:banking-transfer-platform}")
    private String issuer;

    // Cache des tokens invalides (blacklist)
    private final Map<String, Date> invalidatedTokens = new ConcurrentHashMap<>();

    /**
     * Génère un token d'accès pour un utilisateur
     */
    public String generateAccessToken(User user) {
        return generateToken(user, accessTokenExpiration, "access");
    }

    /**
     * Génère un token de rafraîchissement pour un utilisateur
     */
    public String generateRefreshToken(User user) {
        return generateToken(user, refreshTokenExpiration, "refresh");
    }

    /**
     * Génère un token de réinitialisation de mot de passe
     */
    public String generatePasswordResetToken(User user) {
        return generateToken(user, passwordResetExpiration, "password-reset");
    }

    /**
     * Génère un token générique
     */
    private String generateToken(User user, Long expirationSeconds, String tokenType) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + (expirationSeconds * 1000));

        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", user.getId().toString());
        claims.put("email", user.getEmail());
        claims.put("firstName", user.getFirstName());
        claims.put("lastName", user.getLastName());
        claims.put("kycStatus", user.getKycStatus().name());
        claims.put("amlStatus", user.getAmlStatus().name());
        claims.put("riskScore", user.getRiskScore());
        claims.put("mfaEnabled", user.getMfaEnabled());
        claims.put("tokenType", tokenType);

        return Jwts.builder()
                .setClaims(claims)
                .setSubject(user.getUsername())
                .setIssuer(issuer)
                .setIssuedAt(now)
                .setExpiration(expiryDate)
                .setId(UUID.randomUUID().toString())
                .signWith(getSigningKey(), SignatureAlgorithm.HS512)
                .compact();
    }

    /**
     * Valide un token d'accès
     */
    public boolean validateAccessToken(String token) {
        return validateToken(token, "access");
    }

    /**
     * Valide un token de rafraîchissement
     */
    public boolean validateRefreshToken(String token) {
        return validateToken(token, "refresh");
    }

    /**
     * Valide un token de réinitialisation de mot de passe
     */
    public boolean validatePasswordResetToken(String token) {
        return validateToken(token, "password-reset");
    }

    /**
     * Valide un token générique
     */
    private boolean validateToken(String token, String expectedTokenType) {
        try {
            // Vérifier si le token est dans la liste noire
            if (isTokenInvalidated(token)) {
                return false;
            }

            Claims claims = extractAllClaims(token);
            
            // Vérifier le type de token
            String tokenType = claims.get("tokenType", String.class);
            if (!expectedTokenType.equals(tokenType)) {
                return false;
            }

            // Vérifier l'expiration
            return !isTokenExpired(claims);

        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * Extrait le nom d'utilisateur d'un token
     */
    public String extractUsername(String token) {
        try {
            return extractAllClaims(token).getSubject();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait l'ID utilisateur d'un token
     */
    public UUID extractUserId(String token) {
        try {
            String userIdStr = extractAllClaims(token).get("userId", String.class);
            return userIdStr != null ? UUID.fromString(userIdStr) : null;
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait l'email d'un token
     */
    public String extractEmail(String token) {
        try {
            return extractAllClaims(token).get("email", String.class);
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait le statut KYC d'un token
     */
    public String extractKycStatus(String token) {
        try {
            return extractAllClaims(token).get("kycStatus", String.class);
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait le statut AML d'un token
     */
    public String extractAmlStatus(String token) {
        try {
            return extractAllClaims(token).get("amlStatus", String.class);
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait le score de risque d'un token
     */
    public Integer extractRiskScore(String token) {
        try {
            return extractAllClaims(token).get("riskScore", Integer.class);
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait le statut MFA d'un token
     */
    public Boolean extractMfaEnabled(String token) {
        try {
            return extractAllClaims(token).get("mfaEnabled", Boolean.class);
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait la date d'expiration d'un token
     */
    public Date extractExpiration(String token) {
        try {
            return extractAllClaims(token).getExpiration();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait la date d'émission d'un token
     */
    public Date extractIssuedAt(String token) {
        try {
            return extractAllClaims(token).getIssuedAt();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait l'ID du token
     */
    public String extractTokenId(String token) {
        try {
            return extractAllClaims(token).getId();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Extrait tous les claims d'un token
     */
    public Claims extractAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    /**
     * Invalide un token (l'ajoute à la liste noire)
     */
    public void invalidateToken(String token) {
        try {
            Claims claims = extractAllClaims(token);
            Date expiration = claims.getExpiration();
            
            // Ajouter à la liste noire avec la date d'expiration
            invalidatedTokens.put(token, expiration);
            
            // Nettoyer les tokens expirés de la liste noire
            cleanupInvalidatedTokens();
            
        } catch (JwtException | IllegalArgumentException e) {
            // Token invalide, pas besoin de l'ajouter à la liste noire
        }
    }

    /**
     * Vérifie si un token est dans la liste noire
     */
    public boolean isTokenInvalidated(String token) {
        Date invalidationDate = invalidatedTokens.get(token);
        if (invalidationDate == null) {
            return false;
        }
        
        // Si le token a expiré, le retirer de la liste noire
        if (new Date().after(invalidationDate)) {
            invalidatedTokens.remove(token);
            return false;
        }
        
        return true;
    }

    /**
     * Nettoie les tokens expirés de la liste noire
     */
    private void cleanupInvalidatedTokens() {
        Date now = new Date();
        invalidatedTokens.entrySet().removeIf(entry -> now.after(entry.getValue()));
    }

    /**
     * Vérifie si un token est expiré
     */
    private boolean isTokenExpired(Claims claims) {
        return claims.getExpiration().before(new Date());
    }

    /**
     * Calcule le temps restant avant expiration d'un token
     */
    public long getTimeUntilExpiration(String token) {
        try {
            Date expiration = extractExpiration(token);
            if (expiration == null) {
                return 0;
            }
            
            long timeUntilExpiration = expiration.getTime() - new Date().getTime();
            return Math.max(0, timeUntilExpiration);
            
        } catch (JwtException | IllegalArgumentException e) {
            return 0;
        }
    }

    /**
     * Vérifie si un token expire bientôt (dans les 5 minutes)
     */
    public boolean isTokenExpiringSoon(String token) {
        long timeUntilExpiration = getTimeUntilExpiration(token);
        return timeUntilExpiration > 0 && timeUntilExpiration < 300000; // 5 minutes
    }

    /**
     * Génère un nouveau token d'accès à partir d'un token de rafraîchissement
     */
    public String generateNewAccessTokenFromRefreshToken(String refreshToken) {
        try {
            if (!validateRefreshToken(refreshToken)) {
                throw new JwtException("Refresh token invalide");
            }

            Claims claims = extractAllClaims(refreshToken);
            
            // Créer un nouveau token d'accès avec les mêmes claims
            Date now = new Date();
            Date expiryDate = new Date(now.getTime() + (accessTokenExpiration * 1000));

            return Jwts.builder()
                    .setClaims(claims)
                    .setIssuedAt(now)
                    .setExpiration(expiryDate)
                    .setId(UUID.randomUUID().toString())
                    .signWith(getSigningKey(), SignatureAlgorithm.HS512)
                    .compact();
                    
        } catch (JwtException | IllegalArgumentException e) {
            throw new RuntimeException("Erreur lors de la génération du nouveau token d'accès", e);
        }
    }

    /**
     * Obtient la clé de signature
     */
    private SecretKey getSigningKey() {
        byte[] keyBytes = jwtSecret.getBytes();
        return Keys.hmacShaKeyFor(keyBytes);
    }

    /**
     * Obtient la durée d'expiration du token d'accès
     */
    public Long getAccessTokenExpiration() {
        return accessTokenExpiration;
    }

    /**
     * Obtient la durée d'expiration du token de rafraîchissement
     */
    public Long getRefreshTokenExpiration() {
        return refreshTokenExpiration;
    }

    /**
     * Obtient la durée d'expiration du token de réinitialisation de mot de passe
     */
    public Long getPasswordResetExpiration() {
        return passwordResetExpiration;
    }

    /**
     * Obtient le nombre de tokens dans la liste noire
     */
    public int getInvalidatedTokensCount() {
        cleanupInvalidatedTokens();
        return invalidatedTokens.size();
    }

    /**
     * Vide la liste noire des tokens
     */
    public void clearInvalidatedTokens() {
        invalidatedTokens.clear();
    }

    /**
     * Obtient les statistiques des tokens
     */
    public Map<String, Object> getTokenStatistics() {
        cleanupInvalidatedTokens();
        
        Map<String, Object> stats = new HashMap<>();
        stats.put("invalidatedTokensCount", invalidatedTokens.size());
        stats.put("accessTokenExpiration", accessTokenExpiration);
        stats.put("refreshTokenExpiration", refreshTokenExpiration);
        stats.put("passwordResetExpiration", passwordResetExpiration);
        stats.put("issuer", issuer);
        
        return stats;
    }
}
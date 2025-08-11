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

/**
 * Service pour la gestion des JWT (JSON Web Tokens)
 */
@Service
public class JwtService {

    @Value("${jwt.secret:default-secret-key-for-development-only}")
    private String jwtSecret;

    @Value("${jwt.access-token.expiration:3600}")
    private Long accessTokenExpiration; // en secondes

    @Value("${jwt.refresh-token.expiration:86400}")
    private Long refreshTokenExpiration; // en secondes

    @Value("${jwt.issuer:banking-transfer-platform}")
    private String issuer;

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(jwtSecret.getBytes());
    }

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
     * Génère un token avec les claims spécifiés
     */
    private String generateToken(User user, Long expirationSeconds, String tokenType) {
        Date now = new Date();
        Date expiration = new Date(now.getTime() + (expirationSeconds * 1000));

        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", user.getId().toString());
        claims.put("username", user.getUsername());
        claims.put("email", user.getEmail());
        claims.put("tokenType", tokenType);
        claims.put("kycStatus", user.getKycStatus().name());
        claims.put("amlStatus", user.getAmlStatus().name());
        claims.put("riskScore", user.getRiskScore());
        claims.put("mfaEnabled", user.getMfaEnabled());

        return Jwts.builder()
                .setClaims(claims)
                .setSubject(user.getUsername())
                .setIssuer(issuer)
                .setIssuedAt(now)
                .setExpiration(expiration)
                .setId(UUID.randomUUID().toString())
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    /**
     * Valide un token JWT
     */
    public boolean validateToken(String token) {
        try {
            Jwts.parserBuilder()
                    .setSigningKey(getSigningKey())
                    .build()
                    .parseClaimsJws(token);
            return true;
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * Extrait les claims d'un token JWT
     */
    public Claims extractClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    /**
     * Extrait l'ID utilisateur d'un token
     */
    public UUID extractUserId(String token) {
        Claims claims = extractClaims(token);
        return UUID.fromString(claims.get("userId", String.class));
    }

    /**
     * Extrait le nom d'utilisateur d'un token
     */
    public String extractUsername(String token) {
        Claims claims = extractClaims(token);
        return claims.getSubject();
    }

    /**
     * Extrait l'email d'un token
     */
    public String extractEmail(String token) {
        Claims claims = extractClaims(token);
        return claims.get("email", String.class);
    }

    /**
     * Extrait le type de token
     */
    public String extractTokenType(String token) {
        Claims claims = extractClaims(token);
        return claims.get("tokenType", String.class);
    }

    /**
     * Extrait le statut KYC d'un token
     */
    public String extractKycStatus(String token) {
        Claims claims = extractClaims(token);
        return claims.get("kycStatus", String.class);
    }

    /**
     * Extrait le statut AML d'un token
     */
    public String extractAmlStatus(String token) {
        Claims claims = extractClaims(token);
        return claims.get("amlStatus", String.class);
    }

    /**
     * Extrait le score de risque d'un token
     */
    public Integer extractRiskScore(String token) {
        Claims claims = extractClaims(token);
        return claims.get("riskScore", Integer.class);
    }

    /**
     * Extrait le statut MFA d'un token
     */
    public Boolean extractMfaEnabled(String token) {
        Claims claims = extractClaims(token);
        return claims.get("mfaEnabled", Boolean.class);
    }

    /**
     * Vérifie si un token est expiré
     */
    public boolean isTokenExpired(String token) {
        try {
            Claims claims = extractClaims(token);
            return claims.getExpiration().before(new Date());
        } catch (JwtException | IllegalArgumentException e) {
            return true;
        }
    }

    /**
     * Obtient la date d'expiration d'un token
     */
    public LocalDateTime getTokenExpiration(String token) {
        try {
            Claims claims = extractClaims(token);
            return claims.getExpiration().toInstant()
                    .atZone(ZoneId.systemDefault())
                    .toLocalDateTime();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Obtient la date d'émission d'un token
     */
    public LocalDateTime getTokenIssuedAt(String token) {
        try {
            Claims claims = extractClaims(token);
            return claims.getIssuedAt().toInstant()
                    .atZone(ZoneId.systemDefault())
                    .toLocalDateTime();
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Obtient le temps restant avant expiration d'un token (en secondes)
     */
    public Long getTokenTimeToExpiry(String token) {
        try {
            Claims claims = extractClaims(token);
            Date expiration = claims.getExpiration();
            Date now = new Date();
            return Math.max(0, (expiration.getTime() - now.getTime()) / 1000);
        } catch (JwtException | IllegalArgumentException e) {
            return 0L;
        }
    }

    /**
     * Vérifie si un token est un token d'accès
     */
    public boolean isAccessToken(String token) {
        try {
            String tokenType = extractTokenType(token);
            return "access".equals(tokenType);
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * Vérifie si un token est un token de rafraîchissement
     */
    public boolean isRefreshToken(String token) {
        try {
            String tokenType = extractTokenType(token);
            return "refresh".equals(tokenType);
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
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
     * Génère un token temporaire pour des opérations spécifiques
     */
    public String generateTemporaryToken(User user, Long expirationSeconds, String purpose) {
        Date now = new Date();
        Date expiration = new Date(now.getTime() + (expirationSeconds * 1000));

        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", user.getId().toString());
        claims.put("username", user.getUsername());
        claims.put("tokenType", "temporary");
        claims.put("purpose", purpose);

        return Jwts.builder()
                .setClaims(claims)
                .setSubject(user.getUsername())
                .setIssuer(issuer)
                .setIssuedAt(now)
                .setExpiration(expiration)
                .setId(UUID.randomUUID().toString())
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    /**
     * Extrait le but d'un token temporaire
     */
    public String extractTokenPurpose(String token) {
        try {
            Claims claims = extractClaims(token);
            return claims.get("purpose", String.class);
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Vérifie si un token est un token temporaire
     */
    public boolean isTemporaryToken(String token) {
        try {
            String tokenType = extractTokenType(token);
            return "temporary".equals(tokenType);
        } catch (JwtException | IllegalArgumentException e) {
            return false;
        }
    }

    /**
     * Génère un token de réinitialisation de mot de passe
     */
    public String generatePasswordResetToken(User user) {
        return generateTemporaryToken(user, 3600L, "password_reset"); // 1 heure
    }

    /**
     * Génère un token de vérification d'email
     */
    public String generateEmailVerificationToken(User user) {
        return generateTemporaryToken(user, 86400L, "email_verification"); // 24 heures
    }

    /**
     * Génère un token de vérification MFA
     */
    public String generateMfaVerificationToken(User user) {
        return generateTemporaryToken(user, 300L, "mfa_verification"); // 5 minutes
    }

    /**
     * Vérifie si un token est un token de réinitialisation de mot de passe
     */
    public boolean isPasswordResetToken(String token) {
        return isTemporaryToken(token) && "password_reset".equals(extractTokenPurpose(token));
    }

    /**
     * Vérifie si un token est un token de vérification d'email
     */
    public boolean isEmailVerificationToken(String token) {
        return isTemporaryToken(token) && "email_verification".equals(extractTokenPurpose(token));
    }

    /**
     * Vérifie si un token est un token de vérification MFA
     */
    public boolean isMfaVerificationToken(String token) {
        return isTemporaryToken(token) && "mfa_verification".equals(extractTokenPurpose(token));
    }
}
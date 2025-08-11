package com.banking.transfers.service;

import com.banking.transfers.model.User;
import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Service pour la gestion des tokens JWT
 */
@Service
public class JwtService {

    private static final Logger logger = LoggerFactory.getLogger(JwtService.class);

    @Value("${jwt.secret:defaultSecretKeyForDevelopmentOnly}")
    private String jwtSecret;

    @Value("${jwt.access-token.expiration:3600}")
    private Long accessTokenExpiration; // 1 heure par défaut

    @Value("${jwt.refresh-token.expiration:86400}")
    private Long refreshTokenExpiration; // 24 heures par défaut

    @Value("${jwt.issuer:banking-transfer-platform}")
    private String jwtIssuer;

    // Cache pour les tokens invalides (blacklist)
    private final Set<String> blacklistedTokens = ConcurrentHashMap.newKeySet();

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
     * Génère un token JWT
     */
    private String generateToken(User user, Long expiration, String tokenType) {
        Map<String, Object> claims = new HashMap<>();
        claims.put("userId", user.getId().toString());
        claims.put("email", user.getEmail());
        claims.put("firstName", user.getFirstName());
        claims.put("lastName", user.getLastName());
        claims.put("roles", user.getRoles());
        claims.put("permissions", user.getPermissions());
        claims.put("kycStatus", user.getKycStatus().name());
        claims.put("amlStatus", user.getAmlStatus().name());
        claims.put("riskScore", user.getRiskScore());
        claims.put("mfaEnabled", user.getMfaEnabled());
        claims.put("tokenType", tokenType);

        return Jwts.builder()
                .setClaims(claims)
                .setSubject(user.getUsername())
                .setIssuer(jwtIssuer)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + expiration * 1000))
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    /**
     * Extrait le nom d'utilisateur depuis un token
     */
    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    /**
     * Extrait l'ID utilisateur depuis un token
     */
    public String extractUserId(String token) {
        return extractClaim(token, claims -> claims.get("userId", String.class));
    }

    /**
     * Extrait l'email depuis un token
     */
    public String extractEmail(String token) {
        return extractClaim(token, claims -> claims.get("email", String.class));
    }

    /**
     * Extrait les rôles depuis un token
     */
    @SuppressWarnings("unchecked")
    public Set<String> extractRoles(String token) {
        return extractClaim(token, claims -> (Set<String>) claims.get("roles"));
    }

    /**
     * Extrait les permissions depuis un token
     */
    @SuppressWarnings("unchecked")
    public Set<String> extractPermissions(String token) {
        return extractClaim(token, claims -> (Set<String>) claims.get("permissions"));
    }

    /**
     * Extrait le type de token depuis un token
     */
    public String extractTokenType(String token) {
        return extractClaim(token, claims -> claims.get("tokenType", String.class));
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
    public <T> T extractClaim(String token, java.util.function.Function<Claims, T> claimsResolver) {
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
    public boolean isTokenExpired(String token) {
        try {
            Date expiration = extractExpiration(token);
            return expiration.before(new Date());
        } catch (Exception e) {
            logger.warn("Erreur lors de la vérification d'expiration du token: {}", e.getMessage());
            return true;
        }
    }

    /**
     * Vérifie si un token est valide pour un utilisateur
     */
    public boolean isTokenValid(String token, UserDetails userDetails) {
        try {
            final String username = extractUsername(token);
            return (username.equals(userDetails.getUsername()) && !isTokenExpired(token) && !isTokenBlacklisted(token));
        } catch (Exception e) {
            logger.warn("Erreur lors de la validation du token: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Vérifie si un token est valide pour un utilisateur
     */
    public boolean isTokenValid(String token, User user) {
        try {
            final String username = extractUsername(token);
            return (username.equals(user.getUsername()) && !isTokenExpired(token) && !isTokenBlacklisted(token));
        } catch (Exception e) {
            logger.warn("Erreur lors de la validation du token: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Vérifie si un token est valide (sans vérifier l'utilisateur)
     */
    public boolean isTokenValid(String token) {
        try {
            return !isTokenExpired(token) && !isTokenBlacklisted(token);
        } catch (Exception e) {
            logger.warn("Erreur lors de la validation du token: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Vérifie si un token est dans la liste noire
     */
    public boolean isTokenBlacklisted(String token) {
        return blacklistedTokens.contains(token);
    }

    /**
     * Invalide un token (l'ajoute à la liste noire)
     */
    public void invalidateToken(String token) {
        if (token != null && !token.trim().isEmpty()) {
            blacklistedTokens.add(token);
            logger.info("Token ajouté à la liste noire");
        }
    }

    /**
     * Nettoie les tokens expirés de la liste noire
     */
    public void cleanupExpiredTokens() {
        blacklistedTokens.removeIf(token -> {
            try {
                return isTokenExpired(token);
            } catch (Exception e) {
                logger.warn("Erreur lors du nettoyage du token: {}", e.getMessage());
                return true; // Supprimer le token en cas d'erreur
            }
        });
        logger.info("Nettoyage des tokens expirés terminé. {} tokens restants dans la liste noire", blacklistedTokens.size());
    }

    /**
     * Obtient la clé de signature pour les tokens
     */
    private SecretKey getSigningKey() {
        byte[] keyBytes = jwtSecret.getBytes(StandardCharsets.UTF_8);
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
     * Vérifie si un token est un token d'accès
     */
    public boolean isAccessToken(String token) {
        try {
            String tokenType = extractTokenType(token);
            return "access".equals(tokenType);
        } catch (Exception e) {
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
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Extrait les informations de sécurité depuis un token
     */
    public SecurityInfo extractSecurityInfo(String token) {
        try {
            Claims claims = extractAllClaims(token);
            return SecurityInfo.builder()
                    .userId(claims.get("userId", String.class))
                    .username(claims.getSubject())
                    .email(claims.get("email", String.class))
                    .roles((Set<String>) claims.get("roles"))
                    .permissions((Set<String>) claims.get("permissions"))
                    .kycStatus(claims.get("kycStatus", String.class))
                    .amlStatus(claims.get("amlStatus", String.class))
                    .riskScore(claims.get("riskScore", Integer.class))
                    .mfaEnabled(claims.get("mfaEnabled", Boolean.class))
                    .tokenType(claims.get("tokenType", String.class))
                    .issuedAt(claims.getIssuedAt())
                    .expiresAt(claims.getExpiration())
                    .build();
        } catch (Exception e) {
            logger.warn("Erreur lors de l'extraction des informations de sécurité: {}", e.getMessage());
            return null;
        }
    }

    /**
     * Classe pour encapsuler les informations de sécurité extraites d'un token
     */
    public static class SecurityInfo {
        private String userId;
        private String username;
        private String email;
        private Set<String> roles;
        private Set<String> permissions;
        private String kycStatus;
        private String amlStatus;
        private Integer riskScore;
        private Boolean mfaEnabled;
        private String tokenType;
        private Date issuedAt;
        private Date expiresAt;

        private SecurityInfo() {}

        public static Builder builder() {
            return new Builder();
        }

        // Getters
        public String getUserId() { return userId; }
        public String getUsername() { return username; }
        public String getEmail() { return email; }
        public Set<String> getRoles() { return roles; }
        public Set<String> getPermissions() { return permissions; }
        public String getKycStatus() { return kycStatus; }
        public String getAmlStatus() { return amlStatus; }
        public Integer getRiskScore() { return riskScore; }
        public Boolean getMfaEnabled() { return mfaEnabled; }
        public String getTokenType() { return tokenType; }
        public Date getIssuedAt() { return issuedAt; }
        public Date getExpiresAt() { return expiresAt; }

        // Builder
        public static class Builder {
            private SecurityInfo info = new SecurityInfo();

            public Builder userId(String userId) {
                info.userId = userId;
                return this;
            }

            public Builder username(String username) {
                info.username = username;
                return this;
            }

            public Builder email(String email) {
                info.email = email;
                return this;
            }

            public Builder roles(Set<String> roles) {
                info.roles = roles;
                return this;
            }

            public Builder permissions(Set<String> permissions) {
                info.permissions = permissions;
                return this;
            }

            public Builder kycStatus(String kycStatus) {
                info.kycStatus = kycStatus;
                return this;
            }

            public Builder amlStatus(String amlStatus) {
                info.amlStatus = amlStatus;
                return this;
            }

            public Builder riskScore(Integer riskScore) {
                info.riskScore = riskScore;
                return this;
            }

            public Builder mfaEnabled(Boolean mfaEnabled) {
                info.mfaEnabled = mfaEnabled;
                return this;
            }

            public Builder tokenType(String tokenType) {
                info.tokenType = tokenType;
                return this;
            }

            public Builder issuedAt(Date issuedAt) {
                info.issuedAt = issuedAt;
                return this;
            }

            public Builder expiresAt(Date expiresAt) {
                info.expiresAt = expiresAt;
                return this;
            }

            public SecurityInfo build() {
                return info;
            }
        }
    }
}
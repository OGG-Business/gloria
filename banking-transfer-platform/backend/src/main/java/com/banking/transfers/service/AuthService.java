package com.banking.transfers.service;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.model.User;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.RiskLevel;
import com.banking.transfers.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.LockedException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Service d'authentification et d'autorisation
 */
@Service
@Transactional
public class AuthService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AuthenticationManager authenticationManager;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Value("${jwt.secret}")
    private String jwtSecret;

    @Value("${jwt.expiration}")
    private long jwtExpiration;

    @Autowired
    private KeycloakService keycloakService;

    @Autowired
    private MfaService mfaService;

    @Autowired
    private AuditService auditService;

    // Cache des sessions actives (en production, utiliser Redis)
    private final Map<String, UserSession> activeSessions = new ConcurrentHashMap<>();

    // Configuration
    private static final int MAX_FAILED_LOGIN_ATTEMPTS = 5;
    private static final int SESSION_TIMEOUT_MINUTES = 30;
    private static final int REFRESH_TOKEN_TIMEOUT_DAYS = 7;

    /**
     * Authentification d'un utilisateur
     */
    public LoginResponse login(LoginRequest request, String clientIp, String userAgent) {
        try {
            // Validation des paramètres
            validateLoginRequest(request);

            // Recherche de l'utilisateur
            User user = findUserByUsernameOrEmail(request.getUsernameOrEmail());
            if (user == null) {
                throw new BadCredentialsException("Identifiants invalides");
            }

            // Vérification du statut du compte
            validateUserAccountStatus(user);

            // Tentative d'authentification
            Authentication authentication = authenticateUser(request, user);

            // Vérification MFA si nécessaire
            if (user.getMfaEnabled() && request.getMfaCode() == null) {
                return createMfaRequiredResponse(user);
            }

            if (user.getMfaEnabled() && request.getMfaCode() != null) {
                validateMfaCode(user, request.getMfaCode());
            }

            // Mise à jour des informations de connexion
            updateUserLoginInfo(user, clientIp, userAgent);

            // Génération des tokens
            String accessToken = generateAccessToken(user);
            String refreshToken = generateRefreshToken(user);

            // Création de la session
            UserSession session = createUserSession(user, accessToken, clientIp, userAgent);
            activeSessions.put(session.getSessionId(), session);

            // Audit
            auditService.logLoginSuccess(user.getId(), clientIp, userAgent);

            // Construction de la réponse
            return buildLoginResponse(user, accessToken, refreshToken, session);

        } catch (BadCredentialsException e) {
            handleFailedLogin(request.getUsernameOrEmail(), clientIp, userAgent);
            throw e;
        } catch (LockedException e) {
            auditService.logLoginFailed(request.getUsernameOrEmail(), "Account locked", clientIp, userAgent);
            throw e;
        } catch (Exception e) {
            auditService.logLoginFailed(request.getUsernameOrEmail(), e.getMessage(), clientIp, userAgent);
            throw new RuntimeException("Erreur lors de la connexion", e);
        }
    }

    /**
     * Déconnexion d'un utilisateur
     */
    public void logout(String accessToken, String clientIp) {
        try {
            // Validation du token
            Claims claims = parseAccessToken(accessToken);
            if (claims == null) {
                return;
            }

            // Récupération de l'utilisateur
            String userId = claims.getSubject();
            User user = userRepository.findById(UUID.fromString(userId)).orElse(null);
            if (user == null) {
                return;
            }

            // Suppression de la session
            String sessionId = claims.get("sessionId", String.class);
            if (sessionId != null) {
                activeSessions.remove(sessionId);
            }

            // Invalidation du token dans Keycloak si nécessaire
            if (user.getKeycloakId() != null) {
                keycloakService.logout(user.getKeycloakId());
            }

            // Audit
            auditService.logLogout(user.getId(), clientIp);

        } catch (Exception e) {
            // Log de l'erreur mais ne pas la propager
            auditService.logError("LOGOUT_ERROR", e.getMessage(), clientIp);
        }
    }

    /**
     * Rafraîchissement d'un token
     */
    public LoginResponse refreshToken(String refreshToken, String clientIp) {
        try {
            // Validation du refresh token
            Claims claims = parseRefreshToken(refreshToken);
            if (claims == null) {
                throw new BadCredentialsException("Refresh token invalide");
            }

            // Récupération de l'utilisateur
            String userId = claims.getSubject();
            User user = userRepository.findById(UUID.fromString(userId)).orElse(null);
            if (user == null) {
                throw new BadCredentialsException("Utilisateur non trouvé");
            }

            // Vérification du statut du compte
            validateUserAccountStatus(user);

            // Génération d'un nouveau access token
            String newAccessToken = generateAccessToken(user);

            // Mise à jour de la session
            String sessionId = claims.get("sessionId", String.class);
            UserSession session = activeSessions.get(sessionId);
            if (session != null) {
                session.setAccessToken(newAccessToken);
                session.setLastActivity(LocalDateTime.now());
            }

            // Audit
            auditService.logTokenRefresh(user.getId(), clientIp);

            // Construction de la réponse
            return buildLoginResponse(user, newAccessToken, refreshToken, session);

        } catch (Exception e) {
            auditService.logError("TOKEN_REFRESH_ERROR", e.getMessage(), clientIp);
            throw new RuntimeException("Erreur lors du rafraîchissement du token", e);
        }
    }

    /**
     * Validation d'un token d'accès
     */
    public User validateAccessToken(String accessToken) {
        try {
            Claims claims = parseAccessToken(accessToken);
            if (claims == null) {
                return null;
            }

            String userId = claims.getSubject();
            User user = userRepository.findById(UUID.fromString(userId)).orElse(null);
            if (user == null) {
                return null;
            }

            // Vérification du statut du compte
            if (!user.getIsActive() || user.getIsLocked()) {
                return null;
            }

            // Vérification de la session
            String sessionId = claims.get("sessionId", String.class);
            UserSession session = activeSessions.get(sessionId);
            if (session == null || session.isExpired()) {
                return null;
            }

            // Mise à jour de l'activité de la session
            session.setLastActivity(LocalDateTime.now());

            return user;

        } catch (Exception e) {
            return null;
        }
    }

    /**
     * Obtention de l'utilisateur actuel
     */
    public User getCurrentUser() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication == null || !authentication.isAuthenticated()) {
            return null;
        }

        String username = authentication.getName();
        return userRepository.findByUsername(username).orElse(null);
    }

    /**
     * Vérification des permissions
     */
    public boolean hasPermission(String permission) {
        User user = getCurrentUser();
        if (user == null) {
            return false;
        }

        // Vérification des permissions via Keycloak
        if (user.getKeycloakId() != null) {
            return keycloakService.hasPermission(user.getKeycloakId(), permission);
        }

        // Vérification locale des permissions
        return checkLocalPermissions(user, permission);
    }

    /**
     * Vérification des rôles
     */
    public boolean hasRole(String role) {
        User user = getCurrentUser();
        if (user == null) {
            return false;
        }

        // Vérification des rôles via Keycloak
        if (user.getKeycloakId() != null) {
            return keycloakService.hasRole(user.getKeycloakId(), role);
        }

        // Vérification locale des rôles
        return checkLocalRoles(user, role);
    }

    /**
     * Changement de mot de passe
     */
    public void changePassword(String currentPassword, String newPassword, String clientIp) {
        User user = getCurrentUser();
        if (user == null) {
            throw new RuntimeException("Utilisateur non authentifié");
        }

        // Vérification de l'ancien mot de passe
        if (!passwordEncoder.matches(currentPassword, user.getPasswordHash())) {
            throw new BadCredentialsException("Mot de passe actuel incorrect");
        }

        // Validation du nouveau mot de passe
        validatePassword(newPassword);

        // Mise à jour du mot de passe
        user.setPasswordHash(passwordEncoder.encode(newPassword));
        user.setPasswordChangedDate(LocalDateTime.now());
        userRepository.save(user);

        // Invalidation des sessions existantes
        invalidateUserSessions(user.getId());

        // Audit
        auditService.logPasswordChange(user.getId(), clientIp);
    }

    /**
     * Activation/désactivation de MFA
     */
    public void toggleMfa(String mfaCode, String clientIp) {
        User user = getCurrentUser();
        if (user == null) {
            throw new RuntimeException("Utilisateur non authentifié");
        }

        if (user.getMfaEnabled()) {
            // Désactivation de MFA
            validateMfaCode(user, mfaCode);
            user.setMfaEnabled(false);
            user.setMfaSecret(null);
            auditService.logMfaDisable(user.getId(), clientIp);
        } else {
            // Activation de MFA
            String secret = mfaService.generateSecret();
            user.setMfaSecret(secret);
            user.setMfaEnabled(true);
            auditService.logMfaEnable(user.getId(), clientIp);
        }

        userRepository.save(user);
    }

    /**
     * Génération d'un QR code pour MFA
     */
    public String generateMfaQrCode() {
        User user = getCurrentUser();
        if (user == null) {
            throw new RuntimeException("Utilisateur non authentifié");
        }

        if (user.getMfaSecret() == null) {
            throw new RuntimeException("MFA non configuré");
        }

        return mfaService.generateQrCode(user.getMfaSecret(), user.getEmail());
    }

    // Méthodes privées

    private void validateLoginRequest(LoginRequest request) {
        if (request.getUsernameOrEmail() == null || request.getUsernameOrEmail().trim().isEmpty()) {
            throw new IllegalArgumentException("Nom d'utilisateur ou email requis");
        }
        if (request.getPassword() == null || request.getPassword().trim().isEmpty()) {
            throw new IllegalArgumentException("Mot de passe requis");
        }
    }

    private User findUserByUsernameOrEmail(String usernameOrEmail) {
        return userRepository.findByUsernameOrEmail(usernameOrEmail, usernameOrEmail).orElse(null);
    }

    private void validateUserAccountStatus(User user) {
        if (!user.getIsActive()) {
            throw new LockedException("Compte désactivé");
        }
        if (user.getIsLocked()) {
            throw new LockedException("Compte verrouillé");
        }
        if (!user.canLogin()) {
            throw new LockedException("Compte non autorisé à se connecter");
        }
    }

    private Authentication authenticateUser(LoginRequest request, User user) {
        UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                user.getUsername(),
                request.getPassword()
        );

        return authenticationManager.authenticate(authToken);
    }

    private LoginResponse createMfaRequiredResponse(User user) {
        LoginResponse response = new LoginResponse();
        response.setUserId(user.getId());
        response.setUsername(user.getUsername());
        response.setMfaRequired(true);
        response.setMfaType("TOTP");
        response.setMessage("Code MFA requis");
        return response;
    }

    private void validateMfaCode(User user, String mfaCode) {
        if (!mfaService.validateCode(user.getMfaSecret(), mfaCode)) {
            throw new BadCredentialsException("Code MFA invalide");
        }
    }

    private void updateUserLoginInfo(User user, String clientIp, String userAgent) {
        user.updateLastLogin();
        userRepository.save(user);
    }

    private String generateAccessToken(User user) {
        // Génération via Keycloak si configuré
        if (user.getKeycloakId() != null) {
            return keycloakService.generateAccessToken(user.getKeycloakId());
        }

        // Génération locale
        return generateLocalAccessToken(user);
    }

    private String generateRefreshToken(User user) {
        // Génération via Keycloak si configuré
        if (user.getKeycloakId() != null) {
            return keycloakService.generateRefreshToken(user.getKeycloakId());
        }

        // Génération locale
        return generateLocalRefreshToken(user);
    }

    private String generateLocalAccessToken(User user) {
        // Implémentation locale de génération de JWT
        // À implémenter selon les besoins
        return "local_access_token_" + user.getId();
    }

    private String generateLocalRefreshToken(User user) {
        // Implémentation locale de génération de refresh token
        // À implémenter selon les besoins
        return "local_refresh_token_" + user.getId();
    }

    private UserSession createUserSession(User user, String accessToken, String clientIp, String userAgent) {
        String sessionId = UUID.randomUUID().toString();
        return new UserSession(
                sessionId,
                user.getId(),
                accessToken,
                LocalDateTime.now(),
                LocalDateTime.now().plusMinutes(SESSION_TIMEOUT_MINUTES),
                clientIp,
                userAgent
        );
    }

    private LoginResponse buildLoginResponse(User user, String accessToken, String refreshToken, UserSession session) {
        LoginResponse response = new LoginResponse(accessToken, refreshToken, user.getId(), user.getUsername());
        
        // Informations utilisateur
        response.setEmail(user.getEmail());
        response.setFirstName(user.getFirstName());
        response.setLastName(user.getLastName());
        response.setFullName(user.getFullName());
        response.setPhone(user.getPhone());
        response.setNationality(user.getNationality());
        response.setCountry(user.getCountry());

        // Statuts de conformité
        response.setKycStatus(user.getKycStatus());
        response.setAmlStatus(user.getAmlStatus());
        response.setRiskLevel(user.getRiskLevel());
        response.setRiskScore(user.getRiskScore());

        // Configuration MFA
        response.setMfaEnabled(user.getMfaEnabled());
        response.setMfaType("TOTP");

        // Informations de session
        response.setSessionId(session.getSessionId());
        response.setLastLoginDate(user.getLastLoginDate());
        response.setFailedLoginAttempts(user.getFailedLoginAttempts());
        response.setIsLocked(user.getIsLocked());
        response.setIsActive(user.getIsActive());

        // Configuration des tokens
        response.setExpiresIn(30L * 60L); // 30 minutes
        response.setExpiresAt(LocalDateTime.now().plusMinutes(30));

        // Rôles et permissions
        response.setRoles(getUserRoles(user));
        response.setPermissions(getUserPermissions(user));

        // Messages et avertissements
        setResponseMessages(response, user);

        return response;
    }

    private void handleFailedLogin(String usernameOrEmail, String clientIp, String userAgent) {
        User user = findUserByUsernameOrEmail(usernameOrEmail);
        if (user != null) {
            user.incrementFailedLoginAttempts();
            userRepository.save(user);
            auditService.logLoginFailed(usernameOrEmail, "Bad credentials", clientIp, userAgent);
        }
    }

    private Claims parseAccessToken(String accessToken) {
        try {
            return Jwts.parser()
                    .setSigningKey(Keys.hmacShaKeyFor(jwtSecret.getBytes()))
                    .parseClaimsJws(accessToken)
                    .getBody();
        } catch (Exception e) {
            return null;
        }
    }

    private Claims parseRefreshToken(String refreshToken) {
        try {
            return Jwts.parser()
                    .setSigningKey(Keys.hmacShaKeyFor(jwtSecret.getBytes()))
                    .parseClaimsJws(refreshToken)
                    .getBody();
        } catch (Exception e) {
            return null;
        }
    }

    private void validatePassword(String password) {
        if (password == null || password.length() < 8) {
            throw new IllegalArgumentException("Le mot de passe doit contenir au moins 8 caractères");
        }
        // Ajouter d'autres validations selon les politiques de sécurité
    }

    private void invalidateUserSessions(UUID userId) {
        activeSessions.entrySet().removeIf(entry -> entry.getValue().getUserId().equals(userId));
    }

    private boolean checkLocalPermissions(User user, String permission) {
        // Implémentation locale des permissions
        // À adapter selon les besoins
        return true;
    }

    private boolean checkLocalRoles(User user, String role) {
        // Implémentation locale des rôles
        // À adapter selon les besoins
        return true;
    }

    private List<String> getUserRoles(User user) {
        // Récupération des rôles via Keycloak ou localement
        if (user.getKeycloakId() != null) {
            return keycloakService.getUserRoles(user.getKeycloakId());
        }
        return Arrays.asList("USER");
    }

    private List<String> getUserPermissions(User user) {
        // Récupération des permissions via Keycloak ou localement
        if (user.getKeycloakId() != null) {
            return keycloakService.getUserPermissions(user.getKeycloakId());
        }
        return Arrays.asList("READ", "WRITE");
    }

    private void setResponseMessages(LoginResponse response, User user) {
        List<String> warnings = new ArrayList<>();
        List<String> requiredActions = new ArrayList<>();

        if (user.requiresKYC()) {
            warnings.add("Vérification KYC requise");
            requiredActions.add("COMPLETE_KYC");
        }

        if (user.requiresAML()) {
            warnings.add("Vérification AML requise");
            requiredActions.add("COMPLETE_AML");
        }

        if (user.isHighRisk()) {
            warnings.add("Compte à risque élevé - surveillance renforcée");
        }

        if (user.getFailedLoginAttempts() > 0) {
            warnings.add("Échecs de connexion précédents détectés");
        }

        response.setWarnings(warnings);
        response.setRequiredActions(requiredActions);
    }

    // Classe interne pour représenter une session utilisateur
    private static class UserSession {
        private final String sessionId;
        private final UUID userId;
        private String accessToken;
        private final LocalDateTime createdAt;
        private final LocalDateTime expiresAt;
        private LocalDateTime lastActivity;
        private final String clientIp;
        private final String userAgent;

        public UserSession(String sessionId, UUID userId, String accessToken, 
                          LocalDateTime createdAt, LocalDateTime expiresAt, 
                          String clientIp, String userAgent) {
            this.sessionId = sessionId;
            this.userId = userId;
            this.accessToken = accessToken;
            this.createdAt = createdAt;
            this.expiresAt = expiresAt;
            this.lastActivity = createdAt;
            this.clientIp = clientIp;
            this.userAgent = userAgent;
        }

        public boolean isExpired() {
            return LocalDateTime.now().isAfter(expiresAt);
        }

        // Getters et setters
        public String getSessionId() { return sessionId; }
        public UUID getUserId() { return userId; }
        public String getAccessToken() { return accessToken; }
        public void setAccessToken(String accessToken) { this.accessToken = accessToken; }
        public LocalDateTime getCreatedAt() { return createdAt; }
        public LocalDateTime getExpiresAt() { return expiresAt; }
        public LocalDateTime getLastActivity() { return lastActivity; }
        public void setLastActivity(LocalDateTime lastActivity) { this.lastActivity = lastActivity; }
        public String getClientIp() { return clientIp; }
        public String getUserAgent() { return userAgent; }
    }
}
package com.banking.transfers.controller;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.service.AuthService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.UUID;

/**
 * Contrôleur pour l'authentification
 */
@RestController
@RequestMapping("/api/v1/auth")
@Tag(name = "Authentication", description = "Endpoints d'authentification")
@CrossOrigin(origins = "*", maxAge = 3600)
public class AuthController {
    
    private static final Logger logger = LoggerFactory.getLogger(AuthController.class);
    
    @Autowired
    private AuthService authService;
    
    /**
     * Endpoint de connexion
     */
    @PostMapping("/login")
    @Operation(
        summary = "Authentifier un utilisateur",
        description = "Authentifie un utilisateur avec son nom d'utilisateur/email et mot de passe"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Authentification réussie",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Données de connexion invalides"
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Identifiants invalides"
        ),
        @ApiResponse(
            responseCode = "423",
            description = "Compte verrouillé"
        ),
        @ApiResponse(
            responseCode = "429",
            description = "Trop de tentatives de connexion"
        ),
        @ApiResponse(
            responseCode = "500",
            description = "Erreur interne du serveur"
        )
    })
    public ResponseEntity<LoginResponse> login(
            @Valid @RequestBody LoginRequest loginRequest,
            HttpServletRequest request) {
        
        logger.info("Tentative de connexion depuis l'IP: {}", getClientIpAddress(request));
        
        try {
            LoginResponse response = authService.authenticate(loginRequest);
            
            if (response.isSuccess()) {
                logger.info("Connexion réussie pour l'utilisateur: {}", response.getUsername());
                return ResponseEntity.ok(response);
            } else if (response.isMfaRequired()) {
                logger.info("MFA requis pour l'utilisateur: {}", response.getUsername());
                return ResponseEntity.status(HttpStatus.MULTI_STATUS).body(response);
            } else {
                logger.warn("Échec de connexion: {}", response.getError());
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
        } catch (Exception e) {
            logger.error("Erreur lors de la connexion", e);
            LoginResponse errorResponse = new LoginResponse();
            errorResponse.setError("server_error");
            errorResponse.setErrorDescription("Erreur interne du serveur");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Endpoint de connexion avec MFA
     */
    @PostMapping("/login/mfa")
    @Operation(
        summary = "Authentifier avec MFA",
        description = "Authentifie un utilisateur avec un code MFA"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Authentification MFA réussie",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Code MFA invalide"
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Authentification échouée"
        )
    })
    public ResponseEntity<LoginResponse> loginWithMfa(
            @Valid @RequestBody LoginRequest loginRequest,
            HttpServletRequest request) {
        
        logger.info("Tentative de connexion MFA depuis l'IP: {}", getClientIpAddress(request));
        
        try {
            LoginResponse response = authService.authenticateWithMfa(loginRequest);
            
            if (response.isSuccess()) {
                logger.info("Connexion MFA réussie pour l'utilisateur: {}", response.getUsername());
                return ResponseEntity.ok(response);
            } else {
                logger.warn("Échec de connexion MFA: {}", response.getError());
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
        } catch (Exception e) {
            logger.error("Erreur lors de la connexion MFA", e);
            LoginResponse errorResponse = new LoginResponse();
            errorResponse.setError("server_error");
            errorResponse.setErrorDescription("Erreur interne du serveur");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Endpoint de rafraîchissement de token
     */
    @PostMapping("/refresh")
    @Operation(
        summary = "Rafraîchir un token d'accès",
        description = "Rafraîchit un token d'accès expiré avec un refresh token"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Token rafraîchi avec succès",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Refresh token invalide"
        )
    })
    public ResponseEntity<LoginResponse> refreshToken(
            @RequestParam String refreshToken,
            HttpServletRequest request) {
        
        logger.info("Tentative de rafraîchissement de token depuis l'IP: {}", getClientIpAddress(request));
        
        try {
            LoginResponse response = authService.refreshToken(refreshToken);
            
            if (response.isSuccess()) {
                logger.info("Token rafraîchi avec succès pour l'utilisateur: {}", response.getUsername());
                return ResponseEntity.ok(response);
            } else {
                logger.warn("Échec du rafraîchissement de token: {}", response.getError());
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(response);
            }
            
        } catch (Exception e) {
            logger.error("Erreur lors du rafraîchissement de token", e);
            LoginResponse errorResponse = new LoginResponse();
            errorResponse.setError("server_error");
            errorResponse.setErrorDescription("Erreur interne du serveur");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse);
        }
    }
    
    /**
     * Endpoint de déconnexion
     */
    @PostMapping("/logout")
    @Operation(
        summary = "Déconnecter un utilisateur",
        description = "Déconnecte un utilisateur et révoque ses tokens"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Déconnexion réussie"
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Token invalide"
        )
    })
    public ResponseEntity<Map<String, String>> logout(
            @RequestHeader("Authorization") String authorizationHeader,
            HttpServletRequest request) {
        
        logger.info("Tentative de déconnexion depuis l'IP: {}", getClientIpAddress(request));
        
        try {
            String token = extractTokenFromHeader(authorizationHeader);
            if (token != null) {
                authService.logout(token);
                logger.info("Déconnexion réussie");
                return ResponseEntity.ok(Map.of("message", "Déconnexion réussie"));
            } else {
                logger.warn("Token d'autorisation manquant");
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("error", "Token d'autorisation manquant"));
            }
            
        } catch (Exception e) {
            logger.error("Erreur lors de la déconnexion", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint de validation de token
     */
    @GetMapping("/validate")
    @Operation(
        summary = "Valider un token d'accès",
        description = "Valide un token d'accès et retourne les informations de l'utilisateur"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Token valide",
            content = @Content(schema = @Schema(implementation = Map.class))
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Token invalide"
        )
    })
    public ResponseEntity<Map<String, Object>> validateToken(
            @RequestHeader("Authorization") String authorizationHeader,
            HttpServletRequest request) {
        
        logger.info("Validation de token depuis l'IP: {}", getClientIpAddress(request));
        
        try {
            String token = extractTokenFromHeader(authorizationHeader);
            if (token == null) {
                return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                        .body(Map.of("valid", false, "error", "Token manquant"));
            }
            
            boolean isValid = authService.validateToken(token);
            if (isValid) {
                var userOpt = authService.getUserFromToken(token);
                if (userOpt.isPresent()) {
                    var user = userOpt.get();
                    Map<String, Object> response = Map.of(
                        "valid", true,
                        "userId", user.getId(),
                        "username", user.getUsername(),
                        "email", user.getEmail(),
                        "roles", authService.getUserRoles(user),
                        "permissions", authService.getUserPermissions(user),
                        "kycStatus", user.getKycStatus(),
                        "amlStatus", user.getAmlStatus(),
                        "riskScore", user.getRiskScore()
                    );
                    return ResponseEntity.ok(response);
                }
            }
            
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED)
                    .body(Map.of("valid", false, "error", "Token invalide"));
            
        } catch (Exception e) {
            logger.error("Erreur lors de la validation du token", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("valid", false, "error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint de révocation de token
     */
    @PostMapping("/revoke")
    @Operation(
        summary = "Révoquer un token",
        description = "Révoque un token d'accès ou de rafraîchissement"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Token révoqué avec succès"
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Token manquant"
        )
    })
    public ResponseEntity<Map<String, String>> revokeToken(
            @RequestParam String token,
            HttpServletRequest request) {
        
        logger.info("Révocation de token depuis l'IP: {}", getClientIpAddress(request));
        
        try {
            authService.revokeToken(token);
            logger.info("Token révoqué avec succès");
            return ResponseEntity.ok(Map.of("message", "Token révoqué avec succès"));
            
        } catch (Exception e) {
            logger.error("Erreur lors de la révocation du token", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint pour obtenir les informations de session
     */
    @GetMapping("/session/{sessionId}")
    @Operation(
        summary = "Obtenir les informations de session",
        description = "Récupère les informations d'une session utilisateur"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Informations de session récupérées",
            content = @Content(schema = @Schema(implementation = Map.class))
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Session non trouvée"
        )
    })
    public ResponseEntity<Map<String, Object>> getSessionInfo(
            @Parameter(description = "ID de la session") @PathVariable String sessionId,
            HttpServletRequest request) {
        
        logger.info("Récupération des informations de session {} depuis l'IP: {}", 
                   sessionId, getClientIpAddress(request));
        
        try {
            boolean isValid = authService.validateSession(sessionId);
            if (isValid) {
                Map<String, Object> sessionInfo = authService.getSessionInfo(sessionId);
                return ResponseEntity.ok(sessionInfo);
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Session non trouvée ou expirée"));
            }
            
        } catch (Exception e) {
            logger.error("Erreur lors de la récupération des informations de session", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint pour renouveler une session
     */
    @PostMapping("/session/{sessionId}/renew")
    @Operation(
        summary = "Renouveler une session",
        description = "Renouvelle une session utilisateur"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Session renouvelée avec succès"
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Session non trouvée"
        )
    })
    public ResponseEntity<Map<String, String>> renewSession(
            @Parameter(description = "ID de la session") @PathVariable String sessionId,
            HttpServletRequest request) {
        
        logger.info("Renouvellement de session {} depuis l'IP: {}", 
                   sessionId, getClientIpAddress(request));
        
        try {
            boolean isValid = authService.validateSession(sessionId);
            if (isValid) {
                authService.renewSession(sessionId);
                return ResponseEntity.ok(Map.of("message", "Session renouvelée avec succès"));
            } else {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Session non trouvée ou expirée"));
            }
            
        } catch (Exception e) {
            logger.error("Erreur lors du renouvellement de session", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint pour supprimer une session
     */
    @DeleteMapping("/session/{sessionId}")
    @Operation(
        summary = "Supprimer une session",
        description = "Supprime une session utilisateur"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Session supprimée avec succès"
        ),
        @ApiResponse(
            responseCode = "404",
            description = "Session non trouvée"
        )
    })
    public ResponseEntity<Map<String, String>> removeSession(
            @Parameter(description = "ID de la session") @PathVariable String sessionId,
            HttpServletRequest request) {
        
        logger.info("Suppression de session {} depuis l'IP: {}", 
                   sessionId, getClientIpAddress(request));
        
        try {
            authService.removeSession(sessionId);
            return ResponseEntity.ok(Map.of("message", "Session supprimée avec succès"));
            
        } catch (Exception e) {
            logger.error("Erreur lors de la suppression de session", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint pour obtenir les sessions actives d'un utilisateur
     */
    @GetMapping("/user/{userId}/sessions")
    @Operation(
        summary = "Obtenir les sessions actives d'un utilisateur",
        description = "Récupère toutes les sessions actives d'un utilisateur"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Sessions récupérées avec succès",
            content = @Content(schema = @Schema(implementation = Map.class))
        ),
        @ApiResponse(
            responseCode = "403",
            description = "Accès non autorisé"
        )
    })
    public ResponseEntity<Map<String, Object>> getUserSessions(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            HttpServletRequest request) {
        
        logger.info("Récupération des sessions de l'utilisateur {} depuis l'IP: {}", 
                   userId, getClientIpAddress(request));
        
        try {
            // Vérifier l'autorisation (l'utilisateur ne peut voir que ses propres sessions)
            String token = extractTokenFromHeader(request.getHeader("Authorization"));
            if (token != null) {
                var currentUserOpt = authService.getUserFromToken(token);
                if (currentUserOpt.isPresent() && currentUserOpt.get().getId().equals(userId)) {
                    var sessions = authService.getUserActiveSessions(userId);
                    return ResponseEntity.ok(Map.of("sessions", sessions));
                }
            }
            
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Accès non autorisé"));
            
        } catch (Exception e) {
            logger.error("Erreur lors de la récupération des sessions utilisateur", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint pour supprimer toutes les sessions d'un utilisateur
     */
    @DeleteMapping("/user/{userId}/sessions")
    @Operation(
        summary = "Supprimer toutes les sessions d'un utilisateur",
        description = "Supprime toutes les sessions actives d'un utilisateur"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Sessions supprimées avec succès"
        ),
        @ApiResponse(
            responseCode = "403",
            description = "Accès non autorisé"
        )
    })
    public ResponseEntity<Map<String, String>> removeAllUserSessions(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            HttpServletRequest request) {
        
        logger.info("Suppression de toutes les sessions de l'utilisateur {} depuis l'IP: {}", 
                   userId, getClientIpAddress(request));
        
        try {
            // Vérifier l'autorisation
            String token = extractTokenFromHeader(request.getHeader("Authorization"));
            if (token != null) {
                var currentUserOpt = authService.getUserFromToken(token);
                if (currentUserOpt.isPresent() && currentUserOpt.get().getId().equals(userId)) {
                    authService.removeAllUserSessions(userId);
                    return ResponseEntity.ok(Map.of("message", "Toutes les sessions supprimées avec succès"));
                }
            }
            
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Accès non autorisé"));
            
        } catch (Exception e) {
            logger.error("Erreur lors de la suppression des sessions utilisateur", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint pour obtenir les statistiques d'authentification
     */
    @GetMapping("/statistics")
    @Operation(
        summary = "Obtenir les statistiques d'authentification",
        description = "Récupère les statistiques d'authentification (admin seulement)"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Statistiques récupérées avec succès",
            content = @Content(schema = @Schema(implementation = Map.class))
        ),
        @ApiResponse(
            responseCode = "403",
            description = "Accès non autorisé"
        )
    })
    public ResponseEntity<Map<String, Object>> getAuthStatistics(HttpServletRequest request) {
        
        logger.info("Récupération des statistiques d'authentification depuis l'IP: {}", 
                   getClientIpAddress(request));
        
        try {
            // Vérifier l'autorisation admin
            String token = extractTokenFromHeader(request.getHeader("Authorization"));
            if (token != null) {
                var userOpt = authService.getUserFromToken(token);
                if (userOpt.isPresent() && authService.hasRole(userOpt.get(), "ADMIN")) {
                    var statistics = authService.getAuthStatistics();
                    return ResponseEntity.ok(statistics);
                }
            }
            
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Accès non autorisé"));
            
        } catch (Exception e) {
            logger.error("Erreur lors de la récupération des statistiques", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint pour nettoyer les sessions expirées
     */
    @PostMapping("/cleanup/sessions")
    @Operation(
        summary = "Nettoyer les sessions expirées",
        description = "Nettoie toutes les sessions expirées (admin seulement)"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Nettoyage terminé avec succès"
        ),
        @ApiResponse(
            responseCode = "403",
            description = "Accès non autorisé"
        )
    })
    public ResponseEntity<Map<String, String>> cleanupExpiredSessions(HttpServletRequest request) {
        
        logger.info("Nettoyage des sessions expirées depuis l'IP: {}", getClientIpAddress(request));
        
        try {
            // Vérifier l'autorisation admin
            String token = extractTokenFromHeader(request.getHeader("Authorization"));
            if (token != null) {
                var userOpt = authService.getUserFromToken(token);
                if (userOpt.isPresent() && authService.hasRole(userOpt.get(), "ADMIN")) {
                    authService.cleanupExpiredSessions();
                    return ResponseEntity.ok(Map.of("message", "Nettoyage des sessions terminé"));
                }
            }
            
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Accès non autorisé"));
            
        } catch (Exception e) {
            logger.error("Erreur lors du nettoyage des sessions", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    /**
     * Endpoint pour nettoyer les tokens expirés
     */
    @PostMapping("/cleanup/tokens")
    @Operation(
        summary = "Nettoyer les tokens expirés",
        description = "Nettoie tous les tokens expirés (admin seulement)"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Nettoyage terminé avec succès"
        ),
        @ApiResponse(
            responseCode = "403",
            description = "Accès non autorisé"
        )
    })
    public ResponseEntity<Map<String, String>> cleanupExpiredTokens(HttpServletRequest request) {
        
        logger.info("Nettoyage des tokens expirés depuis l'IP: {}", getClientIpAddress(request));
        
        try {
            // Vérifier l'autorisation admin
            String token = extractTokenFromHeader(request.getHeader("Authorization"));
            if (token != null) {
                var userOpt = authService.getUserFromToken(token);
                if (userOpt.isPresent() && authService.hasRole(userOpt.get(), "ADMIN")) {
                    authService.cleanupExpiredTokens();
                    return ResponseEntity.ok(Map.of("message", "Nettoyage des tokens terminé"));
                }
            }
            
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body(Map.of("error", "Accès non autorisé"));
            
        } catch (Exception e) {
            logger.error("Erreur lors du nettoyage des tokens", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Erreur interne du serveur"));
        }
    }
    
    // Méthodes utilitaires privées
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty() && !"unknown".equalsIgnoreCase(xForwardedFor)) {
            return xForwardedFor.split(",")[0].trim();
        }
        
        String xRealIp = request.getHeader("X-Real-IP");
        if (xRealIp != null && !xRealIp.isEmpty() && !"unknown".equalsIgnoreCase(xRealIp)) {
            return xRealIp;
        }
        
        return request.getRemoteAddr();
    }
    
    private String extractTokenFromHeader(String authorizationHeader) {
        if (authorizationHeader != null && authorizationHeader.startsWith("Bearer ")) {
            return authorizationHeader.substring(7);
        }
        return null;
    }
}
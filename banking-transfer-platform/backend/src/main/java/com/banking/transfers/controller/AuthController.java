package com.banking.transfers.controller;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.service.AuthService;
import com.banking.transfers.service.MfaService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.LockedException;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * Contrôleur pour l'authentification et la gestion des utilisateurs
 */
@RestController
@RequestMapping("/api/auth")
@Tag(name = "Authentication", description = "Endpoints d'authentification et de gestion des utilisateurs")
@CrossOrigin(origins = "*", maxAge = 3600)
public class AuthController {

    private final AuthService authService;
    private final MfaService mfaService;

    public AuthController(AuthService authService, MfaService mfaService) {
        this.authService = authService;
        this.mfaService = mfaService;
    }

    /**
     * Authentification d'un utilisateur
     */
    @PostMapping("/login")
    @Operation(
        summary = "Authentification utilisateur",
        description = "Authentifie un utilisateur avec son nom d'utilisateur/email et mot de passe"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Authentification réussie",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Identifiants invalides ou compte verrouillé"
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Données de requête invalides"
        )
    })
    public ResponseEntity<?> login(
            @Valid @RequestBody LoginRequest loginRequest,
            HttpServletRequest request) {
        
        try {
            // Ajouter les informations de la requête
            loginRequest.setIpAddress(getClientIpAddress(request));
            loginRequest.setUserAgent(request.getHeader("User-Agent"));

            LoginResponse response = authService.authenticate(loginRequest);
            return ResponseEntity.ok(response);

        } catch (BadCredentialsException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Identifiants invalides");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);

        } catch (LockedException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Compte verrouillé");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur d'authentification");
            error.put("message", "Une erreur inattendue s'est produite");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Rafraîchissement d'un token d'accès
     */
    @PostMapping("/refresh")
    @Operation(
        summary = "Rafraîchissement de token",
        description = "Rafraîchit un token d'accès en utilisant un token de rafraîchissement valide"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Token rafraîchi avec succès",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Token de rafraîchissement invalide"
        )
    })
    public ResponseEntity<?> refreshToken(
            @RequestHeader("Authorization") String authorizationHeader) {
        
        try {
            String refreshToken = extractTokenFromHeader(authorizationHeader);
            LoginResponse response = authService.refreshToken(refreshToken);
            return ResponseEntity.ok(response);

        } catch (BadCredentialsException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Token invalide");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de rafraîchissement");
            error.put("message", "Une erreur inattendue s'est produite");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Déconnexion d'un utilisateur
     */
    @PostMapping("/logout")
    @Operation(
        summary = "Déconnexion utilisateur",
        description = "Déconnecte un utilisateur et invalide son token"
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
    public ResponseEntity<?> logout(
            @RequestHeader("Authorization") String authorizationHeader,
            HttpServletRequest request) {
        
        try {
            String accessToken = extractTokenFromHeader(authorizationHeader);
            authService.logout(accessToken, getClientIpAddress(request));

            Map<String, String> response = new HashMap<>();
            response.put("message", "Déconnexion réussie");
            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de déconnexion");
            error.put("message", "Une erreur inattendue s'est produite");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Changement de mot de passe
     */
    @PostMapping("/change-password")
    @Operation(
        summary = "Changement de mot de passe",
        description = "Change le mot de passe de l'utilisateur connecté"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Mot de passe changé avec succès"
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Données invalides"
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Mot de passe actuel incorrect"
        )
    })
    public ResponseEntity<?> changePassword(
            @RequestParam String currentPassword,
            @RequestParam String newPassword,
            @RequestParam String username) {
        
        try {
            authService.changePassword(username, currentPassword, newPassword);

            Map<String, String> response = new HashMap<>();
            response.put("message", "Mot de passe changé avec succès");
            return ResponseEntity.ok(response);

        } catch (BadCredentialsException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Mot de passe incorrect");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de changement de mot de passe");
            error.put("message", "Une erreur inattendue s'est produite");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Activation/désactivation de MFA
     */
    @PostMapping("/mfa/toggle")
    @Operation(
        summary = "Activation/désactivation MFA",
        description = "Active ou désactive l'authentification multi-facteurs pour un utilisateur"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "MFA configuré avec succès"
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Données invalides"
        )
    })
    public ResponseEntity<?> toggleMfa(
            @RequestParam String username,
            @RequestParam boolean enable) {
        
        try {
            authService.toggleMfa(username, enable);

            Map<String, Object> response = new HashMap<>();
            response.put("message", enable ? "MFA activé avec succès" : "MFA désactivé avec succès");
            response.put("mfaEnabled", enable);

            if (enable) {
                // Retourner les informations pour la configuration MFA
                // TODO: Implémenter la génération de QR code et de secret
                response.put("setupRequired", true);
            }

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de configuration MFA");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Vérification d'un code MFA
     */
    @PostMapping("/mfa/verify")
    @Operation(
        summary = "Vérification code MFA",
        description = "Vérifie un code MFA pour un utilisateur"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Code MFA vérifié avec succès"
        ),
        @ApiResponse(
            responseCode = "400",
            description = "Code MFA invalide"
        )
    })
    public ResponseEntity<?> verifyMfaCode(
            @RequestParam String username,
            @RequestParam String code) {
        
        try {
            boolean isValid = authService.verifyMfaCode(username, code);

            Map<String, Object> response = new HashMap<>();
            response.put("valid", isValid);
            response.put("message", isValid ? "Code MFA valide" : "Code MFA invalide");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de vérification MFA");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Déverrouillage d'un compte
     */
    @PostMapping("/admin/unlock-account")
    @Operation(
        summary = "Déverrouillage de compte",
        description = "Déverrouille un compte utilisateur verrouillé (Admin uniquement)"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Compte déverrouillé avec succès"
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Non autorisé"
        )
    })
    public ResponseEntity<?> unlockAccount(
            @RequestParam String username) {
        
        try {
            authService.unlockAccount(username);

            Map<String, String> response = new HashMap<>();
            response.put("message", "Compte déverrouillé avec succès");
            return ResponseEntity.ok(response);

        } catch (BadCredentialsException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Utilisateur non trouvé");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de déverrouillage");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Activation/désactivation d'un compte
     */
    @PostMapping("/admin/toggle-account")
    @Operation(
        summary = "Activation/désactivation de compte",
        description = "Active ou désactive un compte utilisateur (Admin uniquement)"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Statut de compte modifié avec succès"
        ),
        @ApiResponse(
            responseCode = "401",
            description = "Non autorisé"
        )
    })
    public ResponseEntity<?> toggleAccountStatus(
            @RequestParam String username,
            @RequestParam boolean active) {
        
        try {
            authService.toggleAccountStatus(username, active);

            Map<String, Object> response = new HashMap<>();
            response.put("message", active ? "Compte activé avec succès" : "Compte désactivé avec succès");
            response.put("active", active);
            return ResponseEntity.ok(response);

        } catch (BadCredentialsException e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Utilisateur non trouvé");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de modification de statut");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Vérification de la capacité de transfert
     */
    @GetMapping("/can-transfer")
    @Operation(
        summary = "Vérification capacité de transfert",
        description = "Vérifie si un utilisateur peut effectuer des transferts"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Vérification réussie"
        )
    })
    public ResponseEntity<?> canUserTransfer(
            @RequestParam String username) {
        
        try {
            boolean canTransfer = authService.canUserTransfer(username);

            Map<String, Object> response = new HashMap<>();
            response.put("canTransfer", canTransfer);
            response.put("message", canTransfer ? "Utilisateur autorisé à transférer" : "Utilisateur non autorisé à transférer");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de vérification");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Vérification des permissions
     */
    @GetMapping("/has-permission")
    @Operation(
        summary = "Vérification de permission",
        description = "Vérifie si un utilisateur a une permission spécifique"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Vérification réussie"
        )
    })
    public ResponseEntity<?> hasPermission(
            @RequestParam String username,
            @RequestParam String permission) {
        
        try {
            boolean hasPermission = authService.hasPermission(username, permission);

            Map<String, Object> response = new HashMap<>();
            response.put("hasPermission", hasPermission);
            response.put("permission", permission);
            response.put("message", hasPermission ? "Permission accordée" : "Permission refusée");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de vérification de permission");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Vérification des rôles
     */
    @GetMapping("/has-role")
    @Operation(
        summary = "Vérification de rôle",
        description = "Vérifie si un utilisateur a un rôle spécifique"
    )
    @ApiResponses(value = {
        @ApiResponse(
            responseCode = "200",
            description = "Vérification réussie"
        )
    })
    public ResponseEntity<?> hasRole(
            @RequestParam String username,
            @RequestParam String role) {
        
        try {
            boolean hasRole = authService.hasRole(username, role);

            Map<String, Object> response = new HashMap<>();
            response.put("hasRole", hasRole);
            response.put("role", role);
            response.put("message", hasRole ? "Rôle accordé" : "Rôle refusé");

            return ResponseEntity.ok(response);

        } catch (Exception e) {
            Map<String, String> error = new HashMap<>();
            error.put("error", "Erreur de vérification de rôle");
            error.put("message", e.getMessage());
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Endpoint de santé pour l'authentification
     */
    @GetMapping("/health")
    @Operation(
        summary = "Santé du service d'authentification",
        description = "Vérifie l'état du service d'authentification"
    )
    public ResponseEntity<?> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "UP");
        response.put("service", "Authentication Service");
        response.put("timestamp", System.currentTimeMillis());
        return ResponseEntity.ok(response);
    }

    // Méthodes utilitaires privées

    /**
     * Extrait le token du header Authorization
     */
    private String extractTokenFromHeader(String authorizationHeader) {
        if (authorizationHeader != null && authorizationHeader.startsWith("Bearer ")) {
            return authorizationHeader.substring(7);
        }
        throw new BadCredentialsException("Header Authorization invalide");
    }

    /**
     * Obtient l'adresse IP du client
     */
    private String getClientIpAddress(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty() && !"unknown".equalsIgnoreCase(xForwardedFor)) {
            return xForwardedFor.split(",")[0];
        }
        
        String xRealIp = request.getHeader("X-Real-IP");
        if (xRealIp != null && !xRealIp.isEmpty() && !"unknown".equalsIgnoreCase(xRealIp)) {
            return xRealIp;
        }
        
        return request.getRemoteAddr();
    }
}
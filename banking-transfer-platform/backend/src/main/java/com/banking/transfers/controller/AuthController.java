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
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.LockedException;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

/**
 * Contrôleur pour l'authentification et la gestion des utilisateurs
 */
@RestController
@RequestMapping("/auth")
@Tag(name = "Authentication", description = "Endpoints d'authentification et de gestion des utilisateurs")
@CrossOrigin(origins = "*", maxAge = 3600)
public class AuthController {

    @Autowired
    private AuthService authService;

    @Autowired
    private MfaService mfaService;

    /**
     * Authentification d'un utilisateur
     */
    @PostMapping("/login")
    @Operation(summary = "Authentification utilisateur", description = "Authentifie un utilisateur avec nom d'utilisateur/email et mot de passe")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Authentification réussie",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))),
        @ApiResponse(responseCode = "401", description = "Identifiants invalides"),
        @ApiResponse(responseCode = "423", description = "Compte verrouillé"),
        @ApiResponse(responseCode = "400", description = "Données de requête invalides")
    })
    public ResponseEntity<?> login(
            @Valid @RequestBody LoginRequest loginRequest,
            HttpServletRequest request) {
        
        try {
            // Ajouter les informations client à la requête
            loginRequest.setClientIp(getClientIpAddress(request));
            loginRequest.setUserAgent(request.getHeader("User-Agent"));

            LoginResponse response = authService.login(loginRequest);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response);
            result.put("message", "Authentification réussie");
            
            return ResponseEntity.ok(result);
            
        } catch (BadCredentialsException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Identifiants invalides");
            error.put("error", "INVALID_CREDENTIALS");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            
        } catch (LockedException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Compte verrouillé");
            error.put("error", "ACCOUNT_LOCKED");
            return ResponseEntity.status(HttpStatus.LOCKED).body(error);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors de l'authentification");
            error.put("error", "AUTHENTICATION_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Déconnexion d'un utilisateur
     */
    @PostMapping("/logout")
    @Operation(summary = "Déconnexion utilisateur", description = "Déconnecte un utilisateur et invalide son token")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Déconnexion réussie"),
        @ApiResponse(responseCode = "401", description = "Token invalide")
    })
    public ResponseEntity<?> logout(
            @RequestHeader("Authorization") String authorization,
            HttpServletRequest request) {
        
        try {
            authService.logout(authorization, getClientIpAddress(request), request.getHeader("User-Agent"));
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("message", "Déconnexion réussie");
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors de la déconnexion");
            error.put("error", "LOGOUT_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Rafraîchissement d'un token d'accès
     */
    @PostMapping("/refresh")
    @Operation(summary = "Rafraîchissement de token", description = "Rafraîchit un token d'accès avec un refresh token")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Token rafraîchi avec succès",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))),
        @ApiResponse(responseCode = "401", description = "Refresh token invalide")
    })
    public ResponseEntity<?> refreshToken(
            @RequestParam String refreshToken) {
        
        try {
            LoginResponse response = authService.refreshToken(refreshToken);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", response);
            result.put("message", "Token rafraîchi avec succès");
            
            return ResponseEntity.ok(result);
            
        } catch (BadCredentialsException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Refresh token invalide");
            error.put("error", "INVALID_REFRESH_TOKEN");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors du rafraîchissement du token");
            error.put("error", "REFRESH_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Validation d'un token d'accès
     */
    @GetMapping("/validate")
    @Operation(summary = "Validation de token", description = "Valide un token d'accès")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Token valide"),
        @ApiResponse(responseCode = "401", description = "Token invalide")
    })
    public ResponseEntity<?> validateToken(
            @RequestHeader("Authorization") String authorization) {
        
        try {
            boolean isValid = authService.validateToken(authorization);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("valid", isValid);
            result.put("message", isValid ? "Token valide" : "Token invalide");
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors de la validation du token");
            error.put("error", "VALIDATION_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Changement de mot de passe
     */
    @PostMapping("/change-password")
    @Operation(summary = "Changement de mot de passe", description = "Change le mot de passe d'un utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Mot de passe changé avec succès"),
        @ApiResponse(responseCode = "401", description = "Mot de passe actuel incorrect"),
        @ApiResponse(responseCode = "400", description = "Données de requête invalides")
    })
    public ResponseEntity<?> changePassword(
            @RequestParam UUID userId,
            @RequestParam String currentPassword,
            @RequestParam String newPassword) {
        
        try {
            authService.changePassword(userId, currentPassword, newPassword);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("message", "Mot de passe changé avec succès");
            
            return ResponseEntity.ok(result);
            
        } catch (BadCredentialsException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Mot de passe actuel incorrect");
            error.put("error", "INVALID_CURRENT_PASSWORD");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            
        } catch (IllegalArgumentException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", e.getMessage());
            error.put("error", "INVALID_PASSWORD");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors du changement de mot de passe");
            error.put("error", "PASSWORD_CHANGE_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Demande de réinitialisation de mot de passe
     */
    @PostMapping("/reset-password-request")
    @Operation(summary = "Demande de réinitialisation", description = "Demande une réinitialisation de mot de passe")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Demande envoyée avec succès"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<?> resetPasswordRequest(
            @RequestParam String email) {
        
        try {
            authService.resetPassword(email);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("message", "Email de réinitialisation envoyé");
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors de l'envoi de la demande de réinitialisation");
            error.put("error", "RESET_REQUEST_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Confirmation de réinitialisation de mot de passe
     */
    @PostMapping("/reset-password-confirm")
    @Operation(summary = "Confirmation de réinitialisation", description = "Confirme la réinitialisation de mot de passe")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Mot de passe réinitialisé avec succès"),
        @ApiResponse(responseCode = "401", description = "Token de réinitialisation invalide"),
        @ApiResponse(responseCode = "400", description = "Données de requête invalides")
    })
    public ResponseEntity<?> resetPasswordConfirm(
            @RequestParam String resetToken,
            @RequestParam String newPassword) {
        
        try {
            authService.confirmPasswordReset(resetToken, newPassword);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("message", "Mot de passe réinitialisé avec succès");
            
            return ResponseEntity.ok(result);
            
        } catch (BadCredentialsException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Token de réinitialisation invalide");
            error.put("error", "INVALID_RESET_TOKEN");
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(error);
            
        } catch (IllegalArgumentException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", e.getMessage());
            error.put("error", "INVALID_PASSWORD");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors de la réinitialisation du mot de passe");
            error.put("error", "PASSWORD_RESET_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Génération d'un code MFA de test
     */
    @GetMapping("/mfa/test-code")
    @Operation(summary = "Code MFA de test", description = "Génère un code MFA de test pour un secret donné")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Code généré avec succès"),
        @ApiResponse(responseCode = "400", description = "Secret MFA invalide")
    })
    public ResponseEntity<?> generateTestMfaCode(
            @RequestParam String secret) {
        
        try {
            String code = mfaService.generateTestCode(secret);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("code", code);
            result.put("message", "Code MFA généré avec succès");
            
            return ResponseEntity.ok(result);
            
        } catch (IllegalArgumentException e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", e.getMessage());
            error.put("error", "INVALID_MFA_SECRET");
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors de la génération du code MFA");
            error.put("error", "MFA_GENERATION_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Validation d'un code MFA
     */
    @PostMapping("/mfa/validate")
    @Operation(summary = "Validation MFA", description = "Valide un code MFA")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Code validé avec succès"),
        @ApiResponse(responseCode = "401", description = "Code MFA invalide")
    })
    public ResponseEntity<?> validateMfaCode(
            @RequestParam String secret,
            @RequestParam String code) {
        
        try {
            boolean isValid = mfaService.validateMfaCode(secret, code);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("valid", isValid);
            result.put("message", isValid ? "Code MFA valide" : "Code MFA invalide");
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors de la validation du code MFA");
            error.put("error", "MFA_VALIDATION_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Génération d'une configuration MFA
     */
    @GetMapping("/mfa/config")
    @Operation(summary = "Configuration MFA", description = "Génère une configuration MFA complète pour un utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Configuration générée avec succès"),
        @ApiResponse(responseCode = "400", description = "Paramètres invalides")
    })
    public ResponseEntity<?> generateMfaConfig(
            @RequestParam String username,
            @RequestParam(defaultValue = "Banking Transfer Platform") String issuer) {
        
        try {
            MfaService.MfaConfig config = mfaService.generateMfaConfig(username, issuer);
            
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", config);
            result.put("message", "Configuration MFA générée avec succès");
            
            return ResponseEntity.ok(result);
            
        } catch (Exception e) {
            Map<String, Object> error = new HashMap<>();
            error.put("success", false);
            error.put("message", "Erreur lors de la génération de la configuration MFA");
            error.put("error", "MFA_CONFIG_ERROR");
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(error);
        }
    }

    /**
     * Obtient l'adresse IP du client
     */
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
}
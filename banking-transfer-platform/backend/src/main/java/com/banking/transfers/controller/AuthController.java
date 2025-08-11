package com.banking.transfers.controller;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.dto.PasswordChangeRequest;
import com.banking.transfers.dto.MfaToggleRequest;
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
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

/**
 * Contrôleur pour l'authentification et la gestion des utilisateurs
 */
@RestController
@RequestMapping("/auth")
@Tag(name = "Authentification", description = "API d'authentification et de gestion des utilisateurs")
@CrossOrigin(origins = "*", maxAge = 3600)
public class AuthController {

    @Autowired
    private AuthService authService;

    /**
     * Authentification d'un utilisateur
     */
    @PostMapping("/login")
    @Operation(summary = "Authentification utilisateur", description = "Authentifie un utilisateur et retourne un token JWT")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Authentification réussie",
            content = @Content(schema = @Schema(implementation = LoginResponse.class))),
        @ApiResponse(responseCode = "401", description = "Identifiants invalides"),
        @ApiResponse(responseCode = "423", description = "Compte verrouillé"),
        @ApiResponse(responseCode = "400", description = "Données invalides")
    })
    public ResponseEntity<LoginResponse> login(
            @Valid @RequestBody LoginRequest loginRequest,
            HttpServletRequest request) {
        
        String clientIp = getClientIpAddress(request);
        String userAgent = request.getHeader("User-Agent");
        
        LoginResponse response = authService.login(loginRequest, clientIp, userAgent);
        return ResponseEntity.ok(response);
    }

    /**
     * Déconnexion
     */
    @PostMapping("/logout")
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Déconnexion", description = "Déconnecte l'utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Déconnexion réussie"),
        @ApiResponse(responseCode = "401", description = "Non authentifié")
    })
    public ResponseEntity<Void> logout(
            @RequestHeader("Authorization") String authorization,
            HttpServletRequest request) {
        
        String token = authorization.replace("Bearer ", "");
        String clientIp = getClientIpAddress(request);
        
        authService.logout(token, clientIp);
        return ResponseEntity.ok().build();
    }

    /**
     * Changement de mot de passe
     */
    @PostMapping("/change-password")
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Changement mot de passe", description = "Change le mot de passe de l'utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Mot de passe changé avec succès"),
        @ApiResponse(responseCode = "400", description = "Ancien mot de passe incorrect"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé")
    })
    public ResponseEntity<Void> changePassword(
            @Valid @RequestBody PasswordChangeRequest changeRequest,
            HttpServletRequest request) {
        
        String clientIp = getClientIpAddress(request);
        authService.changePassword(changeRequest.getCurrentPassword(), changeRequest.getNewPassword(), clientIp);
        return ResponseEntity.ok().build();
    }

    /**
     * Activation/désactivation MFA
     */
    @PostMapping("/mfa/toggle")
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Toggle MFA", description = "Active ou désactive l'authentification à deux facteurs")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "MFA mis à jour avec succès"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé")
    })
    public ResponseEntity<Void> toggleMfa(
            @Valid @RequestBody MfaToggleRequest toggleRequest,
            HttpServletRequest request) {
        
        String clientIp = getClientIpAddress(request);
        authService.toggleMfa(toggleRequest.getMfaCode(), clientIp);
        return ResponseEntity.ok().build();
    }

    /**
     * Endpoint de santé
     */
    @GetMapping("/health")
    @Operation(summary = "Santé API", description = "Vérifie la santé de l'API d'authentification")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "API en bonne santé")
    })
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Auth API is healthy");
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
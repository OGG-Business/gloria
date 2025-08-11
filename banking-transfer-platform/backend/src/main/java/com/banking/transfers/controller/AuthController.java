package com.banking.transfers.controller;

import com.banking.transfers.dto.*;
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
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

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
            content = @Content(schema = @Schema(implementation = AuthResponse.class))),
        @ApiResponse(responseCode = "401", description = "Identifiants invalides"),
        @ApiResponse(responseCode = "423", description = "Compte verrouillé"),
        @ApiResponse(responseCode = "400", description = "Données invalides")
    })
    public ResponseEntity<AuthResponse> login(
            @Valid @RequestBody LoginRequest loginRequest,
            HttpServletRequest request) {
        
        // Ajouter les informations client
        loginRequest.setClientIp(getClientIpAddress(request));
        loginRequest.setUserAgent(request.getHeader("User-Agent"));
        
        AuthResponse response = authService.authenticateUser(loginRequest);
        return ResponseEntity.ok(response);
    }

    /**
     * Enregistrement d'un nouvel utilisateur
     */
    @PostMapping("/register")
    @Operation(summary = "Enregistrement utilisateur", description = "Enregistre un nouvel utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Utilisateur créé avec succès",
            content = @Content(schema = @Schema(implementation = UserRegistrationResponse.class))),
        @ApiResponse(responseCode = "400", description = "Données invalides ou utilisateur existant"),
        @ApiResponse(responseCode = "409", description = "Utilisateur déjà existant")
    })
    public ResponseEntity<UserRegistrationResponse> register(
            @Valid @RequestBody UserRegistrationRequest registrationRequest) {
        
        UserRegistrationResponse response = authService.registerUser(registrationRequest);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Mise à jour du profil utilisateur
     */
    @PutMapping("/profile")
    @PreAuthorize("hasRole('USER')")
    @Operation(summary = "Mise à jour profil", description = "Met à jour le profil de l'utilisateur connecté")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Profil mis à jour avec succès",
            content = @Content(schema = @Schema(implementation = UserProfileResponse.class))),
        @ApiResponse(responseCode = "400", description = "Données invalides"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé")
    })
    public ResponseEntity<UserProfileResponse> updateProfile(
            @Valid @RequestBody UserProfileUpdateRequest updateRequest,
            @Parameter(description = "ID de l'utilisateur") @RequestParam UUID userId) {
        
        UserProfileResponse response = authService.updateUserProfile(userId, updateRequest);
        return ResponseEntity.ok(response);
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
            @Parameter(description = "ID de l'utilisateur") @RequestParam UUID userId) {
        
        authService.changePassword(userId, changeRequest);
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
            @Parameter(description = "ID de l'utilisateur") @RequestParam UUID userId) {
        
        authService.toggleMfa(userId, toggleRequest);
        return ResponseEntity.ok().build();
    }

    /**
     * Recherche d'utilisateurs (Admin)
     */
    @GetMapping("/users/search")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Recherche utilisateurs", description = "Recherche des utilisateurs avec pagination")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Recherche réussie",
            content = @Content(schema = @Schema(implementation = Page.class))),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé")
    })
    public ResponseEntity<Page<UserProfileResponse>> searchUsers(
            @Parameter(description = "Critères de recherche") UserSearchRequest searchRequest,
            @Parameter(description = "Paramètres de pagination") Pageable pageable) {
        
        Page<UserProfileResponse> users = authService.searchUsers(searchRequest, pageable);
        return ResponseEntity.ok(users);
    }

    /**
     * Utilisateurs nécessitant une surveillance renforcée (Admin)
     */
    @GetMapping("/users/enhanced-due-diligence")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Utilisateurs à surveiller", description = "Liste des utilisateurs nécessitant une surveillance renforcée")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Liste récupérée avec succès"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé")
    })
    public ResponseEntity<List<UserProfileResponse>> getUsersRequiringEnhancedDueDiligence() {
        List<UserProfileResponse> users = authService.findUsersRequiringEnhancedDueDiligence();
        return ResponseEntity.ok(users);
    }

    /**
     * Utilisateurs inactifs (Admin)
     */
    @GetMapping("/users/inactive")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Utilisateurs inactifs", description = "Liste des utilisateurs inactifs depuis une période donnée")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Liste récupérée avec succès"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé")
    })
    public ResponseEntity<List<UserProfileResponse>> getInactiveUsers(
            @Parameter(description = "Date de coupure") @RequestParam LocalDateTime cutoffDate) {
        
        List<UserProfileResponse> users = authService.findInactiveUsers(cutoffDate);
        return ResponseEntity.ok(users);
    }

    /**
     * Statistiques des utilisateurs (Admin)
     */
    @GetMapping("/users/statistics")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Statistiques utilisateurs", description = "Obtient les statistiques des utilisateurs")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Statistiques récupérées avec succès",
            content = @Content(schema = @Schema(implementation = UserStatisticsResponse.class))),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé")
    })
    public ResponseEntity<UserStatisticsResponse> getUserStatistics() {
        UserStatisticsResponse statistics = authService.getUserStatistics();
        return ResponseEntity.ok(statistics);
    }

    /**
     * Déverrouillage d'un compte (Admin)
     */
    @PostMapping("/users/{userId}/unlock")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Déverrouiller compte", description = "Déverrouille un compte utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Compte déverrouillé avec succès"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Void> unlockUserAccount(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId) {
        
        authService.unlockUserAccount(userId);
        return ResponseEntity.ok().build();
    }

    /**
     * Désactivation d'un compte (Admin)
     */
    @PostMapping("/users/{userId}/deactivate")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Désactiver compte", description = "Désactive un compte utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Compte désactivé avec succès"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Void> deactivateUserAccount(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId) {
        
        authService.deactivateUserAccount(userId);
        return ResponseEntity.ok().build();
    }

    /**
     * Mise à jour du statut KYC (Admin)
     */
    @PutMapping("/users/{userId}/kyc-status")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Mettre à jour KYC", description = "Met à jour le statut KYC d'un utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Statut KYC mis à jour avec succès"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Void> updateKycStatus(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            @Parameter(description = "Nouveau statut KYC") @RequestParam String kycStatus,
            @Parameter(description = "Raison du changement") @RequestParam(required = false) String reason) {
        
        // TODO: Convertir le string en enum KYCStatus
        // authService.updateKycStatus(userId, KYCStatus.valueOf(kycStatus), reason);
        return ResponseEntity.ok().build();
    }

    /**
     * Mise à jour du statut AML (Admin)
     */
    @PutMapping("/users/{userId}/aml-status")
    @PreAuthorize("hasRole('ADMIN')")
    @Operation(summary = "Mettre à jour AML", description = "Met à jour le statut AML d'un utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Statut AML mis à jour avec succès"),
        @ApiResponse(responseCode = "401", description = "Non authentifié"),
        @ApiResponse(responseCode = "403", description = "Non autorisé"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Void> updateAmlStatus(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            @Parameter(description = "Nouveau statut AML") @RequestParam String amlStatus,
            @Parameter(description = "Raison du changement") @RequestParam(required = false) String reason) {
        
        // TODO: Convertir le string en enum AMLStatus
        // authService.updateAmlStatus(userId, AMLStatus.valueOf(amlStatus), reason);
        return ResponseEntity.ok().build();
    }

    /**
     * Vérification de la santé de l'API
     */
    @GetMapping("/health")
    @Operation(summary = "Santé API", description = "Vérifie la santé de l'API d'authentification")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "API en bonne santé")
    })
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("Auth API is healthy");
    }

    // Méthodes utilitaires privées

    /**
     * Extrait l'adresse IP du client depuis la requête HTTP
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
package com.banking.transfers.controller;

import com.banking.transfers.dto.auth.LoginRequest;
import com.banking.transfers.dto.auth.LoginResponse;
import com.banking.transfers.model.AMLStatus;
import com.banking.transfers.model.KYCStatus;
import com.banking.transfers.model.User;
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
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Contrôleur pour l'authentification et la gestion des utilisateurs
 */
@RestController
@RequestMapping("/api/auth")
@Tag(name = "Authentication", description = "Endpoints pour l'authentification et la gestion des utilisateurs")
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
    @Operation(summary = "Authentifier un utilisateur", description = "Authentifie un utilisateur avec ses identifiants")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Authentification réussie",
                content = @Content(schema = @Schema(implementation = LoginResponse.class))),
        @ApiResponse(responseCode = "401", description = "Identifiants invalides"),
        @ApiResponse(responseCode = "423", description = "Compte verrouillé"),
        @ApiResponse(responseCode = "400", description = "Données de requête invalides")
    })
    public ResponseEntity<LoginResponse> login(
            @Valid @RequestBody LoginRequest loginRequest,
            HttpServletRequest request) {
        
        // Ajouter les informations de la requête HTTP
        loginRequest.setIpAddress(getClientIpAddress(request));
        loginRequest.setUserAgent(request.getHeader("User-Agent"));

        try {
            LoginResponse response = authService.authenticate(loginRequest);
            return ResponseEntity.ok(response);
        } catch (AuthService.AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
    }

    /**
     * Création d'un nouvel utilisateur
     */
    @PostMapping("/register")
    @Operation(summary = "Créer un nouvel utilisateur", description = "Crée un nouveau compte utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Utilisateur créé avec succès"),
        @ApiResponse(responseCode = "400", description = "Données invalides"),
        @ApiResponse(responseCode = "409", description = "Utilisateur déjà existant")
    })
    public ResponseEntity<User> register(
            @Valid @RequestBody User user,
            @RequestParam String password) {
        
        try {
            User createdUser = authService.createUser(user, password);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdUser);
        } catch (AuthService.UserExistsException e) {
            return ResponseEntity.status(HttpStatus.CONFLICT).build();
        }
    }

    /**
     * Rafraîchir un token d'accès
     */
    @PostMapping("/refresh")
    @Operation(summary = "Rafraîchir un token", description = "Rafraîchit un token d'accès expiré")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Token rafraîchi avec succès"),
        @ApiResponse(responseCode = "401", description = "Token invalide ou expiré")
    })
    public ResponseEntity<LoginResponse> refreshToken(@RequestParam String refreshToken) {
        // TODO: Implémenter le rafraîchissement de token
        return ResponseEntity.status(HttpStatus.NOT_IMPLEMENTED).build();
    }

    /**
     * Déconnexion d'un utilisateur
     */
    @PostMapping("/logout")
    @Operation(summary = "Déconnecter un utilisateur", description = "Déconnecte un utilisateur et invalide ses tokens")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Déconnexion réussie"),
        @ApiResponse(responseCode = "401", description = "Non authentifié")
    })
    public ResponseEntity<Void> logout(@RequestParam String token) {
        // TODO: Implémenter la déconnexion
        return ResponseEntity.ok().build();
    }

    /**
     * Changer le mot de passe
     */
    @PostMapping("/change-password")
    @Operation(summary = "Changer le mot de passe", description = "Change le mot de passe de l'utilisateur connecté")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Mot de passe changé avec succès"),
        @ApiResponse(responseCode = "400", description = "Ancien mot de passe incorrect"),
        @ApiResponse(responseCode = "401", description = "Non authentifié")
    })
    public ResponseEntity<Void> changePassword(
            @RequestParam String currentPassword,
            @RequestParam String newPassword,
            @RequestParam UUID userId) {
        
        try {
            authService.changePassword(userId, currentPassword, newPassword);
            return ResponseEntity.ok().build();
        } catch (AuthService.AuthenticationException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).build();
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Activer/désactiver MFA
     */
    @PostMapping("/mfa/toggle")
    @Operation(summary = "Activer/désactiver MFA", description = "Active ou désactive l'authentification à deux facteurs")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "MFA configuré avec succès"),
        @ApiResponse(responseCode = "400", description = "Données invalides"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Map<String, Object>> toggleMfa(
            @RequestParam UUID userId,
            @RequestParam boolean enable) {
        
        try {
            authService.toggleMfa(userId, enable);
            
            Map<String, Object> response = new HashMap<>();
            response.put("mfaEnabled", enable);
            response.put("message", enable ? "MFA activé avec succès" : "MFA désactivé avec succès");
            
            if (enable) {
                // TODO: Retourner le secret MFA et l'URL QR Code
                response.put("secret", "TODO_GENERATE_SECRET");
                response.put("qrCodeUrl", "TODO_GENERATE_QR_URL");
            }
            
            return ResponseEntity.ok(response);
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Vérifier un code MFA
     */
    @PostMapping("/mfa/verify")
    @Operation(summary = "Vérifier un code MFA", description = "Vérifie un code d'authentification à deux facteurs")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Code MFA valide"),
        @ApiResponse(responseCode = "400", description = "Code MFA invalide"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Map<String, Object>> verifyMfa(
            @RequestParam UUID userId,
            @RequestParam String code) {
        
        try {
            User user = authService.findById(userId);
            boolean isValid = mfaService.verifyMfaCode(user, code);
            
            Map<String, Object> response = new HashMap<>();
            response.put("valid", isValid);
            response.put("message", isValid ? "Code MFA valide" : "Code MFA invalide");
            
            return ResponseEntity.ok(response);
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Obtenir les informations d'un utilisateur
     */
    @GetMapping("/users/{userId}")
    @Operation(summary = "Obtenir un utilisateur", description = "Récupère les informations d'un utilisateur par son ID")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Utilisateur trouvé"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<User> getUser(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId) {
        
        try {
            User user = authService.findById(userId);
            return ResponseEntity.ok(user);
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Mettre à jour un utilisateur
     */
    @PutMapping("/users/{userId}")
    @Operation(summary = "Mettre à jour un utilisateur", description = "Met à jour les informations d'un utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Utilisateur mis à jour avec succès"),
        @ApiResponse(responseCode = "400", description = "Données invalides"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<User> updateUser(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            @Valid @RequestBody User userDetails) {
        
        try {
            User updatedUser = authService.updateUser(userId, userDetails);
            return ResponseEntity.ok(updatedUser);
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Obtenir tous les utilisateurs actifs
     */
    @GetMapping("/users")
    @Operation(summary = "Lister les utilisateurs", description = "Récupère la liste des utilisateurs actifs")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Liste des utilisateurs")
    })
    public ResponseEntity<List<User>> getActiveUsers() {
        List<User> users = authService.findAllActiveUsers();
        return ResponseEntity.ok(users);
    }

    /**
     * Obtenir les utilisateurs nécessitant une vérification KYC
     */
    @GetMapping("/users/kyc/pending")
    @Operation(summary = "Utilisateurs en attente KYC", description = "Récupère les utilisateurs nécessitant une vérification KYC")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Liste des utilisateurs")
    })
    public ResponseEntity<List<User>> getUsersRequiringKYC() {
        List<User> users = authService.findUsersRequiringKYC();
        return ResponseEntity.ok(users);
    }

    /**
     * Obtenir les utilisateurs nécessitant une vérification AML
     */
    @GetMapping("/users/aml/pending")
    @Operation(summary = "Utilisateurs en attente AML", description = "Récupère les utilisateurs nécessitant une vérification AML")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Liste des utilisateurs")
    })
    public ResponseEntity<List<User>> getUsersRequiringAML() {
        List<User> users = authService.findUsersRequiringAML();
        return ResponseEntity.ok(users);
    }

    /**
     * Obtenir les utilisateurs à haut risque
     */
    @GetMapping("/users/high-risk")
    @Operation(summary = "Utilisateurs à haut risque", description = "Récupère les utilisateurs avec un score de risque élevé")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Liste des utilisateurs")
    })
    public ResponseEntity<List<User>> getHighRiskUsers() {
        List<User> users = authService.findHighRiskUsers();
        return ResponseEntity.ok(users);
    }

    /**
     * Mettre à jour le statut KYC d'un utilisateur
     */
    @PutMapping("/users/{userId}/kyc")
    @Operation(summary = "Mettre à jour le statut KYC", description = "Met à jour le statut KYC d'un utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Statut KYC mis à jour"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Void> updateKycStatus(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            @RequestParam KYCStatus status) {
        
        try {
            authService.updateKycStatus(userId, status);
            return ResponseEntity.ok().build();
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Mettre à jour le statut AML d'un utilisateur
     */
    @PutMapping("/users/{userId}/aml")
    @Operation(summary = "Mettre à jour le statut AML", description = "Met à jour le statut AML d'un utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Statut AML mis à jour"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Void> updateAmlStatus(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            @RequestParam AMLStatus status) {
        
        try {
            authService.updateAmlStatus(userId, status);
            return ResponseEntity.ok().build();
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Mettre à jour le score de risque d'un utilisateur
     */
    @PutMapping("/users/{userId}/risk-score")
    @Operation(summary = "Mettre à jour le score de risque", description = "Met à jour le score de risque d'un utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Score de risque mis à jour"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Void> updateRiskScore(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            @RequestParam Integer riskScore) {
        
        try {
            authService.updateRiskScore(userId, riskScore);
            return ResponseEntity.ok().build();
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Verrouiller/déverrouiller un compte utilisateur
     */
    @PutMapping("/users/{userId}/lock")
    @Operation(summary = "Verrouiller/déverrouiller un compte", description = "Verrouille ou déverrouille un compte utilisateur")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Statut de verrouillage mis à jour"),
        @ApiResponse(responseCode = "404", description = "Utilisateur non trouvé")
    })
    public ResponseEntity<Void> toggleAccountLock(
            @Parameter(description = "ID de l'utilisateur") @PathVariable UUID userId,
            @RequestParam boolean lock) {
        
        try {
            authService.toggleAccountLock(userId, lock);
            return ResponseEntity.ok().build();
        } catch (AuthService.UserNotFoundException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }

    /**
     * Obtenir l'adresse IP du client
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
package com.swiftpay.controller;

import com.swiftpay.model.dto.TransferCreateRequest;
import com.swiftpay.model.dto.TransferResponse;
import com.swiftpay.model.dto.TransferEventResponse;
import com.swiftpay.model.entity.Transfer;
import com.swiftpay.service.TransferService;
import com.swiftpay.service.AuditService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.time.ZonedDateTime;
import java.math.BigDecimal;

/**
 * Contrôleur REST pour la gestion des transferts bancaires
 */
@RestController
@RequestMapping("/transfers")
@Tag(name = "Transfers", description = "API de gestion des transferts bancaires SWIFT & IBAN")
@SecurityRequirement(name = "bearerAuth")
public class TransferController {

    private static final Logger logger = LoggerFactory.getLogger(TransferController.class);

    private final TransferService transferService;
    private final AuditService auditService;

    @Autowired
    public TransferController(TransferService transferService, AuditService auditService) {
        this.transferService = transferService;
        this.auditService = auditService;
    }

    @Operation(summary = "Initier un nouveau transfert", 
               description = "Crée un nouveau transfert bancaire avec validation IBAN/BIC et vérifications KYC/AML")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "201", description = "Transfert créé avec succès"),
        @ApiResponse(responseCode = "400", description = "Données invalides"),
        @ApiResponse(responseCode = "403", description = "Limites de transaction dépassées"),
        @ApiResponse(responseCode = "409", description = "Transfert en doublon")
    })
    @PostMapping
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<TransferResponse> createTransfer(
            @Valid @RequestBody TransferCreateRequest request,
            Authentication authentication) {
        
        String correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        
        try {
            logger.info("Initiation d'un nouveau transfert pour l'utilisateur: {}", authentication.getName());
            
            UUID userId = UUID.fromString(authentication.getName());
            Transfer transfer = transferService.createTransfer(userId, request, correlationId);
            
            auditService.logAction("TRANSFER", transfer.getId(), "CREATE", null, transfer, userId, correlationId);
            
            TransferResponse response = TransferResponse.fromEntity(transfer);
            
            logger.info("Transfert créé avec succès: {}", transfer.getReferenceNumber());
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
            
        } catch (Exception e) {
            logger.error("Erreur lors de la création du transfert", e);
            throw e;
        } finally {
            MDC.clear();
        }
    }

    @Operation(summary = "Obtenir un transfert par ID", 
               description = "Récupère les détails d'un transfert spécifique")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Transfert trouvé"),
        @ApiResponse(responseCode = "404", description = "Transfert non trouvé"),
        @ApiResponse(responseCode = "403", description = "Accès non autorisé")
    })
    @GetMapping("/{id}")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<TransferResponse> getTransfer(
            @Parameter(description = "ID du transfert") @PathVariable UUID id,
            Authentication authentication) {
        
        String correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        
        try {
            UUID userId = UUID.fromString(authentication.getName());
            Transfer transfer = transferService.getTransferById(id, userId);
            
            TransferResponse response = TransferResponse.fromEntity(transfer);
            return ResponseEntity.ok(response);
            
        } finally {
            MDC.clear();
        }
    }

    @Operation(summary = "Lister les transferts de l'utilisateur", 
               description = "Récupère la liste paginée des transferts de l'utilisateur connecté")
    @GetMapping
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<Page<TransferResponse>> getUserTransfers(
            @Parameter(description = "Statut du transfert") @RequestParam(required = false) Transfer.TransferStatus status,
            @Parameter(description = "Devise") @RequestParam(required = false) String currency,
            Pageable pageable,
            Authentication authentication) {
        
        String correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        
        try {
            UUID userId = UUID.fromString(authentication.getName());
            Page<Transfer> transfers = transferService.getUserTransfers(userId, status, currency, pageable);
            
            Page<TransferResponse> response = transfers.map(TransferResponse::fromEntity);
            return ResponseEntity.ok(response);
            
        } finally {
            MDC.clear();
        }
    }

    @Operation(summary = "Obtenir les événements d'un transfert", 
               description = "Récupère l'historique des événements d'un transfert pour le suivi")
    @GetMapping("/{id}/events")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<List<TransferEventResponse>> getTransferEvents(
            @Parameter(description = "ID du transfert") @PathVariable UUID id,
            Authentication authentication) {
        
        String correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        
        try {
            UUID userId = UUID.fromString(authentication.getName());
            List<TransferEventResponse> events = transferService.getTransferEvents(id, userId);
            
            return ResponseEntity.ok(events);
            
        } finally {
            MDC.clear();
        }
    }

    @Operation(summary = "Annuler un transfert", 
               description = "Annule un transfert en statut INITIATED ou PENDING")
    @ApiResponses(value = {
        @ApiResponse(responseCode = "200", description = "Transfert annulé"),
        @ApiResponse(responseCode = "400", description = "Transfert ne peut pas être annulé"),
        @ApiResponse(responseCode = "404", description = "Transfert non trouvé")
    })
    @PostMapping("/{id}/cancel")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<TransferResponse> cancelTransfer(
            @Parameter(description = "ID du transfert") @PathVariable UUID id,
            Authentication authentication) {
        
        String correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        
        try {
            logger.info("Demande d'annulation du transfert: {}", id);
            
            UUID userId = UUID.fromString(authentication.getName());
            Transfer transfer = transferService.cancelTransfer(id, userId, correlationId);
            
            auditService.logAction("TRANSFER", id, "CANCEL", null, transfer, userId, correlationId);
            
            TransferResponse response = TransferResponse.fromEntity(transfer);
            return ResponseEntity.ok(response);
            
        } finally {
            MDC.clear();
        }
    }

    @Operation(summary = "Relancer un transfert échoué", 
               description = "Relance un transfert en statut FAILED (admin/operator uniquement)")
    @PostMapping("/{id}/retry")
    @PreAuthorize("hasRole('OPERATOR')")
    public ResponseEntity<TransferResponse> retryTransfer(
            @Parameter(description = "ID du transfert") @PathVariable UUID id,
            Authentication authentication) {
        
        String correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        
        try {
            logger.info("Demande de relance du transfert: {}", id);
            
            UUID userId = UUID.fromString(authentication.getName());
            Transfer transfer = transferService.retryTransfer(id, correlationId);
            
            auditService.logAction("TRANSFER", id, "RETRY", null, transfer, userId, correlationId);
            
            TransferResponse response = TransferResponse.fromEntity(transfer);
            return ResponseEntity.ok(response);
            
        } finally {
            MDC.clear();
        }
    }

    @Operation(summary = "Calculer les frais de transfert", 
               description = "Calcule les frais pour un transfert sans l'initier")
    @PostMapping("/calculate-fees")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<FeeCalculationResponse> calculateFees(
            @Valid @RequestBody FeeCalculationRequest request,
            Authentication authentication) {
        
        String correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        
        try {
            FeeCalculationResponse response = transferService.calculateFees(request);
            return ResponseEntity.ok(response);
            
        } finally {
            MDC.clear();
        }
    }

    @Operation(summary = "Obtenir le statut en temps réel", 
               description = "Récupère le statut le plus récent d'un transfert depuis les systèmes externes")
    @GetMapping("/{id}/status")
    @PreAuthorize("hasRole('USER')")
    public ResponseEntity<TransferStatusResponse> getTransferStatus(
            @Parameter(description = "ID du transfert") @PathVariable UUID id,
            Authentication authentication) {
        
        String correlationId = UUID.randomUUID().toString();
        MDC.put("correlationId", correlationId);
        
        try {
            UUID userId = UUID.fromString(authentication.getName());
            TransferStatusResponse response = transferService.getTransferStatus(id, userId);
            
            return ResponseEntity.ok(response);
            
        } finally {
            MDC.clear();
        }
    }

    // DTOs internes pour ce contrôleur
    public static class FeeCalculationRequest {
        private String fromCountry;
        private String toCountry;
        private String currency;
        private BigDecimal amount;
        private boolean urgent;

        // Getters and setters
        public String getFromCountry() { return fromCountry; }
        public void setFromCountry(String fromCountry) { this.fromCountry = fromCountry; }
        public String getToCountry() { return toCountry; }
        public void setToCountry(String toCountry) { this.toCountry = toCountry; }
        public String getCurrency() { return currency; }
        public void setCurrency(String currency) { this.currency = currency; }
        public BigDecimal getAmount() { return amount; }
        public void setAmount(BigDecimal amount) { this.amount = amount; }
        public boolean isUrgent() { return urgent; }
        public void setUrgent(boolean urgent) { this.urgent = urgent; }
    }

    public static class FeeCalculationResponse {
        private BigDecimal feeAmount;
        private BigDecimal totalAmount;
        private String feeType;
        private String description;

        public FeeCalculationResponse(BigDecimal feeAmount, BigDecimal totalAmount, String feeType, String description) {
            this.feeAmount = feeAmount;
            this.totalAmount = totalAmount;
            this.feeType = feeType;
            this.description = description;
        }

        // Getters and setters
        public BigDecimal getFeeAmount() { return feeAmount; }
        public void setFeeAmount(BigDecimal feeAmount) { this.feeAmount = feeAmount; }
        public BigDecimal getTotalAmount() { return totalAmount; }
        public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
        public String getFeeType() { return feeType; }
        public void setFeeType(String feeType) { this.feeType = feeType; }
        public String getDescription() { return description; }
        public void setDescription(String description) { this.description = description; }
    }

    public static class TransferStatusResponse {
        private UUID transferId;
        private Transfer.TransferStatus status;
        private String statusDescription;
        private ZonedDateTime lastUpdated;
        private String externalReference;

        public TransferStatusResponse(UUID transferId, Transfer.TransferStatus status, String statusDescription, 
                                    ZonedDateTime lastUpdated, String externalReference) {
            this.transferId = transferId;
            this.status = status;
            this.statusDescription = statusDescription;
            this.lastUpdated = lastUpdated;
            this.externalReference = externalReference;
        }

        // Getters and setters
        public UUID getTransferId() { return transferId; }
        public void setTransferId(UUID transferId) { this.transferId = transferId; }
        public Transfer.TransferStatus getStatus() { return status; }
        public void setStatus(Transfer.TransferStatus status) { this.status = status; }
        public String getStatusDescription() { return statusDescription; }
        public void setStatusDescription(String statusDescription) { this.statusDescription = statusDescription; }
        public ZonedDateTime getLastUpdated() { return lastUpdated; }
        public void setLastUpdated(ZonedDateTime lastUpdated) { this.lastUpdated = lastUpdated; }
        public String getExternalReference() { return externalReference; }
        public void setExternalReference(String externalReference) { this.externalReference = externalReference; }
    }
}
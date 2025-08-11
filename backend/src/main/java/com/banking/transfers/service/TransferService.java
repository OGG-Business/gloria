package com.banking.transfers.service;

import com.banking.transfers.model.*;
import com.banking.transfers.repository.TransferRepository;
import com.banking.transfers.repository.AccountRepository;
import com.banking.transfers.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@Transactional
public class TransferService {

    @Autowired
    private TransferRepository transferRepository;

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AccountService accountService;

    @Autowired
    private AuditService auditService;

    @Autowired
    private SwiftConnectorService swiftConnectorService;

    @Autowired
    private MojaloopConnectorService mojaloopConnectorService;

    @Autowired
    private KycService kycService;

    /**
     * Créer un nouveau transfert
     */
    public Transfer createTransfer(Transfer transfer, UUID userId) {
        validateTransfer(transfer, userId);
        
        transfer.setId(UUID.randomUUID());
        transfer.setUserId(userId);
        transfer.setStatus(TransferStatus.INITIATED);
        transfer.setCreatedAt(LocalDateTime.now());
        transfer.setUpdatedAt(LocalDateTime.now());
        
        calculateFees(transfer);
        performComplianceChecks(transfer, userId);
        
        if (!accountService.hasSufficientFunds(transfer.getSourceAccountId(), transfer.getAmount())) {
            throw new IllegalStateException("Fonds insuffisants");
        }
        
        accountService.blockFunds(transfer.getSourceAccountId(), transfer.getAmount());
        
        Transfer savedTransfer = transferRepository.save(transfer);
        createTransferEvent(savedTransfer, EventType.CREATED, "Transfert créé");
        auditService.logTransferCreated(savedTransfer.getId(), userId, transfer.getAmount());
        
        return savedTransfer;
    }

    /**
     * Traiter un transfert
     */
    public Transfer processTransfer(UUID transferId) {
        Transfer transfer = transferRepository.findById(transferId)
                .orElseThrow(() -> new IllegalArgumentException("Transfert non trouvé"));

        if (transfer.getStatus() != TransferStatus.INITIATED) {
            throw new IllegalStateException("Transfert non traitable");
        }

        try {
            transfer.setStatus(TransferStatus.PENDING);
            transfer.setUpdatedAt(LocalDateTime.now());
            transferRepository.save(transfer);
            
            createTransferEvent(transfer, EventType.SENT, "Transfert envoyé");
            auditService.logTransferProcessed(transferId, transfer.getUserId(), transfer.getAmount());
            
        } catch (Exception e) {
            transfer.setStatus(TransferStatus.FAILED);
            transfer.setErrorDetails(e.getMessage());
            transferRepository.save(transfer);
            createTransferEvent(transfer, EventType.ERROR, "Erreur: " + e.getMessage());
            accountService.unblockFunds(transfer.getSourceAccountId(), transfer.getAmount());
        }

        return transfer;
    }

    /**
     * Finaliser un transfert
     */
    public Transfer finalizeTransfer(UUID transferId, TransferStatus status, String messageId, String errorDetails) {
        Transfer transfer = transferRepository.findById(transferId)
                .orElseThrow(() -> new IllegalArgumentException("Transfert non trouvé"));

        transfer.setStatus(status);
        transfer.setUpdatedAt(LocalDateTime.now());

        if (status == TransferStatus.COMPLETED) {
            accountService.debitAccount(transfer.getSourceAccountId(), transfer.getAmount(), 
                "Transfert vers " + transfer.getDestinationIban());
            accountService.unblockFunds(transfer.getSourceAccountId(), transfer.getAmount());
            transfer.setSwiftMessageId(messageId);
            createTransferEvent(transfer, EventType.COMPLETED, "Transfert complété");
            auditService.logTransferCompleted(transferId, transfer.getUserId(), transfer.getAmount());
        } else if (status == TransferStatus.FAILED) {
            accountService.unblockFunds(transfer.getSourceAccountId(), transfer.getAmount());
            transfer.setErrorDetails(errorDetails);
            createTransferEvent(transfer, EventType.ERROR, "Transfert échoué: " + errorDetails);
            auditService.logTransferFailed(transferId, transfer.getUserId(), transfer.getAmount(), errorDetails);
        }

        transferRepository.save(transfer);
        return transfer;
    }

    /**
     * Récupérer un transfert par ID
     */
    public Optional<Transfer> getTransferById(UUID transferId) {
        return transferRepository.findById(transferId);
    }

    /**
     * Récupérer les transferts d'un utilisateur
     */
    public List<Transfer> getTransfersByUserId(UUID userId) {
        return transferRepository.findByUserIdOrderByCreatedAtDesc(userId);
    }

    /**
     * Annuler un transfert
     */
    public Transfer cancelTransfer(UUID transferId, UUID userId) {
        Transfer transfer = transferRepository.findById(transferId)
                .orElseThrow(() -> new IllegalArgumentException("Transfert non trouvé"));

        if (!transfer.getUserId().equals(userId)) {
            throw new SecurityException("Accès non autorisé");
        }

        if (transfer.getStatus() != TransferStatus.INITIATED && transfer.getStatus() != TransferStatus.PENDING) {
            throw new IllegalStateException("Transfert non annulable");
        }

        transfer.setStatus(TransferStatus.CANCELLED);
        transfer.setUpdatedAt(LocalDateTime.now());
        transferRepository.save(transfer);

        accountService.unblockFunds(transfer.getSourceAccountId(), transfer.getAmount());
        createTransferEvent(transfer, EventType.CANCELLED, "Transfert annulé");
        auditService.logTransferCancelled(transferId, userId, transfer.getAmount());

        return transfer;
    }

    /**
     * Valider un transfert
     */
    private void validateTransfer(Transfer transfer, UUID userId) {
        if (transfer.getAmount() == null || transfer.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Montant invalide");
        }

        if (transfer.getSourceAccountId() == null) {
            throw new IllegalArgumentException("Compte source requis");
        }

        if (transfer.getDestinationIban() == null || transfer.getDestinationIban().trim().isEmpty()) {
            throw new IllegalArgumentException("IBAN de destination requis");
        }

        Account sourceAccount = accountRepository.findById(transfer.getSourceAccountId())
                .orElseThrow(() -> new IllegalArgumentException("Compte source non trouvé"));

        if (!sourceAccount.getOwnerId().equals(userId)) {
            throw new SecurityException("Accès non autorisé au compte");
        }

        if (sourceAccount.getStatus() != AccountStatus.ACTIVE) {
            throw new IllegalStateException("Compte non actif");
        }

        checkTransferLimits(transfer, userId);
    }

    /**
     * Vérifier les limites de transfert
     */
    private void checkTransferLimits(Transfer transfer, UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Utilisateur non trouvé"));

        BigDecimal singleLimit = BigDecimal.valueOf(user.getRiskLevel().getMaxTransactionLimit());
        if (transfer.getAmount().compareTo(singleLimit) > 0) {
            throw new IllegalStateException("Limite par transfert dépassée");
        }
    }

    /**
     * Calculer les frais de transfert
     */
    private void calculateFees(Transfer transfer) {
        BigDecimal fees = switch (transfer.getType()) {
            case SWIFT -> new BigDecimal("25.00");
            case MOJALOOP -> new BigDecimal("5.00");
            case SEPA -> new BigDecimal("3.00");
            default -> new BigDecimal("10.00");
        };

        transfer.setFees(fees);
        transfer.setTotalAmount(transfer.getAmount().add(fees));
    }

    /**
     * Effectuer les vérifications de conformité
     */
    private void performComplianceChecks(Transfer transfer, UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Utilisateur non trouvé"));

        if (user.getKycStatus() != KYCStatus.VERIFIED) {
            throw new IllegalStateException("KYC non vérifié");
        }

        if (user.getAmlStatus() != AMLStatus.PASSED) {
            throw new IllegalStateException("Vérification AML échouée");
        }

        if (user.getRiskLevel() == RiskLevel.CRITICAL) {
            throw new IllegalStateException("Transferts non autorisés");
        }
    }

    /**
     * Créer un événement de transfert
     */
    private void createTransferEvent(Transfer transfer, EventType eventType, String description) {
        TransferEvent event = new TransferEvent();
        event.setId(UUID.randomUUID());
        event.setTransferId(transfer.getId());
        event.setEventType(eventType);
        event.setDescription(description);
        event.setCreatedAt(LocalDateTime.now());
        event.setUserId(transfer.getUserId());
        // transferEventRepository.save(event);
    }

    /**
     * Récupérer les événements d'un transfert
     */
    public List<TransferEvent> getTransferEvents(UUID transferId) {
        return List.of();
    }
}
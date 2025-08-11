package com.banking.transfers.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

/**
 * Entité représentant un transfert bancaire
 */
@Entity
@Table(name = "transfers", indexes = {
    @Index(name = "idx_transfer_reference", columnList = "reference"),
    @Index(name = "idx_transfer_status", columnList = "status"),
    @Index(name = "idx_transfer_created_at", columnList = "created_at"),
    @Index(name = "idx_transfer_sender_account", columnList = "sender_account_id"),
    @Index(name = "idx_transfer_beneficiary_account", columnList = "beneficiary_account_id")
})
@EntityListeners(AuditingEntityListener.class)
public class Transfer {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "reference", unique = true, nullable = false, length = 50)
    @NotBlank(message = "La référence du transfert est obligatoire")
    @Pattern(regexp = "^[A-Z0-9]{1,50}$", message = "La référence doit contenir uniquement des lettres majuscules et chiffres")
    private String reference;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    @NotNull(message = "Le statut du transfert est obligatoire")
    private TransferStatus status;

    @Enumerated(EnumType.STRING)
    @Column(name = "type", nullable = false)
    @NotNull(message = "Le type de transfert est obligatoire")
    private TransferType type;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "sender_account_id", nullable = false)
    @NotNull(message = "Le compte émetteur est obligatoire")
    private Account senderAccount;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "beneficiary_account_id", nullable = false)
    @NotNull(message = "Le compte bénéficiaire est obligatoire")
    private Account beneficiaryAccount;

    @Column(name = "amount", nullable = false, precision = 19, scale = 4)
    @NotNull(message = "Le montant est obligatoire")
    @DecimalMin(value = "0.01", message = "Le montant doit être supérieur à 0")
    @DecimalMax(value = "999999999.9999", message = "Le montant ne peut pas dépasser 999,999,999.9999")
    private BigDecimal amount;

    @Column(name = "currency", nullable = false, length = 3)
    @NotBlank(message = "La devise est obligatoire")
    @Pattern(regexp = "^[A-Z]{3}$", message = "La devise doit être un code ISO 4217 à 3 lettres")
    private String currency;

    @Column(name = "exchange_rate", precision = 19, scale = 6)
    private BigDecimal exchangeRate;

    @Column(name = "fees", precision = 19, scale = 4)
    private BigDecimal fees;

    @Column(name = "total_amount", precision = 19, scale = 4)
    private BigDecimal totalAmount;

    @Column(name = "description", length = 140)
    @Size(max = 140, message = "La description ne peut pas dépasser 140 caractères")
    private String description;

    @Column(name = "purpose_code", length = 4)
    @Pattern(regexp = "^[A-Z0-9]{4}$", message = "Le code de finalité doit être à 4 caractères")
    private String purposeCode;

    @Column(name = "priority", length = 4)
    @Enumerated(EnumType.STRING)
    private TransferPriority priority;

    @Column(name = "execution_date")
    private LocalDateTime executionDate;

    @Column(name = "value_date")
    private LocalDateTime valueDate;

    @Column(name = "swift_message_id", length = 100)
    private String swiftMessageId;

    @Column(name = "iso_message_id", length = 100)
    private String isoMessageId;

    @Column(name = "connector_type", length = 20)
    @Enumerated(EnumType.STRING)
    private ConnectorType connectorType;

    @Column(name = "connector_reference", length = 100)
    private String connectorReference;

    @Column(name = "error_code", length = 10)
    private String errorCode;

    @Column(name = "error_message", length = 500)
    private String errorMessage;

    @Column(name = "kyc_status", length = 20)
    @Enumerated(EnumType.STRING)
    private KYCStatus kycStatus;

    @Column(name = "aml_status", length = 20)
    @Enumerated(EnumType.STRING)
    private AMLStatus amlStatus;

    @Column(name = "risk_score")
    private Integer riskScore;

    @Column(name = "dry_run", nullable = false)
    private boolean dryRun = false;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    @Column(name = "created_by", length = 100)
    private String createdBy;

    @Column(name = "updated_by", length = 100)
    private String updatedBy;

    @OneToMany(mappedBy = "transfer", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    @OrderBy("createdAt ASC")
    private List<TransferEvent> events = new ArrayList<>();

    // Constructeurs
    public Transfer() {}

    public Transfer(String reference, TransferType type, Account senderAccount, 
                   Account beneficiaryAccount, BigDecimal amount, String currency) {
        this.reference = reference;
        this.type = type;
        this.senderAccount = senderAccount;
        this.beneficiaryAccount = beneficiaryAccount;
        this.amount = amount;
        this.currency = currency;
        this.status = TransferStatus.INITIATED;
    }

    // Méthodes utilitaires
    public void addEvent(TransferEvent event) {
        this.events.add(event);
        event.setTransfer(this);
    }

    public boolean isCompleted() {
        return TransferStatus.COMPLETED.equals(this.status);
    }

    public boolean isFailed() {
        return TransferStatus.FAILED.equals(this.status);
    }

    public boolean isPending() {
        return TransferStatus.PENDING.equals(this.status);
    }

    public boolean canBeCancelled() {
        return TransferStatus.INITIATED.equals(this.status) || 
               TransferStatus.PENDING.equals(this.status);
    }

    // Getters et Setters
    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getReference() { return reference; }
    public void setReference(String reference) { this.reference = reference; }

    public TransferStatus getStatus() { return status; }
    public void setStatus(TransferStatus status) { this.status = status; }

    public TransferType getType() { return type; }
    public void setType(TransferType type) { this.type = type; }

    public Account getSenderAccount() { return senderAccount; }
    public void setSenderAccount(Account senderAccount) { this.senderAccount = senderAccount; }

    public Account getBeneficiaryAccount() { return beneficiaryAccount; }
    public void setBeneficiaryAccount(Account beneficiaryAccount) { this.beneficiaryAccount = beneficiaryAccount; }

    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }

    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }

    public BigDecimal getExchangeRate() { return exchangeRate; }
    public void setExchangeRate(BigDecimal exchangeRate) { this.exchangeRate = exchangeRate; }

    public BigDecimal getFees() { return fees; }
    public void setFees(BigDecimal fees) { this.fees = fees; }

    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getPurposeCode() { return purposeCode; }
    public void setPurposeCode(String purposeCode) { this.purposeCode = purposeCode; }

    public TransferPriority getPriority() { return priority; }
    public void setPriority(TransferPriority priority) { this.priority = priority; }

    public LocalDateTime getExecutionDate() { return executionDate; }
    public void setExecutionDate(LocalDateTime executionDate) { this.executionDate = executionDate; }

    public LocalDateTime getValueDate() { return valueDate; }
    public void setValueDate(LocalDateTime valueDate) { this.valueDate = valueDate; }

    public String getSwiftMessageId() { return swiftMessageId; }
    public void setSwiftMessageId(String swiftMessageId) { this.swiftMessageId = swiftMessageId; }

    public String getIsoMessageId() { return isoMessageId; }
    public void setIsoMessageId(String isoMessageId) { this.isoMessageId = isoMessageId; }

    public ConnectorType getConnectorType() { return connectorType; }
    public void setConnectorType(ConnectorType connectorType) { this.connectorType = connectorType; }

    public String getConnectorReference() { return connectorReference; }
    public void setConnectorReference(String connectorReference) { this.connectorReference = connectorReference; }

    public String getErrorCode() { return errorCode; }
    public void setErrorCode(String errorCode) { this.errorCode = errorCode; }

    public String getErrorMessage() { return errorMessage; }
    public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }

    public KYCStatus getKycStatus() { return kycStatus; }
    public void setKycStatus(KYCStatus kycStatus) { this.kycStatus = kycStatus; }

    public AMLStatus getAmlStatus() { return amlStatus; }
    public void setAmlStatus(AMLStatus amlStatus) { this.amlStatus = amlStatus; }

    public Integer getRiskScore() { return riskScore; }
    public void setRiskScore(Integer riskScore) { this.riskScore = riskScore; }

    public boolean isDryRun() { return dryRun; }
    public void setDryRun(boolean dryRun) { this.dryRun = dryRun; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }

    public String getUpdatedBy() { return updatedBy; }
    public void setUpdatedBy(String updatedBy) { this.updatedBy = updatedBy; }

    public List<TransferEvent> getEvents() { return events; }
    public void setEvents(List<TransferEvent> events) { this.events = events; }

    @Override
    public String toString() {
        return "Transfer{" +
                "id=" + id +
                ", reference='" + reference + '\'' +
                ", status=" + status +
                ", type=" + type +
                ", amount=" + amount +
                ", currency='" + currency + '\'' +
                ", createdAt=" + createdAt +
                '}';
    }
}
package com.swiftpay.model.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.ZonedDateTime;
import java.util.UUID;

/**
 * Entité représentant un transfert bancaire
 */
@Entity
@Table(name = "transfers")
public class Transfer {

    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @NotBlank
    @Size(max = 50)
    @Column(name = "reference_number", unique = true, nullable = false)
    private String referenceNumber;

    @NotNull
    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @NotNull
    @Column(name = "from_account_id", nullable = false)
    private UUID fromAccountId;

    @Column(name = "to_account_id")
    private UUID toAccountId;

    // Recipient details for external transfers
    @Size(max = 255)
    @Column(name = "recipient_name")
    private String recipientName;

    @Size(max = 34)
    @Column(name = "recipient_iban")
    private String recipientIban;

    @Size(max = 11)
    @Column(name = "recipient_bic")
    private String recipientBic;

    @Size(max = 50)
    @Column(name = "recipient_account_number")
    private String recipientAccountNumber;

    @Size(max = 255)
    @Column(name = "recipient_bank_name")
    private String recipientBankName;

    @Column(name = "recipient_bank_address")
    private String recipientBankAddress;

    @Size(max = 3)
    @Column(name = "recipient_country_code")
    private String recipientCountryCode;

    // Transfer details
    @NotNull
    @DecimalMin(value = "0.01")
    @Column(nullable = false, precision = 15, scale = 2)
    private BigDecimal amount;

    @NotBlank
    @Size(max = 3)
    @Column(nullable = false)
    private String currency;

    @Column(name = "exchange_rate", precision = 10, scale = 6)
    private BigDecimal exchangeRate;

    @Column(name = "fee_amount", precision = 15, scale = 2)
    private BigDecimal feeAmount = BigDecimal.ZERO;

    @NotNull
    @Column(name = "total_amount", nullable = false, precision = 15, scale = 2)
    private BigDecimal totalAmount;

    // Transfer metadata
    @Size(max = 10)
    @Column(name = "purpose_code")
    private String purposeCode;

    @Column(name = "remittance_info")
    private String remittanceInfo;

    private Boolean urgent = false;

    // Status and timing
    @Enumerated(EnumType.STRING)
    @NotNull
    private TransferStatus status = TransferStatus.INITIATED;

    @Column(name = "initiated_at")
    private ZonedDateTime initiatedAt;

    @Column(name = "processed_at")
    private ZonedDateTime processedAt;

    @Column(name = "completed_at")
    private ZonedDateTime completedAt;

    @Column(name = "expected_completion_date")
    private LocalDate expectedCompletionDate;

    // External system references
    @Size(max = 100)
    @Column(name = "swift_message_id")
    private String swiftMessageId;

    @Size(max = 100)
    @Column(name = "mojaloop_transaction_id")
    private String mojaloopTransactionId;

    @Size(max = 100)
    @Column(name = "bank_reference")
    private String bankReference;

    // Error handling
    @Size(max = 50)
    @Column(name = "error_code")
    private String errorCode;

    @Column(name = "error_message")
    private String errorMessage;

    @Column(name = "retry_count")
    private Integer retryCount = 0;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private ZonedDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private ZonedDateTime updatedAt;

    // Constructors
    public Transfer() {}

    public Transfer(UUID userId, UUID fromAccountId, BigDecimal amount, String currency) {
        this.userId = userId;
        this.fromAccountId = fromAccountId;
        this.amount = amount;
        this.currency = currency;
        this.totalAmount = amount;
        this.initiatedAt = ZonedDateTime.now();
        this.referenceNumber = generateReferenceNumber();
    }

    // Business methods
    public void updateStatus(TransferStatus newStatus) {
        this.status = newStatus;
        
        switch (newStatus) {
            case PROCESSING:
                this.processedAt = ZonedDateTime.now();
                break;
            case COMPLETED:
                this.completedAt = ZonedDateTime.now();
                break;
            case FAILED:
                this.retryCount++;
                break;
        }
    }

    public boolean isCompleted() {
        return status == TransferStatus.COMPLETED;
    }

    public boolean isFailed() {
        return status == TransferStatus.FAILED;
    }

    public boolean canRetry() {
        return status == TransferStatus.FAILED && retryCount < 3;
    }

    public boolean isExternalTransfer() {
        return toAccountId == null;
    }

    private String generateReferenceNumber() {
        return "SP" + System.currentTimeMillis() + UUID.randomUUID().toString().substring(0, 8).toUpperCase();
    }

    // Getters and Setters
    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getReferenceNumber() {
        return referenceNumber;
    }

    public void setReferenceNumber(String referenceNumber) {
        this.referenceNumber = referenceNumber;
    }

    public UUID getUserId() {
        return userId;
    }

    public void setUserId(UUID userId) {
        this.userId = userId;
    }

    public UUID getFromAccountId() {
        return fromAccountId;
    }

    public void setFromAccountId(UUID fromAccountId) {
        this.fromAccountId = fromAccountId;
    }

    public UUID getToAccountId() {
        return toAccountId;
    }

    public void setToAccountId(UUID toAccountId) {
        this.toAccountId = toAccountId;
    }

    public String getRecipientName() {
        return recipientName;
    }

    public void setRecipientName(String recipientName) {
        this.recipientName = recipientName;
    }

    public String getRecipientIban() {
        return recipientIban;
    }

    public void setRecipientIban(String recipientIban) {
        this.recipientIban = recipientIban;
    }

    public String getRecipientBic() {
        return recipientBic;
    }

    public void setRecipientBic(String recipientBic) {
        this.recipientBic = recipientBic;
    }

    public String getRecipientAccountNumber() {
        return recipientAccountNumber;
    }

    public void setRecipientAccountNumber(String recipientAccountNumber) {
        this.recipientAccountNumber = recipientAccountNumber;
    }

    public String getRecipientBankName() {
        return recipientBankName;
    }

    public void setRecipientBankName(String recipientBankName) {
        this.recipientBankName = recipientBankName;
    }

    public String getRecipientBankAddress() {
        return recipientBankAddress;
    }

    public void setRecipientBankAddress(String recipientBankAddress) {
        this.recipientBankAddress = recipientBankAddress;
    }

    public String getRecipientCountryCode() {
        return recipientCountryCode;
    }

    public void setRecipientCountryCode(String recipientCountryCode) {
        this.recipientCountryCode = recipientCountryCode;
    }

    public BigDecimal getAmount() {
        return amount;
    }

    public void setAmount(BigDecimal amount) {
        this.amount = amount;
    }

    public String getCurrency() {
        return currency;
    }

    public void setCurrency(String currency) {
        this.currency = currency;
    }

    public BigDecimal getExchangeRate() {
        return exchangeRate;
    }

    public void setExchangeRate(BigDecimal exchangeRate) {
        this.exchangeRate = exchangeRate;
    }

    public BigDecimal getFeeAmount() {
        return feeAmount;
    }

    public void setFeeAmount(BigDecimal feeAmount) {
        this.feeAmount = feeAmount;
    }

    public BigDecimal getTotalAmount() {
        return totalAmount;
    }

    public void setTotalAmount(BigDecimal totalAmount) {
        this.totalAmount = totalAmount;
    }

    public String getPurposeCode() {
        return purposeCode;
    }

    public void setPurposeCode(String purposeCode) {
        this.purposeCode = purposeCode;
    }

    public String getRemittanceInfo() {
        return remittanceInfo;
    }

    public void setRemittanceInfo(String remittanceInfo) {
        this.remittanceInfo = remittanceInfo;
    }

    public Boolean getUrgent() {
        return urgent;
    }

    public void setUrgent(Boolean urgent) {
        this.urgent = urgent;
    }

    public TransferStatus getStatus() {
        return status;
    }

    public void setStatus(TransferStatus status) {
        this.status = status;
    }

    public ZonedDateTime getInitiatedAt() {
        return initiatedAt;
    }

    public void setInitiatedAt(ZonedDateTime initiatedAt) {
        this.initiatedAt = initiatedAt;
    }

    public ZonedDateTime getProcessedAt() {
        return processedAt;
    }

    public void setProcessedAt(ZonedDateTime processedAt) {
        this.processedAt = processedAt;
    }

    public ZonedDateTime getCompletedAt() {
        return completedAt;
    }

    public void setCompletedAt(ZonedDateTime completedAt) {
        this.completedAt = completedAt;
    }

    public LocalDate getExpectedCompletionDate() {
        return expectedCompletionDate;
    }

    public void setExpectedCompletionDate(LocalDate expectedCompletionDate) {
        this.expectedCompletionDate = expectedCompletionDate;
    }

    public String getSwiftMessageId() {
        return swiftMessageId;
    }

    public void setSwiftMessageId(String swiftMessageId) {
        this.swiftMessageId = swiftMessageId;
    }

    public String getMojaloopTransactionId() {
        return mojaloopTransactionId;
    }

    public void setMojaloopTransactionId(String mojaloopTransactionId) {
        this.mojaloopTransactionId = mojaloopTransactionId;
    }

    public String getBankReference() {
        return bankReference;
    }

    public void setBankReference(String bankReference) {
        this.bankReference = bankReference;
    }

    public String getErrorCode() {
        return errorCode;
    }

    public void setErrorCode(String errorCode) {
        this.errorCode = errorCode;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public Integer getRetryCount() {
        return retryCount;
    }

    public void setRetryCount(Integer retryCount) {
        this.retryCount = retryCount;
    }

    public ZonedDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(ZonedDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public ZonedDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(ZonedDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

    // Enums
    public enum TransferStatus {
        INITIATED, PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED
    }
}
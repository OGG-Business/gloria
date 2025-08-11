package com.banking.transfers.model;

import jakarta.persistence.*;
import jakarta.validation.constraints.*;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

/**
 * Entité représentant un compte bancaire
 */
@Entity
@Table(name = "accounts", indexes = {
    @Index(name = "idx_account_iban", columnList = "iban"),
    @Index(name = "idx_account_bic", columnList = "bic"),
    @Index(name = "idx_account_owner", columnList = "owner_id"),
    @Index(name = "idx_account_status", columnList = "status")
})
@EntityListeners(AuditingEntityListener.class)
public class Account {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(name = "account_number", unique = true, nullable = false, length = 50)
    @NotBlank(message = "Le numéro de compte est obligatoire")
    @Pattern(regexp = "^[A-Z0-9]{1,50}$", message = "Le numéro de compte doit contenir uniquement des lettres majuscules et chiffres")
    private String accountNumber;

    @Column(name = "iban", unique = true, length = 34)
    @Pattern(regexp = "^[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}$", 
             message = "L'IBAN doit être au format ISO 13616")
    private String iban;

    @Column(name = "bic", length = 11)
    @Pattern(regexp = "^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$", 
             message = "Le BIC doit être au format ISO 9362")
    private String bic;

    @Column(name = "account_name", nullable = false, length = 100)
    @NotBlank(message = "Le nom du compte est obligatoire")
    @Size(max = 100, message = "Le nom du compte ne peut pas dépasser 100 caractères")
    private String accountName;

    @Column(name = "account_type", nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    @NotNull(message = "Le type de compte est obligatoire")
    private AccountType accountType;

    @Column(name = "currency", nullable = false, length = 3)
    @NotBlank(message = "La devise est obligatoire")
    @Pattern(regexp = "^[A-Z]{3}$", message = "La devise doit être un code ISO 4217 à 3 lettres")
    private String currency;

    @Column(name = "balance", nullable = false, precision = 19, scale = 4)
    @NotNull(message = "Le solde est obligatoire")
    @DecimalMin(value = "0", message = "Le solde ne peut pas être négatif")
    private BigDecimal balance;

    @Column(name = "available_balance", nullable = false, precision = 19, scale = 4)
    @NotNull(message = "Le solde disponible est obligatoire")
    @DecimalMin(value = "0", message = "Le solde disponible ne peut pas être négatif")
    private BigDecimal availableBalance;

    @Column(name = "credit_limit", precision = 19, scale = 4)
    @DecimalMin(value = "0", message = "La limite de crédit ne peut pas être négative")
    private BigDecimal creditLimit;

    @Column(name = "status", nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    @NotNull(message = "Le statut du compte est obligatoire")
    private AccountStatus status;

    @Column(name = "country_code", nullable = false, length = 2)
    @NotBlank(message = "Le code pays est obligatoire")
    @Pattern(regexp = "^[A-Z]{2}$", message = "Le code pays doit être un code ISO 3166-1 alpha-2")
    private String countryCode;

    @Column(name = "bank_code", length = 20)
    private String bankCode;

    @Column(name = "branch_code", length = 20)
    private String branchCode;

    @Column(name = "owner_id", nullable = false)
    @NotNull(message = "L'identifiant du propriétaire est obligatoire")
    private UUID ownerId;

    @Column(name = "owner_name", nullable = false, length = 100)
    @NotBlank(message = "Le nom du propriétaire est obligatoire")
    @Size(max = 100, message = "Le nom du propriétaire ne peut pas dépasser 100 caractères")
    private String ownerName;

    @Column(name = "owner_type", nullable = false, length = 20)
    @Enumerated(EnumType.STRING)
    @NotNull(message = "Le type de propriétaire est obligatoire")
    private OwnerType ownerType;

    @Column(name = "kyc_status", length = 20)
    @Enumerated(EnumType.STRING)
    private KYCStatus kycStatus;

    @Column(name = "aml_status", length = 20)
    @Enumerated(EnumType.STRING)
    private AMLStatus amlStatus;

    @Column(name = "risk_score")
    @Min(value = 0, message = "Le score de risque ne peut pas être négatif")
    @Max(value = 100, message = "Le score de risque ne peut pas dépasser 100")
    private Integer riskScore;

    @Column(name = "daily_limit", precision = 19, scale = 4)
    @DecimalMin(value = "0", message = "La limite quotidienne ne peut pas être négative")
    private BigDecimal dailyLimit;

    @Column(name = "monthly_limit", precision = 19, scale = 4)
    @DecimalMin(value = "0", message = "La limite mensuelle ne peut pas être négative")
    private BigDecimal monthlyLimit;

    @Column(name = "opening_date")
    private LocalDateTime openingDate;

    @Column(name = "last_activity_date")
    private LocalDateTime lastActivityDate;

    @Column(name = "is_active", nullable = false)
    private boolean active = true;

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

    // Constructeurs
    public Account() {}

    public Account(String accountNumber, String accountName, AccountType accountType, 
                  String currency, BigDecimal balance, String countryCode, 
                  UUID ownerId, String ownerName, OwnerType ownerType) {
        this.accountNumber = accountNumber;
        this.accountName = accountName;
        this.accountType = accountType;
        this.currency = currency;
        this.balance = balance;
        this.availableBalance = balance;
        this.countryCode = countryCode;
        this.ownerId = ownerId;
        this.ownerName = ownerName;
        this.ownerType = ownerType;
        this.status = AccountStatus.ACTIVE;
    }

    // Méthodes utilitaires
    public boolean hasSufficientFunds(BigDecimal amount) {
        return this.availableBalance.compareTo(amount) >= 0;
    }

    public void debit(BigDecimal amount) {
        if (!hasSufficientFunds(amount)) {
            throw new IllegalArgumentException("Fonds insuffisants");
        }
        this.balance = this.balance.subtract(amount);
        this.availableBalance = this.availableBalance.subtract(amount);
    }

    public void credit(BigDecimal amount) {
        this.balance = this.balance.add(amount);
        this.availableBalance = this.availableBalance.add(amount);
    }

    public boolean isActive() {
        return this.active && AccountStatus.ACTIVE.equals(this.status);
    }

    public boolean isInternational() {
        return this.iban != null && this.bic != null;
    }

    public boolean isDomestic() {
        return this.iban == null || this.bic == null;
    }

    // Getters et Setters
    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getAccountNumber() { return accountNumber; }
    public void setAccountNumber(String accountNumber) { this.accountNumber = accountNumber; }

    public String getIban() { return iban; }
    public void setIban(String iban) { this.iban = iban; }

    public String getBic() { return bic; }
    public void setBic(String bic) { this.bic = bic; }

    public String getAccountName() { return accountName; }
    public void setAccountName(String accountName) { this.accountName = accountName; }

    public AccountType getAccountType() { return accountType; }
    public void setAccountType(AccountType accountType) { this.accountType = accountType; }

    public String getCurrency() { return currency; }
    public void setCurrency(String currency) { this.currency = currency; }

    public BigDecimal getBalance() { return balance; }
    public void setBalance(BigDecimal balance) { this.balance = balance; }

    public BigDecimal getAvailableBalance() { return availableBalance; }
    public void setAvailableBalance(BigDecimal availableBalance) { this.availableBalance = availableBalance; }

    public BigDecimal getCreditLimit() { return creditLimit; }
    public void setCreditLimit(BigDecimal creditLimit) { this.creditLimit = creditLimit; }

    public AccountStatus getStatus() { return status; }
    public void setStatus(AccountStatus status) { this.status = status; }

    public String getCountryCode() { return countryCode; }
    public void setCountryCode(String countryCode) { this.countryCode = countryCode; }

    public String getBankCode() { return bankCode; }
    public void setBankCode(String bankCode) { this.bankCode = bankCode; }

    public String getBranchCode() { return branchCode; }
    public void setBranchCode(String branchCode) { this.branchCode = branchCode; }

    public UUID getOwnerId() { return ownerId; }
    public void setOwnerId(UUID ownerId) { this.ownerId = ownerId; }

    public String getOwnerName() { return ownerName; }
    public void setOwnerName(String ownerName) { this.ownerName = ownerName; }

    public OwnerType getOwnerType() { return ownerType; }
    public void setOwnerType(OwnerType ownerType) { this.ownerType = ownerType; }

    public KYCStatus getKycStatus() { return kycStatus; }
    public void setKycStatus(KYCStatus kycStatus) { this.kycStatus = kycStatus; }

    public AMLStatus getAmlStatus() { return amlStatus; }
    public void setAmlStatus(AMLStatus amlStatus) { this.amlStatus = amlStatus; }

    public Integer getRiskScore() { return riskScore; }
    public void setRiskScore(Integer riskScore) { this.riskScore = riskScore; }

    public BigDecimal getDailyLimit() { return dailyLimit; }
    public void setDailyLimit(BigDecimal dailyLimit) { this.dailyLimit = dailyLimit; }

    public BigDecimal getMonthlyLimit() { return monthlyLimit; }
    public void setMonthlyLimit(BigDecimal monthlyLimit) { this.monthlyLimit = monthlyLimit; }

    public LocalDateTime getOpeningDate() { return openingDate; }
    public void setOpeningDate(LocalDateTime openingDate) { this.openingDate = openingDate; }

    public LocalDateTime getLastActivityDate() { return lastActivityDate; }
    public void setLastActivityDate(LocalDateTime lastActivityDate) { this.lastActivityDate = lastActivityDate; }

    public boolean getActive() { return active; }
    public void setActive(boolean active) { this.active = active; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }

    public String getCreatedBy() { return createdBy; }
    public void setCreatedBy(String createdBy) { this.createdBy = createdBy; }

    public String getUpdatedBy() { return updatedBy; }
    public void setUpdatedBy(String updatedBy) { this.updatedBy = updatedBy; }

    @Override
    public String toString() {
        return "Account{" +
                "id=" + id +
                ", accountNumber='" + accountNumber + '\'' +
                ", iban='" + iban + '\'' +
                ", accountName='" + accountName + '\'' +
                ", currency='" + currency + '\'' +
                ", balance=" + balance +
                ", status=" + status +
                '}';
    }
}
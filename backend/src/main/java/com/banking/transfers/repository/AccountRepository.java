package com.banking.transfers.repository;

import com.banking.transfers.model.Account;
import com.banking.transfers.model.AccountStatus;
import com.banking.transfers.model.AccountType;
import com.banking.transfers.model.OwnerType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface AccountRepository extends JpaRepository<Account, UUID> {

    // Recherche par propriétaire
    List<Account> findByOwnerId(UUID ownerId);
    List<Account> findByOwnerIdAndStatus(UUID ownerId, AccountStatus status);
    
    // Recherche par IBAN
    Optional<Account> findByIban(String iban);
    boolean existsByIban(String iban);
    
    // Recherche par type de compte
    List<Account> findByAccountType(AccountType accountType);
    List<Account> findByOwnerIdAndAccountType(UUID ownerId, AccountType accountType);
    
    // Recherche par devise
    List<Account> findByCurrency(String currency);
    List<Account> findByOwnerIdAndCurrency(UUID ownerId, String currency);
    
    // Recherche par statut
    List<Account> findByStatus(AccountStatus status);
    long countByStatus(AccountStatus status);
    
    // Recherche par type de propriétaire
    List<Account> findByOwnerType(OwnerType ownerType);
    
    // Recherche par pays
    List<Account> findByCountry(String country);
    List<Account> findByOwnerIdAndCountry(UUID ownerId, String country);
    
    // Recherche par solde
    List<Account> findByBalanceGreaterThan(BigDecimal amount);
    List<Account> findByBalanceLessThan(BigDecimal amount);
    List<Account> findByBalanceBetween(BigDecimal minAmount, BigDecimal maxAmount);
    
    // Recherche par date de création
    List<Account> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate);
    List<Account> findByCreatedAtAfter(LocalDateTime date);
    List<Account> findByCreatedAtBefore(LocalDateTime date);
    
    // Recherche par nom de compte
    List<Account> findByAccountNameContainingIgnoreCase(String accountName);
    List<Account> findByOwnerIdAndAccountNameContainingIgnoreCase(UUID ownerId, String accountName);
    
    // Recherche par description
    List<Account> findByDescriptionContainingIgnoreCase(String description);
    
    // Recherche par banque
    List<Account> findByBankNameContainingIgnoreCase(String bankName);
    List<Account> findByBicContainingIgnoreCase(String bic);
    
    // Recherche par numéro de compte
    List<Account> findByAccountNumberContaining(String accountNumber);
    
    // Recherche par limites
    List<Account> findByDailyLimitGreaterThan(BigDecimal limit);
    List<Account> findByMonthlyLimitGreaterThan(BigDecimal limit);
    List<Account> findBySingleLimitGreaterThan(BigDecimal limit);
    
    // Recherche par montant bloqué
    List<Account> findByBlockedAmountGreaterThan(BigDecimal amount);
    
    // Recherche combinée
    @Query("SELECT a FROM Account a WHERE " +
           "(:ownerId IS NULL OR a.ownerId = :ownerId) AND " +
           "(:accountType IS NULL OR a.accountType = :accountType) AND " +
           "(:currency IS NULL OR a.currency = :currency) AND " +
           "(:status IS NULL OR a.status = :status) AND " +
           "(:country IS NULL OR a.country = :country) AND " +
           "(:minBalance IS NULL OR a.balance >= :minBalance) AND " +
           "(:maxBalance IS NULL OR a.balance <= :maxBalance)")
    Page<Account> findByMultipleCriteria(
            @Param("ownerId") UUID ownerId,
            @Param("accountType") AccountType accountType,
            @Param("currency") String currency,
            @Param("status") AccountStatus status,
            @Param("country") String country,
            @Param("minBalance") BigDecimal minBalance,
            @Param("maxBalance") BigDecimal maxBalance,
            Pageable pageable
    );
    
    // Statistiques
    @Query("SELECT COUNT(a) FROM Account a WHERE a.status = :status")
    long countByStatus(@Param("status") AccountStatus status);
    
    @Query("SELECT COUNT(a) FROM Account a WHERE a.ownerId = :ownerId AND a.status = :status")
    long countByOwnerIdAndStatus(@Param("ownerId") UUID ownerId, @Param("status") AccountStatus status);
    
    @Query("SELECT SUM(a.balance) FROM Account a WHERE a.ownerId = :ownerId AND a.currency = :currency")
    BigDecimal sumBalanceByOwnerIdAndCurrency(@Param("ownerId") UUID ownerId, @Param("currency") String currency);
    
    @Query("SELECT SUM(a.balance) FROM Account a WHERE a.currency = :currency")
    BigDecimal sumBalanceByCurrency(@Param("currency") String currency);
    
    // Recherche de comptes avec solde insuffisant
    @Query("SELECT a FROM Account a WHERE a.availableBalance < :requiredAmount")
    List<Account> findAccountsWithInsufficientFunds(@Param("requiredAmount") BigDecimal requiredAmount);
    
    // Recherche de comptes actifs par devise
    @Query("SELECT a FROM Account a WHERE a.status = 'ACTIVE' AND a.currency = :currency")
    List<Account> findActiveAccountsByCurrency(@Param("currency") String currency);
    
    // Recherche de comptes par plage de solde
    @Query("SELECT a FROM Account a WHERE a.balance BETWEEN :minAmount AND :maxAmount")
    List<Account> findAccountsByBalanceRange(@Param("minAmount") BigDecimal minAmount, @Param("maxAmount") BigDecimal maxAmount);
    
    // Recherche de comptes créés récemment
    @Query("SELECT a FROM Account a WHERE a.createdAt >= :since")
    List<Account> findAccountsCreatedSince(@Param("since") LocalDateTime since);
    
    // Recherche de comptes mis à jour récemment
    @Query("SELECT a FROM Account a WHERE a.updatedAt >= :since")
    List<Account> findAccountsUpdatedSince(@Param("since") LocalDateTime since);
    
    // Recherche de comptes par nom de banque et pays
    @Query("SELECT a FROM Account a WHERE a.bankName = :bankName AND a.country = :country")
    List<Account> findByBankNameAndCountry(@Param("bankName") String bankName, @Param("country") String country);
    
    // Recherche de comptes par BIC
    @Query("SELECT a FROM Account a WHERE a.bic = :bic")
    List<Account> findByBic(@Param("bic") String bic);
    
    // Recherche de comptes avec des fonds bloqués
    @Query("SELECT a FROM Account a WHERE a.blockedAmount > 0")
    List<Account> findAccountsWithBlockedFunds();
    
    // Recherche de comptes par limite quotidienne
    @Query("SELECT a FROM Account a WHERE a.dailyLimit >= :limit")
    List<Account> findAccountsByDailyLimit(@Param("limit") BigDecimal limit);
    
    // Recherche de comptes par limite mensuelle
    @Query("SELECT a FROM Account a WHERE a.monthlyLimit >= :limit")
    List<Account> findAccountsByMonthlyLimit(@Param("limit") BigDecimal limit);
}
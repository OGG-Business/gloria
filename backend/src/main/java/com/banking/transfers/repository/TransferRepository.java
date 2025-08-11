package com.banking.transfers.repository;

import com.banking.transfers.model.Transfer;
import com.banking.transfers.model.TransferStatus;
import com.banking.transfers.model.TransferType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface TransferRepository extends JpaRepository<Transfer, UUID> {

    // Recherche par utilisateur
    List<Transfer> findByUserIdOrderByCreatedAtDesc(UUID userId);
    List<Transfer> findByUserIdAndStatusOrderByCreatedAtDesc(UUID userId, TransferStatus status);
    
    // Recherche par compte source
    List<Transfer> findBySourceAccountIdOrderByCreatedAtDesc(UUID accountId);
    List<Transfer> findBySourceAccountIdAndStatusOrderByCreatedAtDesc(UUID accountId, TransferStatus status);
    
    // Recherche par statut
    List<Transfer> findByStatus(TransferStatus status);
    List<Transfer> findByStatusOrderByCreatedAtDesc(TransferStatus status);
    
    // Recherche par type de transfert
    List<Transfer> findByType(TransferType type);
    List<Transfer> findByUserIdAndTypeOrderByCreatedAtDesc(UUID userId, TransferType type);
    
    // Recherche par devise
    List<Transfer> findByCurrency(String currency);
    List<Transfer> findByUserIdAndCurrencyOrderByCreatedAtDesc(UUID userId, String currency);
    
    // Recherche par montant
    List<Transfer> findByAmountGreaterThan(BigDecimal amount);
    List<Transfer> findByAmountLessThan(BigDecimal amount);
    List<Transfer> findByAmountBetween(BigDecimal minAmount, BigDecimal maxAmount);
    
    // Recherche par date de création
    List<Transfer> findByCreatedAtBetween(LocalDateTime startDate, LocalDateTime endDate);
    List<Transfer> findByCreatedAtAfter(LocalDateTime date);
    List<Transfer> findByCreatedAtBefore(LocalDateTime date);
    
    // Recherche par IBAN de destination
    List<Transfer> findByDestinationIbanContaining(String iban);
    List<Transfer> findByDestinationIban(String iban);
    
    // Recherche par message SWIFT
    List<Transfer> findBySwiftMessageId(String messageId);
    Optional<Transfer> findBySwiftMessageIdAndStatus(String messageId, TransferStatus status);
    
    // Recherche par priorité
    List<Transfer> findByPriority(TransferPriority priority);
    List<Transfer> findByUserIdAndPriorityOrderByCreatedAtDesc(UUID userId, TransferPriority priority);
    
    // Recherche par description
    List<Transfer> findByDescriptionContainingIgnoreCase(String description);
    
    // Recherche par BIC de destination
    List<Transfer> findByDestinationBic(String bic);
    
    // Recherche par nom du bénéficiaire
    List<Transfer> findByBeneficiaryNameContainingIgnoreCase(String beneficiaryName);
    
    // Recherche par pays de destination
    List<Transfer> findByDestinationCountry(String country);
    
    // Recherche combinée
    @Query("SELECT t FROM Transfer t WHERE " +
           "(:userId IS NULL OR t.userId = :userId) AND " +
           "(:status IS NULL OR t.status = :status) AND " +
           "(:type IS NULL OR t.type = :type) AND " +
           "(:currency IS NULL OR t.currency = :currency) AND " +
           "(:minAmount IS NULL OR t.amount >= :minAmount) AND " +
           "(:maxAmount IS NULL OR t.amount <= :maxAmount) AND " +
           "(:startDate IS NULL OR t.createdAt >= :startDate) AND " +
           "(:endDate IS NULL OR t.createdAt <= :endDate)")
    Page<Transfer> findByMultipleCriteria(
            @Param("userId") UUID userId,
            @Param("status") TransferStatus status,
            @Param("type") TransferType type,
            @Param("currency") String currency,
            @Param("minAmount") BigDecimal minAmount,
            @Param("maxAmount") BigDecimal maxAmount,
            @Param("startDate") LocalDateTime startDate,
            @Param("endDate") LocalDateTime endDate,
            Pageable pageable
    );
    
    // Statistiques
    @Query("SELECT COUNT(t) FROM Transfer t WHERE t.userId = :userId")
    long countByUserId(@Param("userId") UUID userId);
    
    @Query("SELECT COUNT(t) FROM Transfer t WHERE t.userId = :userId AND t.status = :status")
    long countByUserIdAndStatus(@Param("userId") UUID userId, @Param("status") TransferStatus status);
    
    @Query("SELECT SUM(t.amount) FROM Transfer t WHERE t.userId = :userId")
    BigDecimal sumTransfersByUserId(@Param("userId") UUID userId);
    
    @Query("SELECT SUM(t.amount) FROM Transfer t WHERE t.userId = :userId AND t.status = :status")
    BigDecimal sumTransfersByUserIdAndStatus(@Param("userId") UUID userId, @Param("status") TransferStatus status);
    
    @Query("SELECT SUM(t.amount) FROM Transfer t WHERE t.userId = :userId AND DATE(t.createdAt) = :date")
    BigDecimal sumDailyTransfersByUserId(@Param("userId") UUID userId, @Param("date") LocalDate date);
    
    @Query("SELECT SUM(t.amount) FROM Transfer t WHERE t.userId = :userId AND YEAR(t.createdAt) = :year AND MONTH(t.createdAt) = :month")
    BigDecimal sumMonthlyTransfersByUserId(@Param("userId") UUID userId, @Param("year") int year, @Param("month") int month);
    
    @Query("SELECT SUM(t.fees) FROM Transfer t WHERE t.userId = :userId")
    BigDecimal sumFeesByUserId(@Param("userId") UUID userId);
    
    @Query("SELECT SUM(t.amount) FROM Transfer t WHERE t.status = :status")
    BigDecimal sumTransfersByStatus(@Param("status") TransferStatus status);
    
    // Recherche de transferts en attente
    @Query("SELECT t FROM Transfer t WHERE t.status = 'PENDING' ORDER BY t.createdAt ASC")
    List<Transfer> findPendingTransfers();
    
    // Recherche de transferts par plage de montant
    @Query("SELECT t FROM Transfer t WHERE t.amount BETWEEN :minAmount AND :maxAmount")
    List<Transfer> findTransfersByAmountRange(@Param("minAmount") BigDecimal minAmount, @Param("maxAmount") BigDecimal maxAmount);
    
    // Recherche de transferts créés récemment
    @Query("SELECT t FROM Transfer t WHERE t.createdAt >= :since ORDER BY t.createdAt DESC")
    List<Transfer> findTransfersCreatedSince(@Param("since") LocalDateTime since);
    
    // Recherche de transferts par devise et statut
    @Query("SELECT t FROM Transfer t WHERE t.currency = :currency AND t.status = :status")
    List<Transfer> findTransfersByCurrencyAndStatus(@Param("currency") String currency, @Param("status") TransferStatus status);
    
    // Recherche de transferts par type et pays de destination
    @Query("SELECT t FROM Transfer t WHERE t.type = :type AND t.destinationCountry = :country")
    List<Transfer> findTransfersByTypeAndDestinationCountry(@Param("type") TransferType type, @Param("country") String country);
    
    // Recherche de transferts avec des frais élevés
    @Query("SELECT t FROM Transfer t WHERE t.fees > :minFees")
    List<Transfer> findTransfersWithHighFees(@Param("minFees") BigDecimal minFees);
    
    // Recherche de transferts urgents
    @Query("SELECT t FROM Transfer t WHERE t.priority = 'URGENT' AND t.status = 'PENDING'")
    List<Transfer> findUrgentPendingTransfers();
    
    // Recherche de transferts par bénéficiaire
    @Query("SELECT t FROM Transfer t WHERE t.beneficiaryName = :beneficiaryName")
    List<Transfer> findTransfersByBeneficiary(@Param("beneficiaryName") String beneficiaryName);
    
    // Recherche de transferts par IBAN de destination
    @Query("SELECT t FROM Transfer t WHERE t.destinationIban = :iban")
    List<Transfer> findTransfersByDestinationIban(@Param("iban") String iban);
    
    // Recherche de transferts avec des erreurs
    @Query("SELECT t FROM Transfer t WHERE t.status = 'FAILED' AND t.errorDetails IS NOT NULL")
    List<Transfer> findFailedTransfersWithErrors();
    
    // Recherche de transferts par message SWIFT
    @Query("SELECT t FROM Transfer t WHERE t.swiftMessageId = :messageId")
    List<Transfer> findTransfersBySwiftMessageId(@Param("messageId") String messageId);
    
    // Recherche de transferts par BIC de destination
    @Query("SELECT t FROM Transfer t WHERE t.destinationBic = :bic")
    List<Transfer> findTransfersByDestinationBic(@Param("bic") String bic);
}
package com.banking.transfers.service;

import com.banking.transfers.model.*;
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
public class AccountService {

    @Autowired
    private AccountRepository accountRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AuditService auditService;

    @Autowired
    private RiskAssessmentService riskAssessmentService;

    /**
     * Créer un nouveau compte bancaire
     */
    public Account createAccount(Account account, UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Utilisateur non trouvé"));

        // Validation du compte
        validateAccount(account);

        // Configuration du compte
        account.setId(UUID.randomUUID());
        account.setOwnerId(userId);
        account.setOwnerType(OwnerType.INDIVIDUAL);
        account.setStatus(AccountStatus.ACTIVE);
        account.setBalance(BigDecimal.ZERO);
        account.setAvailableBalance(BigDecimal.ZERO);
        account.setCreatedAt(LocalDateTime.now());
        account.setUpdatedAt(LocalDateTime.now());

        // Génération du numéro de compte IBAN
        if (account.getIban() == null) {
            account.setIban(generateIBAN(account.getCountry()));
        }

        // Configuration des limites selon le niveau de risque
        configureAccountLimits(account, user);

        Account savedAccount = accountRepository.save(account);
        
        auditService.logAccountCreated(savedAccount.getId(), userId, "Création de compte");
        
        return savedAccount;
    }

    /**
     * Récupérer un compte par ID
     */
    public Optional<Account> getAccountById(UUID accountId) {
        return accountRepository.findById(accountId);
    }

    /**
     * Récupérer tous les comptes d'un utilisateur
     */
    public List<Account> getAccountsByUserId(UUID userId) {
        return accountRepository.findByOwnerId(userId);
    }

    /**
     * Récupérer un compte par IBAN
     */
    public Optional<Account> getAccountByIban(String iban) {
        return accountRepository.findByIban(iban);
    }

    /**
     * Mettre à jour un compte
     */
    public Account updateAccount(UUID accountId, Account accountDetails, UUID userId) {
        Account existingAccount = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));

        // Vérifier que l'utilisateur est propriétaire du compte
        if (!existingAccount.getOwnerId().equals(userId)) {
            throw new SecurityException("Accès non autorisé à ce compte");
        }

        // Mise à jour des champs autorisés
        existingAccount.setAccountName(accountDetails.getAccountName());
        existingAccount.setDescription(accountDetails.getDescription());
        existingAccount.setCurrency(accountDetails.getCurrency());
        existingAccount.setUpdatedAt(LocalDateTime.now());

        Account updatedAccount = accountRepository.save(existingAccount);
        
        auditService.logAccountUpdated(accountId, userId, "Mise à jour du compte");
        
        return updatedAccount;
    }

    /**
     * Désactiver un compte
     */
    public void deactivateAccount(UUID accountId, UUID userId) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));

        if (!account.getOwnerId().equals(userId)) {
            throw new SecurityException("Accès non autorisé à ce compte");
        }

        if (account.getBalance().compareTo(BigDecimal.ZERO) > 0) {
            throw new IllegalStateException("Impossible de désactiver un compte avec un solde positif");
        }

        account.setStatus(AccountStatus.CLOSED);
        account.setUpdatedAt(LocalDateTime.now());
        accountRepository.save(account);
        
        auditService.logAccountDeactivated(accountId, userId, "Désactivation du compte");
    }

    /**
     * Vérifier si un compte a suffisamment de fonds
     */
    public boolean hasSufficientFunds(UUID accountId, BigDecimal amount) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));

        return account.getAvailableBalance().compareTo(amount) >= 0;
    }

    /**
     * Débiter un compte
     */
    public void debitAccount(UUID accountId, BigDecimal amount, String description) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));

        if (account.getAvailableBalance().compareTo(amount) < 0) {
            throw new IllegalStateException("Fonds insuffisants");
        }

        account.setBalance(account.getBalance().subtract(amount));
        account.setAvailableBalance(account.getAvailableBalance().subtract(amount));
        account.setUpdatedAt(LocalDateTime.now());
        accountRepository.save(account);
        
        auditService.logAccountDebited(accountId, amount, description);
    }

    /**
     * Créditer un compte
     */
    public void creditAccount(UUID accountId, BigDecimal amount, String description) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));

        account.setBalance(account.getBalance().add(amount));
        account.setAvailableBalance(account.getAvailableBalance().add(amount));
        account.setUpdatedAt(LocalDateTime.now());
        accountRepository.save(account);
        
        auditService.logAccountCredited(accountId, amount, description);
    }

    /**
     * Bloquer des fonds sur un compte (pour les transferts en cours)
     */
    public void blockFunds(UUID accountId, BigDecimal amount) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));

        if (account.getAvailableBalance().compareTo(amount) < 0) {
            throw new IllegalStateException("Fonds insuffisants pour le blocage");
        }

        account.setAvailableBalance(account.getAvailableBalance().subtract(amount));
        account.setBlockedAmount(account.getBlockedAmount().add(amount));
        account.setUpdatedAt(LocalDateTime.now());
        accountRepository.save(account);
    }

    /**
     * Débloquer des fonds sur un compte
     */
    public void unblockFunds(UUID accountId, BigDecimal amount) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));

        account.setAvailableBalance(account.getAvailableBalance().add(amount));
        account.setBlockedAmount(account.getBlockedAmount().subtract(amount));
        account.setUpdatedAt(LocalDateTime.now());
        accountRepository.save(account);
    }

    /**
     * Valider un compte
     */
    private void validateAccount(Account account) {
        if (account.getAccountType() == null) {
            throw new IllegalArgumentException("Le type de compte est obligatoire");
        }
        if (account.getCurrency() == null) {
            throw new IllegalArgumentException("La devise est obligatoire");
        }
        if (account.getCountry() == null) {
            throw new IllegalArgumentException("Le pays est obligatoire");
        }
        if (account.getIban() != null && !isValidIBAN(account.getIban())) {
            throw new IllegalArgumentException("IBAN invalide");
        }
    }

    /**
     * Configurer les limites du compte selon le niveau de risque
     */
    private void configureAccountLimits(Account account, User user) {
        RiskLevel riskLevel = user.getRiskLevel();
        
        switch (riskLevel) {
            case LOW:
                account.setDailyLimit(new BigDecimal("50000"));
                account.setMonthlyLimit(new BigDecimal("500000"));
                account.setSingleLimit(new BigDecimal("10000"));
                break;
            case MEDIUM:
                account.setDailyLimit(new BigDecimal("25000"));
                account.setMonthlyLimit(new BigDecimal("250000"));
                account.setSingleLimit(new BigDecimal("5000"));
                break;
            case HIGH:
                account.setDailyLimit(new BigDecimal("10000"));
                account.setMonthlyLimit(new BigDecimal("100000"));
                account.setSingleLimit(new BigDecimal("1000"));
                break;
            case CRITICAL:
                account.setDailyLimit(BigDecimal.ZERO);
                account.setMonthlyLimit(BigDecimal.ZERO);
                account.setSingleLimit(BigDecimal.ZERO);
                break;
        }
    }

    /**
     * Générer un IBAN pour un pays donné
     */
    private String generateIBAN(String country) {
        // Implémentation simplifiée - en production, utiliser une bibliothèque IBAN
        String countryCode = country != null ? country : "FR";
        String randomDigits = String.format("%016d", (long) (Math.random() * 10000000000000000L));
        return countryCode + "00" + randomDigits;
    }

    /**
     * Valider un IBAN
     */
    private boolean isValidIBAN(String iban) {
        if (iban == null || iban.length() < 15 || iban.length() > 34) {
            return false;
        }
        
        // Validation basique - en production, utiliser une bibliothèque IBAN
        String countryCode = iban.substring(0, 2);
        return countryCode.matches("[A-Z]{2}");
    }

    /**
     * Récupérer le solde d'un compte
     */
    public BigDecimal getAccountBalance(UUID accountId) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));
        return account.getBalance();
    }

    /**
     * Récupérer le solde disponible d'un compte
     */
    public BigDecimal getAvailableBalance(UUID accountId) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));
        return account.getAvailableBalance();
    }

    /**
     * Vérifier si un compte est actif
     */
    public boolean isAccountActive(UUID accountId) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalArgumentException("Compte non trouvé"));
        return account.getStatus() == AccountStatus.ACTIVE;
    }

    /**
     * Récupérer l'historique des transactions d'un compte
     */
    public List<Account> getAccountHistory(UUID accountId) {
        // Cette méthode devrait retourner l'historique des transactions
        // Pour l'instant, retourner une liste vide
        return List.of();
    }
}
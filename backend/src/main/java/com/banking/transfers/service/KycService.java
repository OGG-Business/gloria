package com.banking.transfers.service;

import com.banking.transfers.model.*;
import com.banking.transfers.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
@Transactional
public class KycService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private AuditService auditService;

    @Autowired
    private RiskAssessmentService riskAssessmentService;

    @Value("${kyc.auto-verification.enabled:true}")
    private boolean autoVerificationEnabled;

    @Value("${kyc.auto-verification.max-amount:10000}")
    private double maxAutoVerificationAmount;

    @Value("${kyc.sanctions-screening.enabled:true}")
    private boolean sanctionsScreeningEnabled;

    /**
     * Effectuer une vérification KYC complète
     */
    public KycResult performKycVerification(UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Utilisateur non trouvé"));

        KycResult result = new KycResult();
        result.setUserId(userId);
        result.setVerificationDate(LocalDateTime.now());

        // Vérification des documents
        boolean documentsValid = validateDocuments(user);
        result.setDocumentsValid(documentsValid);

        // Vérification des sanctions
        boolean sanctionsCheck = performSanctionsCheck(user);
        result.setSanctionsCheckPassed(sanctionsCheck);

        // Vérification du risque
        int riskScore = riskAssessmentService.calculateRiskScore(user);
        result.setRiskScore(riskScore);

        // Détermination du statut KYC
        KYCStatus kycStatus = determineKycStatus(result);
        result.setKycStatus(kycStatus);

        // Mise à jour de l'utilisateur
        user.setKycStatus(kycStatus);
        user.setRiskScore(riskScore);
        user.setKycVerifiedAt(LocalDateTime.now());
        userRepository.save(user);

        // Audit
        auditService.logKycVerification(userId, kycStatus, riskScore);

        return result;
    }

    /**
     * Effectuer une vérification KYC automatique
     */
    public boolean performAutoKycVerification(UUID userId) {
        if (!autoVerificationEnabled) {
            return false;
        }

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Utilisateur non trouvé"));

        // Vérifications automatiques basiques
        boolean autoVerified = isEligibleForAutoVerification(user);

        if (autoVerified) {
            user.setKycStatus(KYCStatus.VERIFIED);
            user.setKycVerifiedAt(LocalDateTime.now());
            userRepository.save(user);
            
            auditService.logKycAutoVerification(userId, "Vérification automatique");
            return true;
        }

        return false;
    }

    /**
     * Vérifier si un utilisateur est éligible pour la vérification automatique
     */
    private boolean isEligibleForAutoVerification(User user) {
        // Vérifications basiques
        if (user.getDateOfBirth() == null) return false;
        if (user.getNationality() == null) return false;
        if (user.getCountry() == null) return false;
        if (user.getIdType() == null) return false;
        if (user.getIdNumber() == null || user.getIdNumber().trim().isEmpty()) return false;

        // Vérification de l'âge
        int age = LocalDateTime.now().getYear() - user.getDateOfBirth().getYear();
        if (age < 18 || age > 100) return false;

        // Vérification du pays de résidence
        if (isHighRiskCountry(user.getCountry())) return false;

        // Vérification du type de document
        if (!user.getIdType().isGovernmentIssued()) return false;

        return true;
    }

    /**
     * Valider les documents d'un utilisateur
     */
    private boolean validateDocuments(User user) {
        // Vérifications basiques des documents
        if (user.getIdType() == null) return false;
        if (user.getIdNumber() == null || user.getIdNumber().trim().isEmpty()) return false;

        // Vérification du format du numéro d'identité selon le type
        return validateIdNumber(user.getIdType(), user.getIdNumber());
    }

    /**
     * Valider un numéro d'identité selon le type
     */
    private boolean validateIdNumber(IdType idType, String idNumber) {
        if (idNumber == null || idNumber.trim().isEmpty()) return false;

        switch (idType) {
            case PASSPORT:
                // Format passeport : généralement 6-9 caractères alphanumériques
                return idNumber.matches("^[A-Z0-9]{6,9}$");
            case NATIONAL_ID:
                // Format carte d'identité : variable selon le pays
                return idNumber.length() >= 5 && idNumber.length() <= 20;
            case DRIVERS_LICENSE:
                // Format permis de conduire : variable selon le pays
                return idNumber.length() >= 5 && idNumber.length() <= 15;
            default:
                return idNumber.length() >= 3;
        }
    }

    /**
     * Effectuer une vérification des sanctions
     */
    private boolean performSanctionsCheck(User user) {
        if (!sanctionsScreeningEnabled) {
            return true; // Si désactivé, considérer comme passé
        }

        // Vérification des listes de sanctions
        boolean unSanctions = checkUnSanctions(user);
        boolean euSanctions = checkEuSanctions(user);
        boolean usSanctions = checkUsSanctions(user);

        return unSanctions && euSanctions && usSanctions;
    }

    /**
     * Vérifier les sanctions de l'ONU
     */
    private boolean checkUnSanctions(User user) {
        // Implémentation simplifiée - en production, appeler l'API des sanctions ONU
        return !isUserInSanctionsList(user, "UN");
    }

    /**
     * Vérifier les sanctions de l'UE
     */
    private boolean checkEuSanctions(User user) {
        // Implémentation simplifiée - en production, appeler l'API des sanctions UE
        return !isUserInSanctionsList(user, "EU");
    }

    /**
     * Vérifier les sanctions des États-Unis
     */
    private boolean checkUsSanctions(User user) {
        // Implémentation simplifiée - en production, appeler l'API OFAC
        return !isUserInSanctionsList(user, "US");
    }

    /**
     * Vérifier si un utilisateur est dans une liste de sanctions
     */
    private boolean isUserInSanctionsList(User user, String listType) {
        // Liste simplifiée pour les tests
        String[] sanctionedNames = {"Osama Bin Laden", "Saddam Hussein"};
        
        String fullName = user.getFirstName() + " " + user.getLastName();
        for (String sanctionedName : sanctionedNames) {
            if (fullName.equalsIgnoreCase(sanctionedName)) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Déterminer le statut KYC basé sur les vérifications
     */
    private KYCStatus determineKycStatus(KycResult result) {
        if (!result.isDocumentsValid()) {
            return KYCStatus.REJECTED;
        }

        if (!result.isSanctionsCheckPassed()) {
            return KYCStatus.REJECTED;
        }

        if (result.getRiskScore() > 75) {
            return KYCStatus.PENDING; // Nécessite une vérification manuelle
        }

        return KYCStatus.VERIFIED;
    }

    /**
     * Vérifier si un utilisateur est sous sanctions
     */
    public boolean isUserSanctioned(UUID userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Utilisateur non trouvé"));

        return !performSanctionsCheck(user);
    }

    /**
     * Vérifier si un pays est à risque élevé
     */
    private boolean isHighRiskCountry(String country) {
        String[] highRiskCountries = {"AF", "KP", "IR", "IQ", "LY", "SO", "SD", "SY", "YE"};
        
        for (String highRiskCountry : highRiskCountries) {
            if (highRiskCountry.equals(country)) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Mettre à jour le statut KYC d'un utilisateur
     */
    public void updateKycStatus(UUID userId, KYCStatus status, String reason) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new IllegalArgumentException("Utilisateur non trouvé"));

        KYCStatus oldStatus = user.getKycStatus();
        user.setKycStatus(status);
        user.setKycVerifiedAt(LocalDateTime.now());
        userRepository.save(user);

        auditService.logKycStatusUpdate(userId, oldStatus, status, reason);
    }

    /**
     * Récupérer les statistiques KYC
     */
    public KycStatistics getKycStatistics() {
        KycStatistics stats = new KycStatistics();
        
        stats.setTotalUsers(userRepository.count());
        stats.setVerifiedUsers(userRepository.countByKycStatus(KYCStatus.VERIFIED));
        stats.setPendingUsers(userRepository.countByKycStatus(KYCStatus.PENDING));
        stats.setRejectedUsers(userRepository.countByKycStatus(KYCStatus.REJECTED));
        
        return stats;
    }

    /**
     * Classe de résultat KYC
     */
    public static class KycResult {
        private UUID userId;
        private LocalDateTime verificationDate;
        private boolean documentsValid;
        private boolean sanctionsCheckPassed;
        private int riskScore;
        private KYCStatus kycStatus;
        private String rejectionReason;

        // Getters et setters
        public UUID getUserId() { return userId; }
        public void setUserId(UUID userId) { this.userId = userId; }

        public LocalDateTime getVerificationDate() { return verificationDate; }
        public void setVerificationDate(LocalDateTime verificationDate) { this.verificationDate = verificationDate; }

        public boolean isDocumentsValid() { return documentsValid; }
        public void setDocumentsValid(boolean documentsValid) { this.documentsValid = documentsValid; }

        public boolean isSanctionsCheckPassed() { return sanctionsCheckPassed; }
        public void setSanctionsCheckPassed(boolean sanctionsCheckPassed) { this.sanctionsCheckPassed = sanctionsCheckPassed; }

        public int getRiskScore() { return riskScore; }
        public void setRiskScore(int riskScore) { this.riskScore = riskScore; }

        public KYCStatus getKycStatus() { return kycStatus; }
        public void setKycStatus(KYCStatus kycStatus) { this.kycStatus = kycStatus; }

        public String getRejectionReason() { return rejectionReason; }
        public void setRejectionReason(String rejectionReason) { this.rejectionReason = rejectionReason; }
    }

    /**
     * Classe de statistiques KYC
     */
    public static class KycStatistics {
        private long totalUsers;
        private long verifiedUsers;
        private long pendingUsers;
        private long rejectedUsers;

        // Getters et setters
        public long getTotalUsers() { return totalUsers; }
        public void setTotalUsers(long totalUsers) { this.totalUsers = totalUsers; }

        public long getVerifiedUsers() { return verifiedUsers; }
        public void setVerifiedUsers(long verifiedUsers) { this.verifiedUsers = verifiedUsers; }

        public long getPendingUsers() { return pendingUsers; }
        public void setPendingUsers(long pendingUsers) { this.pendingUsers = pendingUsers; }

        public long getRejectedUsers() { return rejectedUsers; }
        public void setRejectedUsers(long rejectedUsers) { this.rejectedUsers = rejectedUsers; }

        public double getVerificationRate() {
            return totalUsers > 0 ? (double) verifiedUsers / totalUsers * 100 : 0;
        }
    }
}
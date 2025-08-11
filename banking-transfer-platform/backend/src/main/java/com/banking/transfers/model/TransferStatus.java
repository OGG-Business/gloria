package com.banking.transfers.model;

/**
 * Statuts possibles d'un transfert bancaire
 */
public enum TransferStatus {
    
    /**
     * Transfert initié mais pas encore validé
     */
    INITIATED("Initiated", "Transfert initié"),
    
    /**
     * Transfert validé et en attente de traitement
     */
    PENDING("Pending", "Transfert en attente"),
    
    /**
     * Transfert en cours de traitement
     */
    PROCESSING("Processing", "Transfert en cours"),
    
    /**
     * Transfert envoyé au système externe (SWIFT/Mojaloop)
     */
    SENT("Sent", "Transfert envoyé"),
    
    /**
     * Transfert accepté par le système externe
     */
    ACCEPTED("Accepted", "Transfert accepté"),
    
    /**
     * Transfert rejeté par le système externe
     */
    REJECTED("Rejected", "Transfert rejeté"),
    
    /**
     * Transfert complété avec succès
     */
    COMPLETED("Completed", "Transfert complété"),
    
    /**
     * Transfert échoué
     */
    FAILED("Failed", "Transfert échoué"),
    
    /**
     * Transfert annulé
     */
    CANCELLED("Cancelled", "Transfert annulé"),
    
    /**
     * Transfert en attente de clarification
     */
    PENDING_CLARIFICATION("Pending Clarification", "En attente de clarification"),
    
    /**
     * Transfert suspendu pour vérification
     */
    SUSPENDED("Suspended", "Transfert suspendu"),
    
    /**
     * Transfert en attente de fonds
     */
    PENDING_FUNDS("Pending Funds", "En attente de fonds"),
    
    /**
     * Transfert en attente d'autorisation
     */
    PENDING_AUTHORIZATION("Pending Authorization", "En attente d'autorisation");

    private final String code;
    private final String description;

    TransferStatus(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    /**
     * Vérifie si le statut est final (ne peut plus changer)
     */
    public boolean isFinal() {
        return this == COMPLETED || this == FAILED || this == CANCELLED;
    }

    /**
     * Vérifie si le transfert peut être annulé
     */
    public boolean canBeCancelled() {
        return this == INITIATED || this == PENDING || this == PENDING_AUTHORIZATION;
    }

    /**
     * Vérifie si le transfert est en cours de traitement
     */
    public boolean isInProgress() {
        return this == PROCESSING || this == SENT || this == ACCEPTED;
    }

    /**
     * Vérifie si le transfert est en attente
     */
    public boolean isWaiting() {
        return this == PENDING || this == PENDING_CLARIFICATION || 
               this == PENDING_FUNDS || this == PENDING_AUTHORIZATION;
    }

    @Override
    public String toString() {
        return code;
    }
}
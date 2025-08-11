package com.banking.transfers.model;

/**
 * Statuts de comptes bancaires
 */
public enum AccountStatus {
    
    /**
     * Compte actif
     */
    ACTIVE("ACTIVE", "Compte actif"),
    
    /**
     * Compte inactif
     */
    INACTIVE("INACTIVE", "Compte inactif"),
    
    /**
     * Compte suspendu
     */
    SUSPENDED("SUSPENDED", "Compte suspendu"),
    
    /**
     * Compte bloqué
     */
    BLOCKED("BLOCKED", "Compte bloqué"),
    
    /**
     * Compte fermé
     */
    CLOSED("CLOSED", "Compte fermé"),
    
    /**
     * Compte en attente d'activation
     */
    PENDING_ACTIVATION("PENDING_ACTIVATION", "Compte en attente d'activation"),
    
    /**
     * Compte en attente de documents
     */
    PENDING_DOCUMENTS("PENDING_DOCUMENTS", "Compte en attente de documents"),
    
    /**
     * Compte en attente de vérification
     */
    PENDING_VERIFICATION("PENDING_VERIFICATION", "Compte en attente de vérification");

    private final String code;
    private final String description;

    AccountStatus(String code, String description) {
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
     * Vérifie si le compte peut effectuer des opérations
     */
    public boolean canOperate() {
        return this == ACTIVE;
    }

    /**
     * Vérifie si le compte est bloquant
     */
    public boolean isBlocking() {
        return this == SUSPENDED || this == BLOCKED || this == CLOSED;
    }

    /**
     * Vérifie si le compte est en attente
     */
    public boolean isPending() {
        return this == PENDING_ACTIVATION || this == PENDING_DOCUMENTS || this == PENDING_VERIFICATION;
    }

    @Override
    public String toString() {
        return code;
    }
}
package com.banking.transfers.model;

/**
 * Statuts KYC (Know Your Customer)
 */
public enum KYCStatus {
    
    /**
     * KYC non vérifié
     */
    NOT_VERIFIED("NOT_VERIFIED", "KYC non vérifié"),
    
    /**
     * KYC en cours de vérification
     */
    PENDING("PENDING", "KYC en cours de vérification"),
    
    /**
     * KYC vérifié
     */
    VERIFIED("VERIFIED", "KYC vérifié"),
    
    /**
     * KYC rejeté
     */
    REJECTED("REJECTED", "KYC rejeté"),
    
    /**
     * KYC expiré
     */
    EXPIRED("EXPIRED", "KYC expiré"),
    
    /**
     * KYC suspendu
     */
    SUSPENDED("SUSPENDED", "KYC suspendu");

    private final String code;
    private final String description;

    KYCStatus(String code, String description) {
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
     * Vérifie si le KYC est valide
     */
    public boolean isValid() {
        return this == VERIFIED;
    }

    /**
     * Vérifie si le KYC est en attente
     */
    public boolean isPending() {
        return this == PENDING;
    }

    /**
     * Vérifie si le KYC est bloquant
     */
    public boolean isBlocking() {
        return this == NOT_VERIFIED || this == REJECTED || this == EXPIRED || this == SUSPENDED;
    }

    @Override
    public String toString() {
        return code;
    }
}
package com.banking.transfers.model;

/**
 * Types de comptes bancaires
 */
public enum AccountType {
    
    /**
     * Compte courant
     */
    CURRENT("CURRENT", "Compte courant"),
    
    /**
     * Compte d'épargne
     */
    SAVINGS("SAVINGS", "Compte d'épargne"),
    
    /**
     * Compte de dépôt à terme
     */
    FIXED_DEPOSIT("FIXED_DEPOSIT", "Compte de dépôt à terme"),
    
    /**
     * Compte professionnel
     */
    BUSINESS("BUSINESS", "Compte professionnel"),
    
    /**
     * Compte de compensation
     */
    SETTLEMENT("SETTLEMENT", "Compte de compensation"),
    
    /**
     * Compte de trésorerie
     */
    TREASURY("TREASURY", "Compte de trésorerie"),
    
    /**
     * Compte de fiducie
     */
    TRUST("TRUST", "Compte de fiducie"),
    
    /**
     * Compte de joint
     */
    JOINT("JOINT", "Compte de joint"),
    
    /**
     * Compte de correspondant
     */
    NOSTRO("NOSTRO", "Compte de correspondant"),
    
    /**
     * Compte de correspondant
     */
    VOSTRO("VOSTRO", "Compte de correspondant");

    private final String code;
    private final String description;

    AccountType(String code, String description) {
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
     * Vérifie si le compte peut effectuer des transferts
     */
    public boolean canTransfer() {
        return this == CURRENT || this == BUSINESS || this == SETTLEMENT || 
               this == TREASURY || this == JOINT || this == NOSTRO || this == VOSTRO;
    }

    /**
     * Vérifie si le compte est un compte de correspondant
     */
    public boolean isCorrespondentAccount() {
        return this == NOSTRO || this == VOSTRO;
    }

    @Override
    public String toString() {
        return code;
    }
}
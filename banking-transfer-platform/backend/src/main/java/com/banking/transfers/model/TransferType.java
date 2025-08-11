package com.banking.transfers.model;

/**
 * Types de transferts bancaires
 */
public enum TransferType {
    
    /**
     * Transfert SWIFT standard
     */
    SWIFT("SWIFT", "Transfert SWIFT standard"),
    
    /**
     * Transfert SWIFT urgent
     */
    SWIFT_URGENT("SWIFT_URGENT", "Transfert SWIFT urgent"),
    
    /**
     * Transfert Mojaloop (corridors africains)
     */
    MOJALOOP("MOJALOOP", "Transfert Mojaloop"),
    
    /**
     * Transfert SEPA
     */
    SEPA("SEPA", "Transfert SEPA"),
    
    /**
     * Transfert domestique
     */
    DOMESTIC("DOMESTIC", "Transfert domestique"),
    
    /**
     * Transfert interne (même banque)
     */
    INTERNAL("INTERNAL", "Transfert interne"),
    
    /**
     * Transfert de masse
     */
    BULK("BULK", "Transfert de masse"),
    
    /**
     * Transfert récurrent
     */
    RECURRING("RECURRING", "Transfert récurrent"),
    
    /**
     * Transfert de compensation
     */
    SETTLEMENT("SETTLEMENT", "Transfert de compensation");

    private final String code;
    private final String description;

    TransferType(String code, String description) {
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
     * Vérifie si le transfert est international
     */
    public boolean isInternational() {
        return this == SWIFT || this == SWIFT_URGENT || this == MOJALOOP || this == SEPA;
    }

    /**
     * Vérifie si le transfert est urgent
     */
    public boolean isUrgent() {
        return this == SWIFT_URGENT;
    }

    /**
     * Vérifie si le transfert nécessite un connecteur externe
     */
    public boolean requiresExternalConnector() {
        return this == SWIFT || this == SWIFT_URGENT || this == MOJALOOP;
    }

    @Override
    public String toString() {
        return code;
    }
}
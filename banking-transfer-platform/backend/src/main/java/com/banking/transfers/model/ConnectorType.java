package com.banking.transfers.model;

/**
 * Types de connecteurs pour les transferts bancaires
 */
public enum ConnectorType {
    
    /**
     * Connecteur SWIFT
     */
    SWIFT("SWIFT", "Connecteur SWIFT"),
    
    /**
     * Connecteur Mojaloop
     */
    MOJALOOP("MOJALOOP", "Connecteur Mojaloop"),
    
    /**
     * Connecteur SEPA
     */
    SEPA("SEPA", "Connecteur SEPA"),
    
    /**
     * Connecteur domestique
     */
    DOMESTIC("DOMESTIC", "Connecteur domestique"),
    
    /**
     * Connecteur interne
     */
    INTERNAL("INTERNAL", "Connecteur interne"),
    
    /**
     * Connecteur de test
     */
    MOCK("MOCK", "Connecteur de test");

    private final String code;
    private final String description;

    ConnectorType(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    @Override
    public String toString() {
        return code;
    }
}
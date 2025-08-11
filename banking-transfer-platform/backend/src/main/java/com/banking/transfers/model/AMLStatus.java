package com.banking.transfers.model;

/**
 * Statuts AML (Anti-Money Laundering)
 */
public enum AMLStatus {
    
    /**
     * AML non vérifié
     */
    NOT_CHECKED("NOT_CHECKED", "AML non vérifié"),
    
    /**
     * AML en cours de vérification
     */
    PENDING("PENDING", "AML en cours de vérification"),
    
    /**
     * AML passé
     */
    PASSED("PASSED", "AML passé"),
    
    /**
     * AML échoué
     */
    FAILED("FAILED", "AML échoué"),
    
    /**
     * AML en attente de clarification
     */
    PENDING_CLARIFICATION("PENDING_CLARIFICATION", "AML en attente de clarification"),
    
    /**
     * AML suspendu
     */
    SUSPENDED("SUSPENDED", "AML suspendu"),
    
    /**
     * AML bloqué
     */
    BLOCKED("BLOCKED", "AML bloqué");

    private final String code;
    private final String description;

    AMLStatus(String code, String description) {
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
     * Vérifie si l'AML est valide
     */
    public boolean isValid() {
        return this == PASSED;
    }

    /**
     * Vérifie si l'AML est en attente
     */
    public boolean isPending() {
        return this == PENDING || this == PENDING_CLARIFICATION;
    }

    /**
     * Vérifie si l'AML est bloquant
     */
    public boolean isBlocking() {
        return this == FAILED || this == BLOCKED || this == SUSPENDED;
    }

    /**
     * Vérifie si l'AML nécessite une intervention manuelle
     */
    public boolean requiresManualReview() {
        return this == PENDING_CLARIFICATION || this == SUSPENDED;
    }

    @Override
    public String toString() {
        return code;
    }
}
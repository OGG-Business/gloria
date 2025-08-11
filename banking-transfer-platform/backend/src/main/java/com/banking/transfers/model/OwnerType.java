package com.banking.transfers.model;

/**
 * Types de propriétaires de comptes
 */
public enum OwnerType {
    
    /**
     * Particulier
     */
    INDIVIDUAL("INDIVIDUAL", "Particulier"),
    
    /**
     * Entreprise
     */
    CORPORATE("CORPORATE", "Entreprise"),
    
    /**
     * Institution financière
     */
    FINANCIAL_INSTITUTION("FINANCIAL_INSTITUTION", "Institution financière"),
    
    /**
     * Gouvernement
     */
    GOVERNMENT("GOVERNMENT", "Gouvernement"),
    
    /**
     * Organisation non gouvernementale
     */
    NGO("NGO", "Organisation non gouvernementale"),
    
    /**
     * Fiducie
     */
    TRUST("TRUST", "Fiducie"),
    
    /**
     * Fondation
     */
    FOUNDATION("FOUNDATION", "Fondation"),
    
    /**
     * Association
     */
    ASSOCIATION("ASSOCIATION", "Association"),
    
    /**
     * Société de personnes
     */
    PARTNERSHIP("PARTNERSHIP", "Société de personnes"),
    
    /**
     * Société anonyme
     */
    JOINT_STOCK("JOINT_STOCK", "Société anonyme");

    private final String code;
    private final String description;

    OwnerType(String code, String description) {
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
     * Vérifie si le propriétaire est un particulier
     */
    public boolean isIndividual() {
        return this == INDIVIDUAL;
    }

    /**
     * Vérifie si le propriétaire est une entreprise
     */
    public boolean isCorporate() {
        return this == CORPORATE || this == PARTNERSHIP || this == JOINT_STOCK;
    }

    /**
     * Vérifie si le propriétaire est une institution
     */
    public boolean isInstitution() {
        return this == FINANCIAL_INSTITUTION || this == GOVERNMENT || this == NGO || 
               this == FOUNDATION || this == ASSOCIATION;
    }

    @Override
    public String toString() {
        return code;
    }
}
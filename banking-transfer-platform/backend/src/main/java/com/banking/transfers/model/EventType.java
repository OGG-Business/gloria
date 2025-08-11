package com.banking.transfers.model;

/**
 * Types d'événements de transfert
 */
public enum EventType {
    
    /**
     * Transfert créé
     */
    CREATED("CREATED", "Transfert créé"),
    
    /**
     * Transfert validé
     */
    VALIDATED("VALIDATED", "Transfert validé"),
    
    /**
     * Transfert autorisé
     */
    AUTHORIZED("AUTHORIZED", "Transfert autorisé"),
    
    /**
     * Transfert en cours de traitement
     */
    PROCESSING("PROCESSING", "Transfert en cours de traitement"),
    
    /**
     * Transfert envoyé au système externe
     */
    SENT("SENT", "Transfert envoyé"),
    
    /**
     * Transfert accepté par le système externe
     */
    ACCEPTED("ACCEPTED", "Transfert accepté"),
    
    /**
     * Transfert rejeté par le système externe
     */
    REJECTED("REJECTED", "Transfert rejeté"),
    
    /**
     * Transfert complété
     */
    COMPLETED("COMPLETED", "Transfert complété"),
    
    /**
     * Transfert échoué
     */
    FAILED("FAILED", "Transfert échoué"),
    
    /**
     * Transfert annulé
     */
    CANCELLED("CANCELLED", "Transfert annulé"),
    
    /**
     * Transfert suspendu
     */
    SUSPENDED("SUSPENDED", "Transfert suspendu"),
    
    /**
     * Transfert mis à jour
     */
    UPDATED("UPDATED", "Transfert mis à jour"),
    
    /**
     * Information générale
     */
    INFO("INFO", "Information"),
    
    /**
     * Erreur
     */
    ERROR("ERROR", "Erreur"),
    
    /**
     * Avertissement
     */
    WARNING("WARNING", "Avertissement"),
    
    /**
     * Vérification KYC
     */
    KYC_CHECK("KYC_CHECK", "Vérification KYC"),
    
    /**
     * Vérification AML
     */
    AML_CHECK("AML_CHECK", "Vérification AML"),
    
    /**
     * Vérification de fonds
     */
    FUNDS_CHECK("FUNDS_CHECK", "Vérification de fonds"),
    
    /**
     * Calcul des frais
     */
    FEES_CALCULATED("FEES_CALCULATED", "Frais calculés"),
    
    /**
     * Conversion de devise
     */
    CURRENCY_CONVERSION("CURRENCY_CONVERSION", "Conversion de devise"),
    
    /**
     * Notification envoyée
     */
    NOTIFICATION_SENT("NOTIFICATION_SENT", "Notification envoyée"),
    
    /**
     * Audit
     */
    AUDIT("AUDIT", "Audit");

    private final String code;
    private final String description;

    EventType(String code, String description) {
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
     * Vérifie si l'événement est un succès
     */
    public boolean isSuccess() {
        return this == CREATED || this == VALIDATED || this == AUTHORIZED || 
               this == PROCESSING || this == SENT || this == ACCEPTED || 
               this == COMPLETED || this == UPDATED || this == INFO || 
               this == KYC_CHECK || this == AML_CHECK || this == FUNDS_CHECK ||
               this == FEES_CALCULATED || this == CURRENCY_CONVERSION || 
               this == NOTIFICATION_SENT || this == AUDIT;
    }

    /**
     * Vérifie si l'événement est une erreur
     */
    public boolean isError() {
        return this == REJECTED || this == FAILED || this == ERROR;
    }

    /**
     * Vérifie si l'événement est un avertissement
     */
    public boolean isWarning() {
        return this == WARNING || this == SUSPENDED;
    }

    /**
     * Vérifie si l'événement est final
     */
    public boolean isFinal() {
        return this == COMPLETED || this == FAILED || this == CANCELLED;
    }

    @Override
    public String toString() {
        return code;
    }
}
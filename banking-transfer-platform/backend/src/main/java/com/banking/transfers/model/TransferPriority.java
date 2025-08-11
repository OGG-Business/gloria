package com.banking.transfers.model;

/**
 * Priorités de transferts bancaires
 */
public enum TransferPriority {
    
    /**
     * Priorité normale
     */
    NORMAL("NORMAL", "Priorité normale"),
    
    /**
     * Priorité élevée
     */
    HIGH("HIGH", "Priorité élevée"),
    
    /**
     * Priorité urgente
     */
    URGENT("URGENT", "Priorité urgente"),
    
    /**
     * Priorité critique
     */
    CRITICAL("CRITICAL", "Priorité critique");

    private final String code;
    private final String description;

    TransferPriority(String code, String description) {
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
     * Vérifie si la priorité est urgente
     */
    public boolean isUrgent() {
        return this == URGENT || this == CRITICAL;
    }

    /**
     * Vérifie si la priorité est critique
     */
    public boolean isCritical() {
        return this == CRITICAL;
    }

    /**
     * Retourne le délai de traitement en minutes
     */
    public int getProcessingTimeMinutes() {
        switch (this) {
            case CRITICAL: return 5;
            case URGENT: return 15;
            case HIGH: return 30;
            case NORMAL: return 60;
            default: return 60;
        }
    }

    @Override
    public String toString() {
        return code;
    }
}
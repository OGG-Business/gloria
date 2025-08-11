package com.banking.transfers.model;

/**
 * Niveaux de risque pour les utilisateurs
 */
public enum RiskLevel {
    LOW("LOW", "Faible", 0, 30),
    MEDIUM("MEDIUM", "Moyen", 31, 60),
    HIGH("HIGH", "Élevé", 61, 80),
    CRITICAL("CRITICAL", "Critique", 81, 100);

    private final String code;
    private final String description;
    private final int minScore;
    private final int maxScore;

    RiskLevel(String code, String description, int minScore, int maxScore) {
        this.code = code;
        this.description = description;
        this.minScore = minScore;
        this.maxScore = maxScore;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    public int getMinScore() {
        return minScore;
    }

    public int getMaxScore() {
        return maxScore;
    }

    public static RiskLevel fromScore(int score) {
        for (RiskLevel level : values()) {
            if (score >= level.minScore && score <= level.maxScore) {
                return level;
            }
        }
        return CRITICAL; // Par défaut, niveau critique si score hors limites
    }

    public static RiskLevel fromCode(String code) {
        for (RiskLevel level : values()) {
            if (level.code.equals(code)) {
                return level;
            }
        }
        throw new IllegalArgumentException("Niveau de risque inconnu: " + code);
    }

    public boolean isHighRisk() {
        return this == HIGH || this == CRITICAL;
    }

    public boolean requiresEnhancedDueDiligence() {
        return this == HIGH || this == CRITICAL;
    }

    public boolean requiresManualReview() {
        return this == CRITICAL;
    }

    public boolean allowsHighValueTransactions() {
        return this == LOW || this == MEDIUM;
    }

    public int getMaxTransactionLimit() {
        switch (this) {
            case LOW:
                return 100000; // 100k USD
            case MEDIUM:
                return 50000;  // 50k USD
            case HIGH:
                return 10000;  // 10k USD
            case CRITICAL:
                return 1000;   // 1k USD
            default:
                return 1000;
        }
    }

    public String getMonitoringFrequency() {
        switch (this) {
            case LOW:
                return "MONTHLY";
            case MEDIUM:
                return "WEEKLY";
            case HIGH:
                return "DAILY";
            case CRITICAL:
                return "REAL_TIME";
            default:
                return "WEEKLY";
        }
    }

    @Override
    public String toString() {
        return code;
    }
}
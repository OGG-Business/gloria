package com.banking.transfers.model;

/**
 * Niveaux de risque des utilisateurs
 */
public enum RiskLevel {
    LOW("LOW", "Faible", 0, 25),
    MEDIUM("MEDIUM", "Moyen", 26, 50),
    HIGH("HIGH", "Élevé", 51, 75),
    CRITICAL("CRITICAL", "Critique", 76, 100);

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
        return CRITICAL; // Par défaut si le score est hors limites
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
                return 10000; // 10k USD
            case MEDIUM:
                return 5000;  // 5k USD
            case HIGH:
                return 1000;  // 1k USD
            case CRITICAL:
                return 0;     // Aucune transaction autorisée
            default:
                return 0;
        }
    }

    @Override
    public String toString() {
        return code;
    }
}
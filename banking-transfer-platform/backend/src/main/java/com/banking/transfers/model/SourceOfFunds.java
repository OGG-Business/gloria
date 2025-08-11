package com.banking.transfers.model;

/**
 * Sources de fonds pour la conformité AML
 */
public enum SourceOfFunds {
    SALARY("SALARY", "Salaire"),
    BUSINESS_INCOME("BUSINESS_INCOME", "Revenus d'entreprise"),
    INVESTMENT_INCOME("INVESTMENT_INCOME", "Revenus d'investissement"),
    RENTAL_INCOME("RENTAL_INCOME", "Revenus locatifs"),
    INHERITANCE("INHERITANCE", "Héritage"),
    GIFT("GIFT", "Don"),
    LOAN("LOAN", "Prêt"),
    INSURANCE_SETTLEMENT("INSURANCE_SETTLEMENT", "Règlement d'assurance"),
    LEGAL_SETTLEMENT("LEGAL_SETTLEMENT", "Règlement judiciaire"),
    SALE_OF_ASSETS("SALE_OF_ASSETS", "Vente d'actifs"),
    DIVIDENDS("DIVIDENDS", "Dividendes"),
    INTEREST("INTEREST", "Intérêts"),
    PENSION("PENSION", "Pension"),
    SOCIAL_BENEFITS("SOCIAL_BENEFITS", "Prestations sociales"),
    REMITTANCE("REMITTANCE", "Transfert d'argent"),
    CRYPTO_CURRENCY("CRYPTO_CURRENCY", "Cryptomonnaie"),
    GAMBLING_WINNINGS("GAMBLING_WINNINGS", "Gains de jeux"),
    OTHER("OTHER", "Autre");

    private final String code;
    private final String description;

    SourceOfFunds(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    public static SourceOfFunds fromCode(String code) {
        for (SourceOfFunds source : values()) {
            if (source.code.equals(code)) {
                return source;
            }
        }
        throw new IllegalArgumentException("Source de fonds inconnue: " + code);
    }

    public boolean isHighRisk() {
        return this == CRYPTO_CURRENCY || this == GAMBLING_WINNINGS || this == GIFT || 
               this == INHERITANCE || this == LEGAL_SETTLEMENT;
    }

    public boolean requiresDocumentation() {
        return this == INHERITANCE || this == GIFT || this == LEGAL_SETTLEMENT || 
               this == SALE_OF_ASSETS || this == INSURANCE_SETTLEMENT;
    }

    public boolean isRegularIncome() {
        return this == SALARY || this == BUSINESS_INCOME || this == RENTAL_INCOME || 
               this == PENSION || this == SOCIAL_BENEFITS;
    }

    public boolean isInvestmentRelated() {
        return this == INVESTMENT_INCOME || this == DIVIDENDS || this == INTEREST || 
               this == SALE_OF_ASSETS || this == CRYPTO_CURRENCY;
    }

    @Override
    public String toString() {
        return code;
    }
}
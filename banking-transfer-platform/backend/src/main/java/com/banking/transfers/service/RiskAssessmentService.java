package com.banking.transfers.service;

import com.banking.transfers.model.*;
import org.springframework.stereotype.Service;

/**
 * Service d'évaluation des risques pour les utilisateurs
 */
@Service
public class RiskAssessmentService {

    /**
     * Calcule le score de risque initial pour un nouvel utilisateur
     */
    public int calculateInitialRiskScore(User user) {
        int score = 0;

        // Score basé sur la nationalité
        score += getNationalityRiskScore(user.getNationality());

        // Score basé sur le type de document d'identité
        score += getIdTypeRiskScore(user.getIdType());

        // Score basé sur la source de fonds
        score += getSourceOfFundsRiskScore(user.getSourceOfFunds());

        // Score basé sur le revenu annuel
        score += getIncomeRiskScore(user.getAnnualIncome());

        // Score basé sur l'occupation
        score += getOccupationRiskScore(user.getOccupation());

        return Math.min(100, Math.max(0, score));
    }

    /**
     * Calcule le score de risque pour un utilisateur existant
     */
    public int calculateRiskScore(User user) {
        int score = calculateInitialRiskScore(user);

        // Ajustements basés sur l'historique
        if (user.getKycStatus() == KYCStatus.REJECTED) {
            score += 20;
        }
        if (user.getAmlStatus() == AMLStatus.FAILED) {
            score += 30;
        }
        if (user.getAmlStatus() == AMLStatus.BLOCKED) {
            score += 50;
        }

        return Math.min(100, Math.max(0, score));
    }

    private int getNationalityRiskScore(String nationality) {
        if (nationality == null) return 10;

        // Pays à haut risque (exemples)
        switch (nationality) {
            case "KP": // Corée du Nord
            case "IR": // Iran
            case "SY": // Syrie
                return 50;
            case "CU": // Cuba
            case "VE": // Venezuela
                return 40;
            case "RU": // Russie
            case "CN": // Chine
                return 30;
            case "CD": // RDC
            case "NG": // Nigeria
            case "KE": // Kenya
                return 20;
            default:
                return 10;
        }
    }

    private int getIdTypeRiskScore(IdType idType) {
        if (idType == null) return 15;

        if (idType.isGovernmentIssued()) {
            return 5;
        } else if (idType.isPrimaryId()) {
            return 10;
        } else {
            return 20;
        }
    }

    private int getSourceOfFundsRiskScore(SourceOfFunds sourceOfFunds) {
        if (sourceOfFunds == null) return 10;

        if (sourceOfFunds.isHighRisk()) {
            return 40;
        } else if (sourceOfFunds.isRegularIncome()) {
            return 5;
        } else if (sourceOfFunds.isInvestmentRelated()) {
            return 15;
        } else {
            return 20;
        }
    }

    private int getIncomeRiskScore(Double annualIncome) {
        if (annualIncome == null) return 10;

        if (annualIncome > 1000000) { // > 1M USD
            return 30;
        } else if (annualIncome > 500000) { // > 500k USD
            return 20;
        } else if (annualIncome > 100000) { // > 100k USD
            return 10;
        } else if (annualIncome < 10000) { // < 10k USD
            return 15;
        } else {
            return 5;
        }
    }

    private int getOccupationRiskScore(String occupation) {
        if (occupation == null) return 10;

        String lowerOccupation = occupation.toLowerCase();
        
        // Professions à haut risque
        if (lowerOccupation.contains("politic") || lowerOccupation.contains("diplomat")) {
            return 30;
        } else if (lowerOccupation.contains("gambling") || lowerOccupation.contains("casino")) {
            return 40;
        } else if (lowerOccupation.contains("crypto") || lowerOccupation.contains("bitcoin")) {
            return 35;
        } else if (lowerOccupation.contains("lawyer") || lowerOccupation.contains("attorney")) {
            return 15;
        } else if (lowerOccupation.contains("bank") || lowerOccupation.contains("finance")) {
            return 10;
        } else {
            return 10;
        }
    }
}
package com.banking.transfers.dto;

import jakarta.validation.constraints.NotBlank;

/**
 * DTO pour les requêtes d'activation/désactivation MFA
 */
public class MfaToggleRequest {

    @NotBlank(message = "Le code MFA est obligatoire")
    private String mfaCode;

    private boolean enable;

    // Constructeurs
    public MfaToggleRequest() {}

    // Getters et Setters
    public String getMfaCode() { return mfaCode; }
    public void setMfaCode(String mfaCode) { this.mfaCode = mfaCode; }

    public boolean isEnable() { return enable; }
    public void setEnable(boolean enable) { this.enable = enable; }
}
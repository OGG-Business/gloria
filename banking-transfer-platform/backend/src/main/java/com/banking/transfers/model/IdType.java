package com.banking.transfers.model;

/**
 * Types de documents d'identité
 */
public enum IdType {
    PASSPORT("PASSPORT", "Passeport"),
    NATIONAL_ID("NATIONAL_ID", "Carte d'identité nationale"),
    DRIVERS_LICENSE("DRIVERS_LICENSE", "Permis de conduire"),
    RESIDENCE_PERMIT("RESIDENCE_PERMIT", "Permis de séjour"),
    BIRTH_CERTIFICATE("BIRTH_CERTIFICATE", "Acte de naissance"),
    MILITARY_ID("MILITARY_ID", "Carte militaire"),
    STUDENT_ID("STUDENT_ID", "Carte d'étudiant"),
    EMPLOYEE_ID("EMPLOYEE_ID", "Carte d'employé"),
    BUSINESS_LICENSE("BUSINESS_LICENSE", "Licence commerciale"),
    TAX_ID("TAX_ID", "Numéro d'identification fiscale"),
    SOCIAL_SECURITY("SOCIAL_SECURITY", "Numéro de sécurité sociale"),
    VOTER_ID("VOTER_ID", "Carte d'électeur"),
    REFUGEE_ID("REFUGEE_ID", "Carte de réfugié"),
    DIPLOMATIC_ID("DIPLOMATIC_ID", "Carte diplomatique"),
    OTHER("OTHER", "Autre");

    private final String code;
    private final String description;

    IdType(String code, String description) {
        this.code = code;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getDescription() {
        return description;
    }

    public static IdType fromCode(String code) {
        for (IdType idType : values()) {
            if (idType.code.equals(code)) {
                return idType;
            }
        }
        throw new IllegalArgumentException("Code d'identité invalide: " + code);
    }

    public boolean isGovernmentIssued() {
        return this == PASSPORT || this == NATIONAL_ID || this == DRIVERS_LICENSE || 
               this == RESIDENCE_PERMIT || this == MILITARY_ID || this == DIPLOMATIC_ID;
    }

    public boolean isPrimaryId() {
        return this == PASSPORT || this == NATIONAL_ID;
    }

    public boolean isSecondaryId() {
        return this == DRIVERS_LICENSE || this == RESIDENCE_PERMIT || this == MILITARY_ID;
    }

    @Override
    public String toString() {
        return code;
    }
}
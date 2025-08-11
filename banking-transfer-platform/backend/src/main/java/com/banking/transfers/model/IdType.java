package com.banking.transfers.model;

/**
 * Types de documents d'identité
 */
public enum IdType {
    PASSPORT("PASSPORT", "Passeport"),
    NATIONAL_ID("NATIONAL_ID", "Carte d'identité nationale"),
    DRIVERS_LICENSE("DRIVERS_LICENSE", "Permis de conduire"),
    RESIDENCE_PERMIT("RESIDENCE_PERMIT", "Permis de séjour"),
    MILITARY_ID("MILITARY_ID", "Carte militaire"),
    STUDENT_ID("STUDENT_ID", "Carte d'étudiant"),
    WORK_PERMIT("WORK_PERMIT", "Permis de travail"),
    REFUGEE_ID("REFUGEE_ID", "Carte de réfugié"),
    BIRTH_CERTIFICATE("BIRTH_CERTIFICATE", "Acte de naissance"),
    MARRIAGE_CERTIFICATE("MARRIAGE_CERTIFICATE", "Acte de mariage"),
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
        throw new IllegalArgumentException("Type d'identité inconnu: " + code);
    }

    public boolean isGovernmentIssued() {
        return this == PASSPORT || this == NATIONAL_ID || this == DRIVERS_LICENSE || 
               this == RESIDENCE_PERMIT || this == MILITARY_ID || this == WORK_PERMIT || 
               this == REFUGEE_ID;
    }

    public boolean isPrimaryId() {
        return this == PASSPORT || this == NATIONAL_ID;
    }

    @Override
    public String toString() {
        return code;
    }
}
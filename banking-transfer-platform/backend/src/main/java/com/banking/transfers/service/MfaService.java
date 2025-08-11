package com.banking.transfers.service;

import dev.samstevens.totp.code.*;
import dev.samstevens.totp.exceptions.QrGenerationException;
import dev.samstevens.totp.qr.QrData;
import dev.samstevens.totp.qr.QrGenerator;
import dev.samstevens.totp.qr.ZxingPngQrGenerator;
import dev.samstevens.totp.secret.DefaultSecretGenerator;
import dev.samstevens.totp.time.SystemTimeProvider;
import dev.samstevens.totp.time.TimeProvider;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;

/**
 * Service de gestion de l'authentification à deux facteurs (MFA)
 */
@Service
public class MfaService {

    private final DefaultSecretGenerator secretGenerator;
    private final TimeProvider timeProvider;
    private final CodeGenerator codeGenerator;
    private final CodeVerifier codeVerifier;
    private final QrGenerator qrGenerator;

    public MfaService() {
        this.secretGenerator = new DefaultSecretGenerator();
        this.timeProvider = new SystemTimeProvider();
        this.codeGenerator = new DefaultCodeGenerator();
        this.codeVerifier = new DefaultCodeVerifier(codeGenerator, timeProvider);
        this.qrGenerator = new ZxingPngQrGenerator();
    }

    /**
     * Génère un secret MFA pour un utilisateur
     */
    public String generateSecret() {
        return secretGenerator.generate();
    }

    /**
     * Génère un secret MFA avec une taille personnalisée
     */
    public String generateSecret(int length) {
        return secretGenerator.generate(length);
    }

    /**
     * Génère un code TOTP pour un secret donné
     */
    public String generateCode(String secret) {
        return codeGenerator.generate(secret, timeProvider.getTime());
    }

    /**
     * Valide un code MFA
     */
    public boolean validateMfaCode(String secret, String code) {
        if (secret == null || secret.trim().isEmpty() || 
            code == null || code.trim().isEmpty()) {
            return false;
        }

        try {
            return codeVerifier.isValidCode(secret, code);
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Valide un code MFA avec une fenêtre de tolérance personnalisée
     */
    public boolean validateMfaCode(String secret, String code, int window) {
        if (secret == null || secret.trim().isEmpty() || 
            code == null || code.trim().isEmpty()) {
            return false;
        }

        try {
            return codeVerifier.isValidCode(secret, code, window);
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Génère des codes de sauvegarde pour un utilisateur
     */
    public List<String> generateBackupCodes(int count) {
        return IntStream.range(0, count)
                .mapToObj(i -> generateBackupCode())
                .collect(Collectors.toList());
    }

    /**
     * Génère un code de sauvegarde unique
     */
    private String generateBackupCode() {
        // Génère un code de 8 chiffres
        return String.format("%08d", (int) (Math.random() * 100000000));
    }

    /**
     * Valide un code de sauvegarde
     */
    public boolean validateBackupCode(String storedBackupCodes, String providedCode) {
        if (storedBackupCodes == null || storedBackupCodes.trim().isEmpty() ||
            providedCode == null || providedCode.trim().isEmpty()) {
            return false;
        }

        // Les codes de sauvegarde sont stockés séparés par des virgules
        String[] codes = storedBackupCodes.split(",");
        for (String code : codes) {
            if (code.trim().equals(providedCode.trim())) {
                return true;
            }
        }
        return false;
    }

    /**
     * Consomme un code de sauvegarde (le retire de la liste)
     */
    public String consumeBackupCode(String storedBackupCodes, String usedCode) {
        if (storedBackupCodes == null || storedBackupCodes.trim().isEmpty()) {
            return storedBackupCodes;
        }

        String[] codes = storedBackupCodes.split(",");
        StringBuilder remainingCodes = new StringBuilder();
        
        for (String code : codes) {
            if (!code.trim().equals(usedCode.trim())) {
                if (remainingCodes.length() > 0) {
                    remainingCodes.append(",");
                }
                remainingCodes.append(code.trim());
            }
        }
        
        return remainingCodes.toString();
    }

    /**
     * Génère une URL QR pour l'application d'authentification
     */
    public String generateQrUrl(String secret, String username, String issuer) {
        QrData data = new QrData.Builder()
                .label(username)
                .secret(secret)
                .issuer(issuer)
                .algorithm(HashingAlgorithm.SHA1)
                .digits(6)
                .period(30)
                .build();

        return data.getUri();
    }

    /**
     * Génère une image QR en base64
     */
    public String generateQrImageBase64(String secret, String username, String issuer) {
        try {
            QrData data = new QrData.Builder()
                    .label(username)
                    .secret(secret)
                    .issuer(issuer)
                    .algorithm(HashingAlgorithm.SHA1)
                    .digits(6)
                    .period(30)
                    .build();

            byte[] qrImage = qrGenerator.generate(data);
            return java.util.Base64.getEncoder().encodeToString(qrImage);
        } catch (QrGenerationException e) {
            throw new RuntimeException("Erreur lors de la génération du QR code", e);
        }
    }

    /**
     * Génère une image QR avec des paramètres personnalisés
     */
    public String generateQrImageBase64(String secret, String username, String issuer, 
                                       HashingAlgorithm algorithm, int digits, int period) {
        try {
            QrData data = new QrData.Builder()
                    .label(username)
                    .secret(secret)
                    .issuer(issuer)
                    .algorithm(algorithm)
                    .digits(digits)
                    .period(period)
                    .build();

            byte[] qrImage = qrGenerator.generate(data);
            return java.util.Base64.getEncoder().encodeToString(qrImage);
        } catch (QrGenerationException e) {
            throw new RuntimeException("Erreur lors de la génération du QR code", e);
        }
    }

    /**
     * Vérifie si un secret MFA est valide
     */
    public boolean isValidSecret(String secret) {
        if (secret == null || secret.trim().isEmpty()) {
            return false;
        }

        // Un secret TOTP doit être au moins de 16 caractères
        if (secret.length() < 16) {
            return false;
        }

        // Vérifier que le secret ne contient que des caractères valides
        return secret.matches("^[A-Z2-7]+=*$");
    }

    /**
     * Génère un code de test pour un secret
     */
    public String generateTestCode(String secret) {
        if (!isValidSecret(secret)) {
            throw new IllegalArgumentException("Secret MFA invalide");
        }
        return generateCode(secret);
    }

    /**
     * Obtient le temps restant avant le prochain code
     */
    public int getTimeRemaining() {
        long currentTime = timeProvider.getTime();
        return 30 - (int) (currentTime % 30);
    }

    /**
     * Obtient le temps écoulé depuis le début de la période actuelle
     */
    public int getTimeElapsed() {
        long currentTime = timeProvider.getTime();
        return (int) (currentTime % 30);
    }

    /**
     * Vérifie si un code est sur le point d'expirer
     */
    public boolean isCodeExpiringSoon(String secret) {
        int timeRemaining = getTimeRemaining();
        return timeRemaining <= 5; // 5 secondes ou moins
    }

    /**
     * Génère des informations de configuration MFA pour un utilisateur
     */
    public MfaConfig generateMfaConfig(String username, String issuer) {
        String secret = generateSecret();
        String qrUrl = generateQrUrl(secret, username, issuer);
        String qrImage = generateQrImageBase64(secret, username, issuer);
        List<String> backupCodes = generateBackupCodes(10);

        return MfaConfig.builder()
                .secret(secret)
                .qrUrl(qrUrl)
                .qrImage(qrImage)
                .backupCodes(backupCodes)
                .backupCodesString(String.join(",", backupCodes))
                .build();
    }

    /**
     * Valide une configuration MFA complète
     */
    public boolean validateMfaConfig(MfaConfig config) {
        if (config == null) {
            return false;
        }

        // Vérifier le secret
        if (!isValidSecret(config.getSecret())) {
            return false;
        }

        // Vérifier l'URL QR
        if (config.getQrUrl() == null || config.getQrUrl().trim().isEmpty()) {
            return false;
        }

        // Vérifier les codes de sauvegarde
        if (config.getBackupCodes() == null || config.getBackupCodes().isEmpty()) {
            return false;
        }

        // Vérifier qu'au moins un code de sauvegarde est valide
        return config.getBackupCodes().stream()
                .anyMatch(code -> code != null && code.length() == 8 && code.matches("\\d{8}"));
    }

    /**
     * Classe pour encapsuler la configuration MFA
     */
    public static class MfaConfig {
        private String secret;
        private String qrUrl;
        private String qrImage;
        private List<String> backupCodes;
        private String backupCodesString;

        private MfaConfig() {}

        public static Builder builder() {
            return new Builder();
        }

        // Getters
        public String getSecret() { return secret; }
        public String getQrUrl() { return qrUrl; }
        public String getQrImage() { return qrImage; }
        public List<String> getBackupCodes() { return backupCodes; }
        public String getBackupCodesString() { return backupCodesString; }

        // Builder
        public static class Builder {
            private MfaConfig config = new MfaConfig();

            public Builder secret(String secret) {
                config.secret = secret;
                return this;
            }

            public Builder qrUrl(String qrUrl) {
                config.qrUrl = qrUrl;
                return this;
            }

            public Builder qrImage(String qrImage) {
                config.qrImage = qrImage;
                return this;
            }

            public Builder backupCodes(List<String> backupCodes) {
                config.backupCodes = backupCodes;
                return this;
            }

            public Builder backupCodesString(String backupCodesString) {
                config.backupCodesString = backupCodesString;
                return this;
            }

            public MfaConfig build() {
                return config;
            }
        }
    }
}
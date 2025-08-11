package com.banking.transfers.service;

import dev.samstevens.totp.code.*;
import dev.samstevens.totp.exceptions.QrGenerationException;
import dev.samstevens.totp.qr.QrData;
import dev.samstevens.totp.qr.QrGenerator;
import dev.samstevens.totp.qr.ZxingPngQrGenerator;
import dev.samstevens.totp.secret.DefaultSecretGenerator;
import dev.samstevens.totp.time.SystemTimeProvider;
import dev.samstevens.totp.time.TimeProvider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Service pour la gestion de l'authentification multi-facteurs (MFA)
 */
@Service
public class MfaService {

    private static final Logger logger = LoggerFactory.getLogger(MfaService.class);

    private final DefaultSecretGenerator secretGenerator;
    private final TimeProvider timeProvider;
    private final CodeGenerator codeGenerator;
    private final CodeVerifier codeVerifier;
    private final QrGenerator qrGenerator;
    private final SecureRandom secureRandom;

    public MfaService() {
        this.secretGenerator = new DefaultSecretGenerator();
        this.timeProvider = new SystemTimeProvider();
        this.codeGenerator = new DefaultCodeGenerator();
        this.codeVerifier = new DefaultCodeVerifier(codeGenerator, timeProvider);
        this.qrGenerator = new ZxingPngQrGenerator();
        this.secureRandom = new SecureRandom();
    }

    /**
     * Génère un secret MFA
     */
    public String generateSecret() {
        return secretGenerator.generate();
    }

    /**
     * Génère un QR code pour l'application MFA
     */
    public String generateQrCode(String secret, String username, String issuer) {
        try {
            QrData data = new QrData.Builder()
                    .label(username)
                    .secret(secret)
                    .issuer(issuer)
                    .algorithm(HashingAlgorithm.SHA1)
                    .digits(6)
                    .period(30)
                    .build();

            return qrGenerator.generate(data);
        } catch (QrGenerationException e) {
            logger.error("Erreur lors de la génération du QR code: {}", e.getMessage());
            throw new RuntimeException("Impossible de générer le QR code", e);
        }
    }

    /**
     * Génère un QR code avec des paramètres par défaut
     */
    public String generateQrCode(String secret, String username) {
        return generateQrCode(secret, username, "Banking Transfer Platform");
    }

    /**
     * Vérifie un code MFA
     */
    public boolean verifyCode(String secret, String code) {
        if (secret == null || code == null || code.trim().isEmpty()) {
            return false;
        }

        try {
            return codeVerifier.isValidCode(secret, code);
        } catch (Exception e) {
            logger.warn("Erreur lors de la vérification du code MFA: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Vérifie un code MFA avec une fenêtre de tolérance personnalisée
     */
    public boolean verifyCode(String secret, String code, int window) {
        if (secret == null || code == null || code.trim().isEmpty()) {
            return false;
        }

        try {
            return codeVerifier.isValidCode(secret, code, window);
        } catch (Exception e) {
            logger.warn("Erreur lors de la vérification du code MFA: {}", e.getMessage());
            return false;
        }
    }

    /**
     * Génère des codes de sauvegarde
     */
    public String generateBackupCodes() {
        List<String> backupCodes = new ArrayList<>();
        
        for (int i = 0; i < 10; i++) {
            backupCodes.add(generateBackupCode());
        }

        return String.join(",", backupCodes);
    }

    /**
     * Génère un code de sauvegarde unique
     */
    private String generateBackupCode() {
        StringBuilder code = new StringBuilder();
        for (int i = 0; i < 8; i++) {
            code.append(secureRandom.nextInt(10));
        }
        return code.toString();
    }

    /**
     * Vérifie un code de sauvegarde
     */
    public boolean verifyBackupCode(String backupCodesString, String code) {
        if (backupCodesString == null || code == null || code.trim().isEmpty()) {
            return false;
        }

        String[] backupCodes = backupCodesString.split(",");
        for (String backupCode : backupCodes) {
            if (backupCode.trim().equals(code.trim())) {
                return true;
            }
        }
        return false;
    }

    /**
     * Consomme un code de sauvegarde (le retire de la liste)
     */
    public String consumeBackupCode(String backupCodesString, String code) {
        if (backupCodesString == null || code == null || code.trim().isEmpty()) {
            return backupCodesString;
        }

        String[] backupCodes = backupCodesString.split(",");
        List<String> remainingCodes = new ArrayList<>();
        
        boolean found = false;
        for (String backupCode : backupCodes) {
            if (!found && backupCode.trim().equals(code.trim())) {
                found = true; // Consommer le premier code trouvé
            } else {
                remainingCodes.add(backupCode);
            }
        }

        return String.join(",", remainingCodes);
    }

    /**
     * Génère un code MFA temporaire pour les tests
     */
    public String generateTemporaryCode(String secret) {
        try {
            return codeGenerator.generate(secret, timeProvider.getTime());
        } catch (Exception e) {
            logger.error("Erreur lors de la génération du code temporaire: {}", e.getMessage());
            return null;
        }
    }

    /**
     * Vérifie si un secret MFA est valide
     */
    public boolean isValidSecret(String secret) {
        if (secret == null || secret.trim().isEmpty()) {
            return false;
        }

        // Vérifier la longueur (doit être d'au moins 16 caractères)
        if (secret.length() < 16) {
            return false;
        }

        // Vérifier qu'il ne contient que des caractères valides (Base32)
        return secret.matches("^[A-Z2-7]+=*$");
    }

    /**
     * Génère une URL pour l'application MFA
     */
    public String generateMfaUrl(String secret, String username, String issuer) {
        return String.format("otpauth://totp/%s:%s?secret=%s&issuer=%s&algorithm=SHA1&digits=6&period=30",
                issuer, username, secret, issuer);
    }

    /**
     * Génère une URL avec des paramètres par défaut
     */
    public String generateMfaUrl(String secret, String username) {
        return generateMfaUrl(secret, username, "Banking Transfer Platform");
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
    public boolean isCodeExpiringSoon() {
        return getTimeRemaining() <= 5;
    }

    /**
     * Génère des codes de récupération (différents des codes de sauvegarde)
     */
    public List<String> generateRecoveryCodes() {
        List<String> recoveryCodes = new ArrayList<>();
        
        for (int i = 0; i < 5; i++) {
            recoveryCodes.add(generateRecoveryCode());
        }

        return recoveryCodes;
    }

    /**
     * Génère un code de récupération unique
     */
    private String generateRecoveryCode() {
        StringBuilder code = new StringBuilder();
        for (int i = 0; i < 10; i++) {
            if (i > 0 && i % 4 == 0) {
                code.append("-");
            }
            code.append(secureRandom.nextInt(10));
        }
        return code.toString();
    }

    /**
     * Vérifie un code de récupération
     */
    public boolean verifyRecoveryCode(List<String> recoveryCodes, String code) {
        if (recoveryCodes == null || code == null || code.trim().isEmpty()) {
            return false;
        }

        return recoveryCodes.stream()
                .anyMatch(recoveryCode -> recoveryCode.trim().equals(code.trim()));
    }

    /**
     * Consomme un code de récupération
     */
    public List<String> consumeRecoveryCode(List<String> recoveryCodes, String code) {
        if (recoveryCodes == null || code == null || code.trim().isEmpty()) {
            return recoveryCodes;
        }

        return recoveryCodes.stream()
                .filter(recoveryCode -> !recoveryCode.trim().equals(code.trim()))
                .collect(Collectors.toList());
    }

    /**
     * Génère un secret avec une longueur personnalisée
     */
    public String generateSecret(int length) {
        if (length < 16) {
            length = 16; // Minimum recommandé
        }
        
        StringBuilder secret = new StringBuilder();
        String chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
        
        for (int i = 0; i < length; i++) {
            secret.append(chars.charAt(secureRandom.nextInt(chars.length())));
        }
        
        return secret.toString();
    }

    /**
     * Valide un code MFA (format)
     */
    public boolean isValidCodeFormat(String code) {
        if (code == null || code.trim().isEmpty()) {
            return false;
        }

        // Vérifier que c'est un nombre à 6 chiffres
        return code.trim().matches("^\\d{6}$");
    }

    /**
     * Obtient les informations sur l'algorithme de hachage utilisé
     */
    public String getAlgorithmInfo() {
        return "SHA1";
    }

    /**
     * Obtient le nombre de chiffres dans les codes
     */
    public int getDigits() {
        return 6;
    }

    /**
     * Obtient la période de validité des codes (en secondes)
     */
    public int getPeriod() {
        return 30;
    }

    /**
     * Génère un secret compatible avec Google Authenticator
     */
    public String generateGoogleAuthenticatorSecret() {
        return generateSecret(32); // Google Authenticator recommande 32 caractères
    }

    /**
     * Génère un QR code compatible avec Google Authenticator
     */
    public String generateGoogleAuthenticatorQrCode(String secret, String username) {
        return generateQrCode(secret, username, "Banking Transfer Platform");
    }
}
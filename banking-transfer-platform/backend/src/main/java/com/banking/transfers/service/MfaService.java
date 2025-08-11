package com.banking.transfers.service;

import com.banking.transfers.model.User;
import org.springframework.stereotype.Service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.ByteBuffer;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.util.Base64;

/**
 * Service pour la gestion de l'authentification à deux facteurs (MFA)
 */
@Service
public class MfaService {

    private static final String ALGORITHM = "HmacSHA1";
    private static final int DIGITS = 6;
    private static final int PERIOD = 30; // secondes
    private static final int WINDOW = 1; // fenêtre de validation (périodes)

    /**
     * Génère un secret MFA pour un utilisateur
     */
    public String generateMfaSecret() {
        // Générer un secret aléatoire de 20 bytes (160 bits)
        byte[] secret = new byte[20];
        new java.security.SecureRandom().nextBytes(secret);
        return Base64.getEncoder().encodeToString(secret);
    }

    /**
     * Génère un code MFA pour un utilisateur
     */
    public String generateMfaCode(User user) {
        return generateTOTP(user.getMfaSecret());
    }

    /**
     * Vérifie un code MFA pour un utilisateur
     */
    public boolean verifyMfaCode(User user, String code) {
        if (user.getMfaSecret() == null || code == null || code.trim().isEmpty()) {
            return false;
        }

        String expectedCode = generateTOTP(user.getMfaSecret());
        return code.trim().equals(expectedCode);
    }

    /**
     * Vérifie un code MFA avec une fenêtre de validation
     */
    public boolean verifyMfaCodeWithWindow(User user, String code) {
        if (user.getMfaSecret() == null || code == null || code.trim().isEmpty()) {
            return false;
        }

        long currentTime = Instant.now().getEpochSecond();
        long timeStep = currentTime / PERIOD;

        // Vérifier le code actuel et les codes dans la fenêtre
        for (int i = -WINDOW; i <= WINDOW; i++) {
            String expectedCode = generateTOTP(user.getMfaSecret(), timeStep + i);
            if (code.trim().equals(expectedCode)) {
                return true;
            }
        }

        return false;
    }

    /**
     * Génère un TOTP (Time-based One-Time Password)
     */
    private String generateTOTP(String secret) {
        long currentTime = Instant.now().getEpochSecond();
        long timeStep = currentTime / PERIOD;
        return generateTOTP(secret, timeStep);
    }

    /**
     * Génère un TOTP pour un timeStep spécifique
     */
    private String generateTOTP(String secret, long timeStep) {
        try {
            // Décoder le secret
            byte[] secretBytes = Base64.getDecoder().decode(secret);

            // Convertir le timeStep en bytes
            byte[] timeBytes = ByteBuffer.allocate(8).putLong(timeStep).array();

            // Calculer le HMAC
            Mac mac = Mac.getInstance(ALGORITHM);
            SecretKeySpec keySpec = new SecretKeySpec(secretBytes, ALGORITHM);
            mac.init(keySpec);
            byte[] hash = mac.doFinal(timeBytes);

            // Extraire les 4 derniers bits pour l'offset
            int offset = hash[hash.length - 1] & 0xf;

            // Extraire 4 bytes à partir de l'offset
            int binary = ((hash[offset] & 0x7f) << 24) |
                        ((hash[offset + 1] & 0xff) << 16) |
                        ((hash[offset + 2] & 0xff) << 8) |
                        (hash[offset + 3] & 0xff);

            // Convertir en code à 6 chiffres
            int code = binary % (int) Math.pow(10, DIGITS);
            return String.format("%0" + DIGITS + "d", code);

        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new RuntimeException("Erreur lors de la génération du code MFA", e);
        }
    }

    /**
     * Génère une URL QR Code pour l'application d'authentification
     */
    public String generateQrCodeUrl(User user, String issuer, String accountName) {
        String secret = user.getMfaSecret();
        if (secret == null) {
            throw new IllegalStateException("Aucun secret MFA configuré pour cet utilisateur");
        }

        // Format: otpauth://totp/{issuer}:{account}?secret={secret}&issuer={issuer}&algorithm=SHA1&digits=6&period=30
        return String.format("otpauth://totp/%s:%s?secret=%s&issuer=%s&algorithm=SHA1&digits=%d&period=%d",
                issuer, accountName, secret, issuer, DIGITS, PERIOD);
    }

    /**
     * Génère une URL QR Code avec l'email de l'utilisateur
     */
    public String generateQrCodeUrl(User user, String issuer) {
        return generateQrCodeUrl(user, issuer, user.getEmail());
    }

    /**
     * Vérifie si un utilisateur a MFA activé
     */
    public boolean isMfaEnabled(User user) {
        return user.getMfaEnabled() != null && user.getMfaEnabled() && user.getMfaSecret() != null;
    }

    /**
     * Vérifie si un utilisateur a besoin de configurer MFA
     */
    public boolean needsMfaSetup(User user) {
        return user.getMfaEnabled() != null && user.getMfaEnabled() && user.getMfaSecret() == null;
    }

    /**
     * Valide un code MFA pour la configuration initiale
     */
    public boolean validateMfaSetupCode(String secret, String code) {
        if (secret == null || code == null || code.trim().isEmpty()) {
            return false;
        }

        String expectedCode = generateTOTP(secret);
        return code.trim().equals(expectedCode);
    }

    /**
     * Génère un code de sauvegarde pour MFA
     */
    public String generateBackupCode() {
        // Générer un code de 8 chiffres
        int code = new java.security.SecureRandom().nextInt(100000000);
        return String.format("%08d", code);
    }

    /**
     * Génère plusieurs codes de sauvegarde
     */
    public String[] generateBackupCodes(int count) {
        String[] codes = new String[count];
        for (int i = 0; i < count; i++) {
            codes[i] = generateBackupCode();
        }
        return codes;
    }

    /**
     * Vérifie si un code de sauvegarde est valide
     */
    public boolean verifyBackupCode(String storedBackupCodes, String providedCode) {
        if (storedBackupCodes == null || providedCode == null) {
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
     * Supprime un code de sauvegarde utilisé
     */
    public String removeBackupCode(String storedBackupCodes, String usedCode) {
        if (storedBackupCodes == null || usedCode == null) {
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
     * Obtient le temps restant avant le prochain code MFA
     */
    public int getTimeRemaining() {
        long currentTime = Instant.now().getEpochSecond();
        return (int) (PERIOD - (currentTime % PERIOD));
    }

    /**
     * Obtient le prochain code MFA pour un utilisateur
     */
    public String getNextMfaCode(User user) {
        if (!isMfaEnabled(user)) {
            throw new IllegalStateException("MFA n'est pas activé pour cet utilisateur");
        }

        // Calculer le prochain timeStep
        long currentTime = Instant.now().getEpochSecond();
        long nextTimeStep = ((currentTime / PERIOD) + 1) * PERIOD;
        long timeStep = nextTimeStep / PERIOD;

        return generateTOTP(user.getMfaSecret(), timeStep);
    }

    /**
     * Obtient le code MFA précédent pour un utilisateur
     */
    public String getPreviousMfaCode(User user) {
        if (!isMfaEnabled(user)) {
            throw new IllegalStateException("MFA n'est pas activé pour cet utilisateur");
        }

        // Calculer le timeStep précédent
        long currentTime = Instant.now().getEpochSecond();
        long previousTimeStep = ((currentTime / PERIOD) - 1) * PERIOD;
        long timeStep = previousTimeStep / PERIOD;

        return generateTOTP(user.getMfaSecret(), timeStep);
    }

    /**
     * Vérifie si un code MFA est expiré
     */
    public boolean isMfaCodeExpired(String code, long generationTime) {
        long currentTime = Instant.now().getEpochSecond();
        long timeStep = currentTime / PERIOD;
        long generationTimeStep = generationTime / PERIOD;
        
        return (timeStep - generationTimeStep) > WINDOW;
    }

    /**
     * Génère un secret MFA compatible avec les applications d'authentification
     */
    public String generateCompatibleSecret() {
        // Générer un secret de 32 caractères (160 bits) compatible avec Base32
        byte[] secret = new byte[20];
        new java.security.SecureRandom().nextBytes(secret);
        
        // Convertir en Base32 pour une meilleure compatibilité
        return Base32.encode(secret);
    }

    /**
     * Classe utilitaire pour l'encodage Base32
     */
    private static class Base32 {
        private static final String ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
        private static final int MASK = 31;
        private static final int SHIFT = 5;

        public static String encode(byte[] data) {
            if (data.length == 0) {
                return "";
            }

            StringBuilder result = new StringBuilder();
            int buffer = data[0];
            int next = 1;
            int bitsLeft = 8;

            while (bitsLeft > 0 || next < data.length) {
                if (bitsLeft < SHIFT) {
                    if (next < data.length) {
                        buffer <<= 8;
                        buffer |= (data[next++] & 0xff);
                        bitsLeft += 8;
                    } else {
                        int pad = SHIFT - bitsLeft;
                        buffer <<= pad;
                        bitsLeft += pad;
                    }
                }
                int index = MASK & (buffer >> (bitsLeft - SHIFT));
                bitsLeft -= SHIFT;
                result.append(ALPHABET.charAt(index));
            }

            return result.toString();
        }
    }
}
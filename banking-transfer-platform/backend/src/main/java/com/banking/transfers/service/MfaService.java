package com.banking.transfers.service;

import org.springframework.stereotype.Service;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.nio.ByteBuffer;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.Base64;

/**
 * Service pour l'authentification à deux facteurs (MFA)
 */
@Service
public class MfaService {

    private static final String ALGORITHM = "HmacSHA1";
    private static final int DIGITS = 6;
    private static final int PERIOD = 30; // 30 secondes
    private static final int WINDOW = 1; // Fenêtre de validation (1 période avant/après)

    /**
     * Génère un secret TOTP pour un utilisateur
     */
    public String generateSecret() {
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[20]; // 160 bits
        random.nextBytes(bytes);
        return Base64.getEncoder().encodeToString(bytes);
    }

    /**
     * Valide un code TOTP
     */
    public boolean validateCode(String secret, String code) {
        if (secret == null || code == null || code.length() != DIGITS) {
            return false;
        }

        try {
            long currentTime = Instant.now().getEpochSecond();
            long timeStep = currentTime / PERIOD;

            // Vérifier le code actuel et les codes dans la fenêtre
            for (int i = -WINDOW; i <= WINDOW; i++) {
                String expectedCode = generateTOTP(secret, timeStep + i);
                if (code.equals(expectedCode)) {
                    return true;
                }
            }

            return false;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Génère un code TOTP pour un instant donné
     */
    public String generateTOTP(String secret, long timeStep) {
        try {
            byte[] key = Base64.getDecoder().decode(secret);
            byte[] time = ByteBuffer.allocate(8).putLong(timeStep).array();

            Mac mac = Mac.getInstance(ALGORITHM);
            SecretKeySpec keySpec = new SecretKeySpec(key, ALGORITHM);
            mac.init(keySpec);

            byte[] hash = mac.doFinal(time);
            int offset = hash[hash.length - 1] & 0xf;

            int binary = ((hash[offset] & 0x7f) << 24) |
                        ((hash[offset + 1] & 0xff) << 16) |
                        ((hash[offset + 2] & 0xff) << 8) |
                        (hash[offset + 3] & 0xff);

            int otp = binary % (int) Math.pow(10, DIGITS);
            return String.format("%0" + DIGITS + "d", otp);

        } catch (NoSuchAlgorithmException | InvalidKeyException e) {
            throw new RuntimeException("Erreur lors de la génération du code TOTP", e);
        }
    }

    /**
     * Génère un code TOTP pour l'instant actuel
     */
    public String generateCurrentTOTP(String secret) {
        long currentTime = Instant.now().getEpochSecond();
        long timeStep = currentTime / PERIOD;
        return generateTOTP(secret, timeStep);
    }

    /**
     * Génère un QR code pour l'application d'authentification
     */
    public String generateQrCode(String secret, String email) {
        String issuer = "Banking Transfer Platform";
        String accountName = email;
        
        // Format URI pour les applications TOTP
        String uri = String.format("otpauth://totp/%s:%s?secret=%s&issuer=%s&algorithm=SHA1&digits=%d&period=%d",
                issuer, accountName, secret, issuer, DIGITS, PERIOD);
        
        return uri;
    }

    /**
     * Génère un QR code avec des paramètres personnalisés
     */
    public String generateQrCode(String secret, String email, String issuer, String accountName) {
        if (issuer == null) {
            issuer = "Banking Transfer Platform";
        }
        if (accountName == null) {
            accountName = email;
        }
        
        String uri = String.format("otpauth://totp/%s:%s?secret=%s&issuer=%s&algorithm=SHA1&digits=%d&period=%d",
                issuer, accountName, secret, issuer, DIGITS, PERIOD);
        
        return uri;
    }

    /**
     * Vérifie si un secret est valide
     */
    public boolean isValidSecret(String secret) {
        try {
            if (secret == null || secret.trim().isEmpty()) {
                return false;
            }
            
            // Vérifier que le secret peut être décodé
            Base64.getDecoder().decode(secret);
            
            // Vérifier la longueur minimale (au moins 128 bits)
            byte[] key = Base64.getDecoder().decode(secret);
            return key.length >= 16;
            
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Génère un secret avec une longueur spécifique
     */
    public String generateSecret(int length) {
        if (length < 16) {
            throw new IllegalArgumentException("La longueur minimale du secret doit être de 16 octets");
        }
        
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[length];
        random.nextBytes(bytes);
        return Base64.getEncoder().encodeToString(bytes);
    }

    /**
     * Calcule le temps restant avant le prochain code
     */
    public int getTimeRemaining() {
        long currentTime = Instant.now().getEpochSecond();
        return (int) (PERIOD - (currentTime % PERIOD));
    }

    /**
     * Vérifie si un code est expiré
     */
    public boolean isCodeExpired(String code, long timestamp) {
        long currentTime = Instant.now().getEpochSecond();
        long codeTime = timestamp / PERIOD;
        long currentTimeStep = currentTime / PERIOD;
        
        return Math.abs(currentTimeStep - codeTime) > WINDOW;
    }

    /**
     * Génère un code de récupération (backup code)
     */
    public String generateBackupCode() {
        SecureRandom random = new SecureRandom();
        int code = random.nextInt(100000000); // 8 chiffres
        return String.format("%08d", code);
    }

    /**
     * Valide un code de récupération
     */
    public boolean validateBackupCode(String backupCode, String storedBackupCodes) {
        if (backupCode == null || storedBackupCodes == null) {
            return false;
        }
        
        // Les codes de récupération sont stockés séparés par des virgules
        String[] codes = storedBackupCodes.split(",");
        for (String code : codes) {
            if (code.trim().equals(backupCode.trim())) {
                return true;
            }
        }
        
        return false;
    }

    /**
     * Génère plusieurs codes de récupération
     */
    public String generateBackupCodes(int count) {
        if (count < 1 || count > 10) {
            throw new IllegalArgumentException("Le nombre de codes de récupération doit être entre 1 et 10");
        }
        
        StringBuilder codes = new StringBuilder();
        for (int i = 0; i < count; i++) {
            if (i > 0) {
                codes.append(",");
            }
            codes.append(generateBackupCode());
        }
        
        return codes.toString();
    }

    /**
     * Supprime un code de récupération utilisé
     */
    public String removeBackupCode(String backupCode, String storedBackupCodes) {
        if (backupCode == null || storedBackupCodes == null) {
            return storedBackupCodes;
        }
        
        String[] codes = storedBackupCodes.split(",");
        StringBuilder remainingCodes = new StringBuilder();
        
        for (String code : codes) {
            if (!code.trim().equals(backupCode.trim())) {
                if (remainingCodes.length() > 0) {
                    remainingCodes.append(",");
                }
                remainingCodes.append(code.trim());
            }
        }
        
        return remainingCodes.toString();
    }

    /**
     * Vérifie la force d'un secret
     */
    public SecretStrength checkSecretStrength(String secret) {
        if (!isValidSecret(secret)) {
            return SecretStrength.WEAK;
        }
        
        try {
            byte[] key = Base64.getDecoder().decode(secret);
            int bitLength = key.length * 8;
            
            if (bitLength >= 256) {
                return SecretStrength.STRONG;
            } else if (bitLength >= 192) {
                return SecretStrength.MEDIUM;
            } else {
                return SecretStrength.WEAK;
            }
        } catch (Exception e) {
            return SecretStrength.WEAK;
        }
    }

    /**
     * Génère un secret fort recommandé
     */
    public String generateStrongSecret() {
        return generateSecret(32); // 256 bits
    }

    /**
     * Enum pour la force du secret
     */
    public enum SecretStrength {
        WEAK("Faible", "Recommandé: utiliser un secret plus long"),
        MEDIUM("Moyen", "Acceptable pour la plupart des cas d'usage"),
        STRONG("Fort", "Excellent niveau de sécurité");

        private final String label;
        private final String description;

        SecretStrength(String label, String description) {
            this.label = label;
            this.description = description;
        }

        public String getLabel() {
            return label;
        }

        public String getDescription() {
            return description;
        }
    }
}
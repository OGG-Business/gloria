package com.swiftpay.connector.iban;

import org.iban4j.Iban;
import org.iban4j.IbanFormatException;
import org.iban4j.InvalidCheckDigitException;
import org.iban4j.UnsupportedCountryException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

/**
 * Validateur IBAN avec support étendu pour les pays africains
 * 
 * Supporte la validation IBAN standard ainsi que les formats
 * spécifiques aux pays africains, notamment la RDC.
 */
@Component
public class IbanValidator {

    private static final Logger logger = LoggerFactory.getLogger(IbanValidator.class);

    // Patterns IBAN pour pays africains (certains n'ont pas encore d'IBAN standard)
    private static final Map<String, IbanCountryInfo> AFRICAN_COUNTRY_PATTERNS = new HashMap<>();
    
    static {
        // Pays africains avec IBAN standard
        AFRICAN_COUNTRY_PATTERNS.put("DZ", new IbanCountryInfo("DZ", 24, "Algérie", true));
        AFRICAN_COUNTRY_PATTERNS.put("AO", new IbanCountryInfo("AO", 25, "Angola", true));
        AFRICAN_COUNTRY_PATTERNS.put("BF", new IbanCountryInfo("BF", 27, "Burkina Faso", true));
        AFRICAN_COUNTRY_PATTERNS.put("BI", new IbanCountryInfo("BI", 16, "Burundi", true));
        AFRICAN_COUNTRY_PATTERNS.put("CM", new IbanCountryInfo("CM", 27, "Cameroun", true));
        AFRICAN_COUNTRY_PATTERNS.put("CV", new IbanCountryInfo("CV", 25, "Cap-Vert", true));
        AFRICAN_COUNTRY_PATTERNS.put("CI", new IbanCountryInfo("CI", 28, "Côte d'Ivoire", true));
        AFRICAN_COUNTRY_PATTERNS.put("DJ", new IbanCountryInfo("DJ", 27, "Djibouti", true));
        AFRICAN_COUNTRY_PATTERNS.put("EG", new IbanCountryInfo("EG", 29, "Égypte", true));
        AFRICAN_COUNTRY_PATTERNS.put("GA", new IbanCountryInfo("GA", 27, "Gabon", true));
        AFRICAN_COUNTRY_PATTERNS.put("IR", new IbanCountryInfo("IR", 26, "Iran", true));
        AFRICAN_COUNTRY_PATTERNS.put("JO", new IbanCountryInfo("JO", 30, "Jordanie", true));
        AFRICAN_COUNTRY_PATTERNS.put("LB", new IbanCountryInfo("LB", 28, "Liban", true));
        AFRICAN_COUNTRY_PATTERNS.put("LY", new IbanCountryInfo("LY", 25, "Libye", true));
        AFRICAN_COUNTRY_PATTERNS.put("MA", new IbanCountryInfo("MA", 28, "Maroc", true));
        AFRICAN_COUNTRY_PATTERNS.put("MG", new IbanCountryInfo("MG", 27, "Madagascar", true));
        AFRICAN_COUNTRY_PATTERNS.put("ML", new IbanCountryInfo("ML", 28, "Mali", true));
        AFRICAN_COUNTRY_PATTERNS.put("MR", new IbanCountryInfo("MR", 27, "Mauritanie", true));
        AFRICAN_COUNTRY_PATTERNS.put("MU", new IbanCountryInfo("MU", 30, "Maurice", true));
        AFRICAN_COUNTRY_PATTERNS.put("MZ", new IbanCountryInfo("MZ", 25, "Mozambique", true));
        AFRICAN_COUNTRY_PATTERNS.put("NE", new IbanCountryInfo("NE", 28, "Niger", true));
        AFRICAN_COUNTRY_PATTERNS.put("SN", new IbanCountryInfo("SN", 28, "Sénégal", true));
        AFRICAN_COUNTRY_PATTERNS.put("TN", new IbanCountryInfo("TN", 24, "Tunisie", true));
        
        // RDC - Format spécial (pas encore IBAN standard)
        AFRICAN_COUNTRY_PATTERNS.put("CD", new IbanCountryInfo("CD", 27, "République Démocratique du Congo", false));
        
        // Autres pays africains sans IBAN standard
        AFRICAN_COUNTRY_PATTERNS.put("GH", new IbanCountryInfo("GH", 0, "Ghana", false));
        AFRICAN_COUNTRY_PATTERNS.put("KE", new IbanCountryInfo("KE", 0, "Kenya", false));
        AFRICAN_COUNTRY_PATTERNS.put("NG", new IbanCountryInfo("NG", 0, "Nigeria", false));
        AFRICAN_COUNTRY_PATTERNS.put("ZA", new IbanCountryInfo("ZA", 0, "Afrique du Sud", false));
        AFRICAN_COUNTRY_PATTERNS.put("UG", new IbanCountryInfo("UG", 0, "Ouganda", false));
        AFRICAN_COUNTRY_PATTERNS.put("TZ", new IbanCountryInfo("TZ", 0, "Tanzanie", false));
        AFRICAN_COUNTRY_PATTERNS.put("ZW", new IbanCountryInfo("ZW", 0, "Zimbabwe", false));
        AFRICAN_COUNTRY_PATTERNS.put("ZM", new IbanCountryInfo("ZM", 0, "Zambie", false));
        AFRICAN_COUNTRY_PATTERNS.put("RW", new IbanCountryInfo("RW", 0, "Rwanda", false));
        AFRICAN_COUNTRY_PATTERNS.put("ET", new IbanCountryInfo("ET", 0, "Éthiopie", false));
    }

    /**
     * Valide un IBAN selon les standards internationaux et africains
     * 
     * @param iban L'IBAN à valider
     * @return Résultat de la validation avec détails
     */
    public IbanValidationResult validateIban(String iban) {
        if (iban == null || iban.trim().isEmpty()) {
            return new IbanValidationResult(false, "IBAN vide ou null", null, null);
        }

        // Nettoyage de l'IBAN
        String cleanIban = iban.replaceAll("\\s+", "").toUpperCase();
        
        if (cleanIban.length() < 4) {
            return new IbanValidationResult(false, "IBAN trop court", null, null);
        }

        String countryCode = cleanIban.substring(0, 2);
        
        try {
            // Tentative de validation avec iban4j pour les pays supportés
            Iban validatedIban = Iban.valueOf(cleanIban);
            
            IbanCountryInfo countryInfo = AFRICAN_COUNTRY_PATTERNS.get(countryCode);
            if (countryInfo != null) {
                logger.debug("IBAN validé pour pays africain: {} ({})", countryCode, countryInfo.getCountryName());
            }
            
            return new IbanValidationResult(true, "IBAN valide", countryCode, 
                                          countryInfo != null ? countryInfo.getCountryName() : null);
            
        } catch (IbanFormatException e) {
            logger.debug("Format IBAN invalide: {}", cleanIban);
            return new IbanValidationResult(false, "Format IBAN invalide: " + e.getMessage(), countryCode, null);
            
        } catch (InvalidCheckDigitException e) {
            logger.debug("Chiffres de contrôle IBAN invalides: {}", cleanIban);
            return new IbanValidationResult(false, "Chiffres de contrôle invalides", countryCode, null);
            
        } catch (UnsupportedCountryException e) {
            // Pour les pays non supportés par iban4j, validation manuelle
            return validateUnsupportedCountryIban(cleanIban, countryCode);
        }
    }

    /**
     * Validation manuelle pour les pays non supportés par iban4j
     * Particulièrement important pour les pays africains
     */
    private IbanValidationResult validateUnsupportedCountryIban(String iban, String countryCode) {
        IbanCountryInfo countryInfo = AFRICAN_COUNTRY_PATTERNS.get(countryCode);
        
        if (countryInfo == null) {
            return new IbanValidationResult(false, 
                                          "Pays non supporté pour IBAN: " + countryCode, 
                                          countryCode, null);
        }

        if (!countryInfo.hasStandardIban()) {
            return new IbanValidationResult(false, 
                                          "Pays sans IBAN standard: " + countryInfo.getCountryName() + 
                                          ". Utilisez le numéro de compte local.", 
                                          countryCode, countryInfo.getCountryName());
        }

        // Validation de la longueur pour les pays africains avec IBAN
        if (countryInfo.getIbanLength() > 0 && iban.length() != countryInfo.getIbanLength()) {
            return new IbanValidationResult(false, 
                                          String.format("Longueur IBAN incorrecte pour %s. Attendu: %d, Reçu: %d", 
                                                       countryInfo.getCountryName(), 
                                                       countryInfo.getIbanLength(), 
                                                       iban.length()),
                                          countryCode, countryInfo.getCountryName());
        }

        // Validation basique du format
        if (!Pattern.matches("^[A-Z]{2}[0-9]{2}[A-Z0-9]+$", iban)) {
            return new IbanValidationResult(false, "Format IBAN invalide", countryCode, countryInfo.getCountryName());
        }

        // Validation manuelle des chiffres de contrôle (algorithme mod-97)
        if (!validateCheckDigits(iban)) {
            return new IbanValidationResult(false, "Chiffres de contrôle IBAN invalides", countryCode, countryInfo.getCountryName());
        }

        logger.info("IBAN validé manuellement pour {}: {}", countryInfo.getCountryName(), iban);
        return new IbanValidationResult(true, "IBAN valide", countryCode, countryInfo.getCountryName());
    }

    /**
     * Validation manuelle des chiffres de contrôle IBAN (mod-97)
     */
    private boolean validateCheckDigits(String iban) {
        try {
            // Déplacer les 4 premiers caractères à la fin
            String rearranged = iban.substring(4) + iban.substring(0, 4);
            
            // Remplacer les lettres par leurs valeurs numériques (A=10, B=11, ..., Z=35)
            StringBuilder numeric = new StringBuilder();
            for (char c : rearranged.toCharArray()) {
                if (Character.isLetter(c)) {
                    numeric.append(c - 'A' + 10);
                } else {
                    numeric.append(c);
                }
            }
            
            // Calcul mod 97
            String numericString = numeric.toString();
            int remainder = 0;
            
            for (int i = 0; i < numericString.length(); i++) {
                remainder = (remainder * 10 + Character.getNumericValue(numericString.charAt(i))) % 97;
            }
            
            return remainder == 1;
            
        } catch (Exception e) {
            logger.error("Erreur lors de la validation des chiffres de contrôle IBAN", e);
            return false;
        }
    }

    /**
     * Valide un numéro de compte local pour les pays sans IBAN
     * 
     * @param accountNumber Numéro de compte local
     * @param countryCode Code pays ISO
     * @return Résultat de la validation
     */
    public AccountValidationResult validateLocalAccountNumber(String accountNumber, String countryCode) {
        if (accountNumber == null || accountNumber.trim().isEmpty()) {
            return new AccountValidationResult(false, "Numéro de compte vide", countryCode);
        }

        IbanCountryInfo countryInfo = AFRICAN_COUNTRY_PATTERNS.get(countryCode);
        if (countryInfo == null) {
            return new AccountValidationResult(false, "Pays non supporté: " + countryCode, countryCode);
        }

        // Validation spécifique par pays
        switch (countryCode) {
            case "CD": // RDC
                return validateDrcAccountNumber(accountNumber);
            case "GH": // Ghana
                return validateGhanaAccountNumber(accountNumber);
            case "NG": // Nigeria
                return validateNigeriaAccountNumber(accountNumber);
            case "KE": // Kenya
                return validateKenyaAccountNumber(accountNumber);
            case "ZA": // Afrique du Sud
                return validateSouthAfricaAccountNumber(accountNumber);
            default:
                // Validation générique
                return validateGenericAccountNumber(accountNumber, countryInfo);
        }
    }

    /**
     * Validation spécifique pour les comptes bancaires RDC
     */
    private AccountValidationResult validateDrcAccountNumber(String accountNumber) {
        String clean = accountNumber.replaceAll("\\s+", "");
        
        // Format typique RDC: 10-16 chiffres
        if (!Pattern.matches("^[0-9]{10,16}$", clean)) {
            return new AccountValidationResult(false, 
                                             "Format de compte RDC invalide. Attendu: 10-16 chiffres", "CD");
        }
        
        logger.debug("Numéro de compte RDC validé: {}", accountNumber);
        return new AccountValidationResult(true, "Numéro de compte RDC valide", "CD");
    }

    /**
     * Validation pour les comptes Ghana
     */
    private AccountValidationResult validateGhanaAccountNumber(String accountNumber) {
        String clean = accountNumber.replaceAll("\\s+", "");
        
        // Format Ghana: généralement 13 chiffres
        if (!Pattern.matches("^[0-9]{10,15}$", clean)) {
            return new AccountValidationResult(false, 
                                             "Format de compte Ghana invalide. Attendu: 10-15 chiffres", "GH");
        }
        
        return new AccountValidationResult(true, "Numéro de compte Ghana valide", "GH");
    }

    /**
     * Validation pour les comptes Nigeria
     */
    private AccountValidationResult validateNigeriaAccountNumber(String accountNumber) {
        String clean = accountNumber.replaceAll("\\s+", "");
        
        // Format Nigeria: 10 chiffres (NUBAN)
        if (!Pattern.matches("^[0-9]{10}$", clean)) {
            return new AccountValidationResult(false, 
                                             "Format de compte Nigeria invalide. Attendu: 10 chiffres (NUBAN)", "NG");
        }
        
        return new AccountValidationResult(true, "Numéro de compte Nigeria valide", "NG");
    }

    /**
     * Validation pour les comptes Kenya
     */
    private AccountValidationResult validateKenyaAccountNumber(String accountNumber) {
        String clean = accountNumber.replaceAll("\\s+", "");
        
        // Format Kenya: variable selon la banque, généralement 6-16 chiffres
        if (!Pattern.matches("^[0-9]{6,16}$", clean)) {
            return new AccountValidationResult(false, 
                                             "Format de compte Kenya invalide. Attendu: 6-16 chiffres", "KE");
        }
        
        return new AccountValidationResult(true, "Numéro de compte Kenya valide", "KE");
    }

    /**
     * Validation pour les comptes Afrique du Sud
     */
    private AccountValidationResult validateSouthAfricaAccountNumber(String accountNumber) {
        String clean = accountNumber.replaceAll("\\s+", "");
        
        // Format Afrique du Sud: généralement 9-11 chiffres
        if (!Pattern.matches("^[0-9]{9,11}$", clean)) {
            return new AccountValidationResult(false, 
                                             "Format de compte Afrique du Sud invalide. Attendu: 9-11 chiffres", "ZA");
        }
        
        return new AccountValidationResult(true, "Numéro de compte Afrique du Sud valide", "ZA");
    }

    /**
     * Validation générique pour autres pays
     */
    private AccountValidationResult validateGenericAccountNumber(String accountNumber, IbanCountryInfo countryInfo) {
        String clean = accountNumber.replaceAll("\\s+", "");
        
        // Validation basique: au moins 6 caractères alphanumériques
        if (!Pattern.matches("^[A-Z0-9]{6,20}$", clean.toUpperCase())) {
            return new AccountValidationResult(false, 
                                             "Format de compte invalide pour " + countryInfo.getCountryName() + 
                                             ". Attendu: 6-20 caractères alphanumériques", 
                                             countryInfo.getCountryCode());
        }
        
        return new AccountValidationResult(true, 
                                         "Numéro de compte valide pour " + countryInfo.getCountryName(), 
                                         countryInfo.getCountryCode());
    }

    /**
     * Détermine si un pays utilise IBAN ou des numéros de compte locaux
     */
    public boolean isIbanCountry(String countryCode) {
        IbanCountryInfo info = AFRICAN_COUNTRY_PATTERNS.get(countryCode);
        if (info != null) {
            return info.hasStandardIban();
        }
        
        // Pour les autres pays, essayer avec iban4j
        try {
            // Test avec un IBAN fictif pour voir si le pays est supporté
            String testIban = countryCode + "00000000000000000000";
            Iban.valueOf(testIban);
            return true;
        } catch (UnsupportedCountryException e) {
            return false;
        } catch (Exception e) {
            // Autres erreurs indiquent que le pays est supporté mais l'IBAN est invalide
            return true;
        }
    }

    /**
     * Obtient les informations sur un pays
     */
    public IbanCountryInfo getCountryInfo(String countryCode) {
        return AFRICAN_COUNTRY_PATTERNS.get(countryCode);
    }

    // Classes de résultat
    public static class IbanValidationResult {
        private final boolean valid;
        private final String message;
        private final String countryCode;
        private final String countryName;

        public IbanValidationResult(boolean valid, String message, String countryCode, String countryName) {
            this.valid = valid;
            this.message = message;
            this.countryCode = countryCode;
            this.countryName = countryName;
        }

        public boolean isValid() { return valid; }
        public String getMessage() { return message; }
        public String getCountryCode() { return countryCode; }
        public String getCountryName() { return countryName; }
    }

    public static class AccountValidationResult {
        private final boolean valid;
        private final String message;
        private final String countryCode;

        public AccountValidationResult(boolean valid, String message, String countryCode) {
            this.valid = valid;
            this.message = message;
            this.countryCode = countryCode;
        }

        public boolean isValid() { return valid; }
        public String getMessage() { return message; }
        public String getCountryCode() { return countryCode; }
    }

    public static class IbanCountryInfo {
        private final String countryCode;
        private final int ibanLength;
        private final String countryName;
        private final boolean hasStandardIban;

        public IbanCountryInfo(String countryCode, int ibanLength, String countryName, boolean hasStandardIban) {
            this.countryCode = countryCode;
            this.ibanLength = ibanLength;
            this.countryName = countryName;
            this.hasStandardIban = hasStandardIban;
        }

        public String getCountryCode() { return countryCode; }
        public int getIbanLength() { return ibanLength; }
        public String getCountryName() { return countryName; }
        public boolean hasStandardIban() { return hasStandardIban; }
    }
}
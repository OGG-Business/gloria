package com.banking.transfers.dto;

import com.banking.transfers.model.IdType;
import com.banking.transfers.model.SourceOfFunds;
import jakarta.validation.constraints.*;
import java.time.LocalDate;

public class UserRegistrationRequest {

    @NotBlank(message = "Le nom d'utilisateur est obligatoire")
    @Size(min = 3, max = 50, message = "Le nom d'utilisateur doit contenir entre 3 et 50 caractères")
    @Pattern(regexp = "^[a-zA-Z0-9_]+$", message = "Le nom d'utilisateur ne peut contenir que des lettres, chiffres et underscores")
    private String username;

    @NotBlank(message = "L'email est obligatoire")
    @Email(message = "Format d'email invalide")
    @Size(max = 100, message = "L'email ne peut pas dépasser 100 caractères")
    private String email;

    @NotBlank(message = "Le mot de passe est obligatoire")
    @Size(min = 8, max = 128, message = "Le mot de passe doit contenir entre 8 et 128 caractères")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]+$", 
             message = "Le mot de passe doit contenir au moins une minuscule, une majuscule, un chiffre et un caractère spécial")
    private String password;

    @NotBlank(message = "La confirmation du mot de passe est obligatoire")
    private String confirmPassword;

    @NotBlank(message = "Le prénom est obligatoire")
    @Size(min = 2, max = 50, message = "Le prénom doit contenir entre 2 et 50 caractères")
    @Pattern(regexp = "^[a-zA-ZÀ-ÿ\\s'-]+$", message = "Le prénom ne peut contenir que des lettres, espaces, tirets et apostrophes")
    private String firstName;

    @NotBlank(message = "Le nom de famille est obligatoire")
    @Size(min = 2, max = 50, message = "Le nom de famille doit contenir entre 2 et 50 caractères")
    @Pattern(regexp = "^[a-zA-ZÀ-ÿ\\s'-]+$", message = "Le nom de famille ne peut contenir que des lettres, espaces, tirets et apostrophes")
    private String lastName;

    @NotBlank(message = "Le numéro de téléphone est obligatoire")
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$", message = "Format de numéro de téléphone invalide")
    private String phone;

    @NotNull(message = "La date de naissance est obligatoire")
    @Past(message = "La date de naissance doit être dans le passé")
    private LocalDate dateOfBirth;

    @NotBlank(message = "La nationalité est obligatoire")
    @Size(min = 2, max = 3, message = "La nationalité doit être un code pays ISO à 2 ou 3 caractères")
    @Pattern(regexp = "^[A-Z]{2,3}$", message = "La nationalité doit être un code pays ISO valide")
    private String nationality;

    @NotBlank(message = "Le pays de résidence est obligatoire")
    @Size(min = 2, max = 3, message = "Le pays doit être un code pays ISO à 2 ou 3 caractères")
    @Pattern(regexp = "^[A-Z]{2,3}$", message = "Le pays doit être un code pays ISO valide")
    private String country;

    @NotBlank(message = "L'adresse est obligatoire")
    @Size(max = 200, message = "L'adresse ne peut pas dépasser 200 caractères")
    private String address;

    @NotBlank(message = "La ville est obligatoire")
    @Size(max = 100, message = "La ville ne peut pas dépasser 100 caractères")
    private String city;

    @NotBlank(message = "Le code postal est obligatoire")
    @Size(max = 20, message = "Le code postal ne peut pas dépasser 20 caractères")
    private String postalCode;

    @NotNull(message = "Le type de document d'identité est obligatoire")
    private IdType idType;

    @NotBlank(message = "Le numéro de document d'identité est obligatoire")
    @Size(max = 50, message = "Le numéro de document ne peut pas dépasser 50 caractères")
    private String idNumber;

    @NotBlank(message = "L'occupation est obligatoire")
    @Size(max = 100, message = "L'occupation ne peut pas dépasser 100 caractères")
    private String occupation;

    @Size(max = 100, message = "Le nom de l'employeur ne peut pas dépasser 100 caractères")
    private String employer;

    @NotNull(message = "Le revenu annuel est obligatoire")
    @DecimalMin(value = "0.0", inclusive = false, message = "Le revenu annuel doit être positif")
    @DecimalMax(value = "999999999.99", message = "Le revenu annuel ne peut pas dépasser 999,999,999.99")
    private Double annualIncome;

    @NotNull(message = "La source de fonds est obligatoire")
    private SourceOfFunds sourceOfFunds;

    private String sourceOfFundsDetails;

    @AssertTrue(message = "Vous devez accepter les conditions d'utilisation")
    private Boolean acceptTerms = false;

    @AssertTrue(message = "Vous devez accepter la politique de confidentialité")
    private Boolean acceptPrivacyPolicy = false;

    private Boolean marketingConsent = false;

    // Constructeurs
    public UserRegistrationRequest() {}

    public UserRegistrationRequest(String username, String email, String password, String firstName, String lastName) {
        this.username = username;
        this.email = email;
        this.password = password;
        this.firstName = firstName;
        this.lastName = lastName;
    }

    // Getters et Setters
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

    public String getConfirmPassword() { return confirmPassword; }
    public void setConfirmPassword(String confirmPassword) { this.confirmPassword = confirmPassword; }

    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

    public LocalDate getDateOfBirth() { return dateOfBirth; }
    public void setDateOfBirth(LocalDate dateOfBirth) { this.dateOfBirth = dateOfBirth; }

    public String getNationality() { return nationality; }
    public void setNationality(String nationality) { this.nationality = nationality; }

    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }

    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }

    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }

    public String getPostalCode() { return postalCode; }
    public void setPostalCode(String postalCode) { this.postalCode = postalCode; }

    public IdType getIdType() { return idType; }
    public void setIdType(IdType idType) { this.idType = idType; }

    public String getIdNumber() { return idNumber; }
    public void setIdNumber(String idNumber) { this.idNumber = idNumber; }

    public String getOccupation() { return occupation; }
    public void setOccupation(String occupation) { this.occupation = occupation; }

    public String getEmployer() { return employer; }
    public void setEmployer(String employer) { this.employer = employer; }

    public Double getAnnualIncome() { return annualIncome; }
    public void setAnnualIncome(Double annualIncome) { this.annualIncome = annualIncome; }

    public SourceOfFunds getSourceOfFunds() { return sourceOfFunds; }
    public void setSourceOfFunds(SourceOfFunds sourceOfFunds) { this.sourceOfFunds = sourceOfFunds; }

    public String getSourceOfFundsDetails() { return sourceOfFundsDetails; }
    public void setSourceOfFundsDetails(String sourceOfFundsDetails) { this.sourceOfFundsDetails = sourceOfFundsDetails; }

    public Boolean getAcceptTerms() { return acceptTerms; }
    public void setAcceptTerms(Boolean acceptTerms) { this.acceptTerms = acceptTerms; }

    public Boolean getAcceptPrivacyPolicy() { return acceptPrivacyPolicy; }
    public void setAcceptPrivacyPolicy(Boolean acceptPrivacyPolicy) { this.acceptPrivacyPolicy = acceptPrivacyPolicy; }

    public Boolean getMarketingConsent() { return marketingConsent; }
    public void setMarketingConsent(Boolean marketingConsent) { this.marketingConsent = marketingConsent; }

    // Méthodes utilitaires
    public boolean isPasswordMatching() {
        return password != null && password.equals(confirmPassword);
    }

    public String getFullName() {
        return firstName + " " + lastName;
    }

    public boolean isAdult() {
        if (dateOfBirth == null) return false;
        return dateOfBirth.plusYears(18).isBefore(LocalDate.now());
    }

    public boolean isHighRiskCountry() {
        // Liste simplifiée des pays à risque élevé
        String[] highRiskCountries = {"AF", "KP", "IR", "IQ", "LY", "SO", "SD", "SY", "YE"};
        return java.util.Arrays.asList(highRiskCountries).contains(country);
    }

    @Override
    public String toString() {
        return "UserRegistrationRequest{" +
                "username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", firstName='" + firstName + '\'' +
                ", lastName='" + lastName + '\'' +
                ", phone='" + phone + '\'' +
                ", nationality='" + nationality + '\'' +
                ", country='" + country + '\'' +
                ", idType=" + idType +
                ", occupation='" + occupation + '\'' +
                ", annualIncome=" + annualIncome +
                ", sourceOfFunds=" + sourceOfFunds +
                '}';
    }
}
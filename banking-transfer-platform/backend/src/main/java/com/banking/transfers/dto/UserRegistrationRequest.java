package com.banking.transfers.dto;

import com.banking.transfers.model.IdType;
import com.banking.transfers.model.SourceOfFunds;
import jakarta.validation.constraints.*;
import java.time.LocalDate;

/**
 * DTO pour les requêtes d'inscription d'utilisateur
 */
public class UserRegistrationRequest {

    @NotBlank(message = "Le nom d'utilisateur est obligatoire")
    @Size(min = 3, max = 50, message = "Le nom d'utilisateur doit contenir entre 3 et 50 caractères")
    private String username;

    @NotBlank(message = "L'email est obligatoire")
    @Email(message = "L'email doit être valide")
    private String email;

    @NotBlank(message = "Le mot de passe est obligatoire")
    @Size(min = 8, max = 128, message = "Le mot de passe doit contenir entre 8 et 128 caractères")
    @Pattern(regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$", 
             message = "Le mot de passe doit contenir au moins une minuscule, une majuscule, un chiffre et un caractère spécial")
    private String password;

    @NotBlank(message = "Le prénom est obligatoire")
    @Size(min = 2, max = 50, message = "Le prénom doit contenir entre 2 et 50 caractères")
    private String firstName;

    @NotBlank(message = "Le nom de famille est obligatoire")
    @Size(min = 2, max = 50, message = "Le nom de famille doit contenir entre 2 et 50 caractères")
    private String lastName;

    @NotBlank(message = "Le numéro de téléphone est obligatoire")
    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$", message = "Le numéro de téléphone doit être valide")
    private String phone;

    @NotNull(message = "La date de naissance est obligatoire")
    @Past(message = "La date de naissance doit être dans le passé")
    private LocalDate dateOfBirth;

    @NotBlank(message = "La nationalité est obligatoire")
    @Size(min = 2, max = 3, message = "La nationalité doit être un code pays valide")
    private String nationality;

    @NotBlank(message = "Le pays de résidence est obligatoire")
    @Size(min = 2, max = 3, message = "Le pays de résidence doit être un code pays valide")
    private String country;

    @NotBlank(message = "L'adresse est obligatoire")
    @Size(min = 10, max = 200, message = "L'adresse doit contenir entre 10 et 200 caractères")
    private String address;

    @NotBlank(message = "La ville est obligatoire")
    @Size(min = 2, max = 100, message = "La ville doit contenir entre 2 et 100 caractères")
    private String city;

    @NotBlank(message = "Le code postal est obligatoire")
    @Size(min = 3, max = 10, message = "Le code postal doit contenir entre 3 et 10 caractères")
    private String postalCode;

    @NotNull(message = "Le type de pièce d'identité est obligatoire")
    private IdType idType;

    @NotBlank(message = "Le numéro de pièce d'identité est obligatoire")
    @Size(min = 5, max = 50, message = "Le numéro de pièce d'identité doit contenir entre 5 et 50 caractères")
    private String idNumber;

    @NotNull(message = "La date d'expiration de la pièce d'identité est obligatoire")
    @Future(message = "La date d'expiration doit être dans le futur")
    private LocalDate idExpiryDate;

    @NotBlank(message = "L'émetteur de la pièce d'identité est obligatoire")
    @Size(min = 2, max = 100, message = "L'émetteur doit contenir entre 2 et 100 caractères")
    private String idIssuer;

    @NotNull(message = "La source de fonds est obligatoire")
    private SourceOfFunds sourceOfFunds;

    @NotNull(message = "Le revenu annuel est obligatoire")
    @Min(value = 0, message = "Le revenu annuel doit être positif")
    private Double annualIncome;

    @NotBlank(message = "La profession est obligatoire")
    @Size(min = 2, max = 100, message = "La profession doit contenir entre 2 et 100 caractères")
    private String occupation;

    @Size(max = 100, message = "L'employeur ne peut pas dépasser 100 caractères")
    private String employer;

    private Boolean mfaEnabled = false;

    // Constructeurs
    public UserRegistrationRequest() {}

    // Getters et Setters
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }

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

    public LocalDate getIdExpiryDate() { return idExpiryDate; }
    public void setIdExpiryDate(LocalDate idExpiryDate) { this.idExpiryDate = idExpiryDate; }

    public String getIdIssuer() { return idIssuer; }
    public void setIdIssuer(String idIssuer) { this.idIssuer = idIssuer; }

    public SourceOfFunds getSourceOfFunds() { return sourceOfFunds; }
    public void setSourceOfFunds(SourceOfFunds sourceOfFunds) { this.sourceOfFunds = sourceOfFunds; }

    public Double getAnnualIncome() { return annualIncome; }
    public void setAnnualIncome(Double annualIncome) { this.annualIncome = annualIncome; }

    public String getOccupation() { return occupation; }
    public void setOccupation(String occupation) { this.occupation = occupation; }

    public String getEmployer() { return employer; }
    public void setEmployer(String employer) { this.employer = employer; }

    public Boolean getMfaEnabled() { return mfaEnabled; }
    public void setMfaEnabled(Boolean mfaEnabled) { this.mfaEnabled = mfaEnabled; }
}
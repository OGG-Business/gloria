package com.banking.transfers.dto;

import jakarta.validation.constraints.*;
import java.time.LocalDate;

/**
 * DTO pour les requêtes de mise à jour de profil utilisateur
 */
public class UserProfileUpdateRequest {

    @Size(min = 2, max = 50, message = "Le prénom doit contenir entre 2 et 50 caractères")
    private String firstName;

    @Size(min = 2, max = 50, message = "Le nom de famille doit contenir entre 2 et 50 caractères")
    private String lastName;

    @Pattern(regexp = "^\\+?[1-9]\\d{1,14}$", message = "Le numéro de téléphone doit être valide")
    private String phone;

    @Size(min = 2, max = 3, message = "La nationalité doit être un code pays valide")
    private String nationality;

    @Size(min = 2, max = 3, message = "Le pays de résidence doit être un code pays valide")
    private String country;

    @Size(min = 10, max = 200, message = "L'adresse doit contenir entre 10 et 200 caractères")
    private String address;

    @Size(min = 2, max = 100, message = "La ville doit contenir entre 2 et 100 caractères")
    private String city;

    @Size(min = 3, max = 10, message = "Le code postal doit contenir entre 3 et 10 caractères")
    private String postalCode;

    @Size(min = 2, max = 100, message = "La profession doit contenir entre 2 et 100 caractères")
    private String occupation;

    @Size(max = 100, message = "L'employeur ne peut pas dépasser 100 caractères")
    private String employer;

    // Constructeurs
    public UserProfileUpdateRequest() {}

    // Getters et Setters
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }

    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }

    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }

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

    public String getOccupation() { return occupation; }
    public void setOccupation(String occupation) { this.occupation = occupation; }

    public String getEmployer() { return employer; }
    public void setEmployer(String employer) { this.employer = employer; }
}
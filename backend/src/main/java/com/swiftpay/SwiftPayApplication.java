package com.swiftpay;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * SwiftPay Application - Plateforme de transferts bancaires SWIFT & IBAN
 * 
 * Cette application fournit une plateforme complète pour initier, suivre et gérer
 * des transferts bancaires internationaux en utilisant les standards SWIFT et IBAN.
 * 
 * Fonctionnalités principales :
 * - Validation IBAN/BIC
 * - Intégration SWIFT (MT103, ISO 20022)
 * - Support Mojaloop pour l'Afrique
 * - KYC/AML automatisé
 * - Chiffrement des données sensibles
 * - Audit complet et traçabilité
 * 
 * @author SwiftPay Team
 * @version 1.0.0
 */
@SpringBootApplication
@EnableConfigurationProperties
@EnableJpaAuditing
@EnableCaching
@EnableAsync
@EnableScheduling
@EnableTransactionManagement
public class SwiftPayApplication {

    public static void main(String[] args) {
        // Définir les propriétés système pour la sécurité
        System.setProperty("java.security.egd", "file:/dev/./urandom");
        System.setProperty("spring.jpa.open-in-view", "false");
        
        SpringApplication app = new SpringApplication(SwiftPayApplication.class);
        
        // Configuration pour la production
        app.setAdditionalProfiles("security");
        
        app.run(args);
    }
}
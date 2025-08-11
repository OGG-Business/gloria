package com.banking.transfers;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.transaction.annotation.EnableTransactionManagement;

/**
 * Application principale pour la plateforme de transferts bancaires
 * 
 * Cette application gère les transferts bancaires internationaux
 * conformément aux standards SWIFT et ISO 20022
 */
@SpringBootApplication
@EnableJpaAuditing
@EnableTransactionManagement
@EnableCaching
@EnableKafka
@EnableAsync
@EnableScheduling
public class BankingTransferApplication {

    public static void main(String[] args) {
        SpringApplication.run(BankingTransferApplication.class, args);
    }
}
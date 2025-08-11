package com.swiftpay.connector.swift;

import com.swiftpay.model.entity.Transfer;
import com.swiftpay.model.iso20022.Pacs008Document;
import com.swiftpay.service.EncryptionService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.TrustManagerFactory;
import java.io.FileInputStream;
import java.security.KeyStore;
import java.security.SecureRandom;
import java.time.Duration;
import java.time.ZonedDateTime;
import java.util.UUID;
import java.math.BigDecimal;
import com.swiftpay.connector.swift.ReactorClientHttpConnector;
import com.swiftpay.connector.swift.HttpClient;

/**
 * Connecteur SWIFT pour l'envoi de messages ISO 20022 et MT
 * 
 * ATTENTION: Ce connecteur nécessite des credentials et certificats fournis par votre banque.
 * Ne jamais tenter d'utiliser sans configuration appropriée.
 */
@Component
public class SwiftConnector {

    private static final Logger logger = LoggerFactory.getLogger(SwiftConnector.class);

    @Value("${swiftpay.swift.enabled:false}")
    private boolean swiftEnabled;

    @Value("${swiftpay.swift.bic}")
    private String ourBic;

    @Value("${swiftpay.swift.endpoint-url}")
    private String swiftEndpointUrl;

    @Value("${swiftpay.swift.client-cert-path}")
    private String clientCertPath;

    @Value("${swiftpay.swift.client-cert-password}")
    private String clientCertPassword;

    @Value("${swiftpay.swift.ca-cert-path}")
    private String caCertPath;

    @Value("${swiftpay.swift.mutual-tls-enabled:true}")
    private boolean mutualTlsEnabled;

    @Value("${swiftpay.swift.timeout:30000}")
    private int timeoutMillis;

    private final SwiftMessageProcessor messageProcessor;
    private final SwiftSecurityHandler securityHandler;
    private final EncryptionService encryptionService;
    private WebClient webClient;

    public SwiftConnector(SwiftMessageProcessor messageProcessor, 
                         SwiftSecurityHandler securityHandler,
                         EncryptionService encryptionService) {
        this.messageProcessor = messageProcessor;
        this.securityHandler = securityHandler;
        this.encryptionService = encryptionService;
    }

    /**
     * Initialise le connecteur SWIFT avec les certificats et configuration
     * 
     * IMPORTANT: Cette méthode doit être appelée avec des credentials valides
     * fournis par votre institution bancaire ou partenaire SWIFT.
     */
    public void initialize() {
        if (!swiftEnabled) {
            logger.warn("SWIFT connector désactivé. Activez avec swiftpay.swift.enabled=true");
            return;
        }

        try {
            validateConfiguration();
            setupSSLContext();
            logger.info("SWIFT connector initialisé avec succès pour BIC: {}", ourBic);
        } catch (Exception e) {
            logger.error("Erreur lors de l'initialisation du connecteur SWIFT", e);
            throw new SwiftConnectorException("Échec de l'initialisation SWIFT", e);
        }
    }

    /**
     * Envoie un transfert via SWIFT en utilisant le format ISO 20022 pacs.008
     * 
     * @param transfer Le transfert à envoyer
     * @param correlationId ID de corrélation pour le suivi
     * @return Résultat de l'envoi avec référence SWIFT
     */
    public SwiftTransferResult sendTransfer(Transfer transfer, String correlationId) {
        if (!swiftEnabled) {
            throw new SwiftConnectorException("SWIFT connector non activé");
        }

        MDC.put("correlationId", correlationId);
        
        try {
            logger.info("Envoi du transfert SWIFT: {} vers BIC: {}", 
                       transfer.getReferenceNumber(), transfer.getRecipientBic());

            // Validation préalable
            validateTransferForSwift(transfer);

            // Génération du message ISO 20022 pacs.008
            Pacs008Document pacs008 = messageProcessor.createPacs008Message(transfer, ourBic);
            
            // Signature et chiffrement du message
            String signedMessage = securityHandler.signMessage(pacs008.toXml(), correlationId);
            
            // Envoi via SWIFT API
            SwiftApiResponse response = sendToSwiftNetwork(signedMessage, correlationId);
            
            // Traitement de la réponse
            SwiftTransferResult result = processSwiftResponse(response, transfer, correlationId);
            
            logger.info("Transfert SWIFT envoyé avec succès. Message ID: {}", result.getSwiftMessageId());
            return result;
            
        } catch (Exception e) {
            logger.error("Erreur lors de l'envoi SWIFT pour le transfert: {}", transfer.getReferenceNumber(), e);
            throw new SwiftConnectorException("Échec de l'envoi SWIFT", e);
        } finally {
            MDC.clear();
        }
    }

    /**
     * Mode dry-run pour tester la connectivité sans envoyer de fonds réels
     * 
     * @param transfer Transfert de test
     * @param correlationId ID de corrélation
     * @return Résultat du test de connectivité
     */
    public SwiftTestResult testConnectivity(Transfer transfer, String correlationId) {
        MDC.put("correlationId", correlationId);
        
        try {
            logger.info("Test de connectivité SWIFT en mode dry-run");
            
            // Validation de la configuration
            validateConfiguration();
            
            // Test de la génération du message
            Pacs008Document testMessage = messageProcessor.createPacs008Message(transfer, ourBic);
            
            // Test de signature (sans envoi)
            String signedMessage = securityHandler.signMessage(testMessage.toXml(), correlationId);
            
            // Test de connectivité réseau (ping/health check)
            boolean networkConnectivity = testNetworkConnectivity();
            
            return new SwiftTestResult(true, networkConnectivity, 
                                     "Test de connectivité réussi", 
                                     testMessage.getMessageId());
            
        } catch (Exception e) {
            logger.error("Échec du test de connectivité SWIFT", e);
            return new SwiftTestResult(false, false, 
                                     "Échec du test: " + e.getMessage(), 
                                     null);
        } finally {
            MDC.clear();
        }
    }

    /**
     * Valide la configuration SWIFT avant utilisation
     */
    private void validateConfiguration() {
        if (ourBic == null || ourBic.trim().isEmpty()) {
            throw new SwiftConnectorException("BIC non configuré");
        }
        
        if (swiftEndpointUrl == null || swiftEndpointUrl.trim().isEmpty()) {
            throw new SwiftConnectorException("URL endpoint SWIFT non configurée");
        }
        
        if (mutualTlsEnabled) {
            if (clientCertPath == null || clientCertPath.trim().isEmpty()) {
                throw new SwiftConnectorException("Chemin du certificat client non configuré");
            }
            
            if (caCertPath == null || caCertPath.trim().isEmpty()) {
                throw new SwiftConnectorException("Chemin du certificat CA non configuré");
            }
        }
        
        logger.debug("Configuration SWIFT validée");
    }

    /**
     * Configure le contexte SSL pour TLS mutuel
     */
    private void setupSSLContext() throws Exception {
        if (!mutualTlsEnabled) {
            logger.info("TLS mutuel désactivé pour SWIFT");
            return;
        }

        // Chargement du keystore client
        KeyStore clientKeyStore = KeyStore.getInstance("PKCS12");
        try (FileInputStream fis = new FileInputStream(clientCertPath)) {
            clientKeyStore.load(fis, clientCertPassword.toCharArray());
        }

        KeyManagerFactory kmf = KeyManagerFactory.getInstance(KeyManagerFactory.getDefaultAlgorithm());
        kmf.init(clientKeyStore, clientCertPassword.toCharArray());

        // Chargement du truststore CA
        KeyStore trustStore = KeyStore.getInstance("JKS");
        try (FileInputStream fis = new FileInputStream(caCertPath)) {
            trustStore.load(fis, null);
        }

        TrustManagerFactory tmf = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        tmf.init(trustStore);

        // Configuration du contexte SSL
        SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
        sslContext.init(kmf.getKeyManagers(), tmf.getTrustManagers(), new SecureRandom());

        // Configuration du WebClient avec SSL
        this.webClient = WebClient.builder()
                .clientConnector(new ReactorClientHttpConnector(
                    HttpClient.create()
                        .secure(spec -> spec.sslContext(sslContext))
                        .responseTimeout(Duration.ofMillis(timeoutMillis))
                ))
                .baseUrl(swiftEndpointUrl)
                .defaultHeader("User-Agent", "SwiftPay/1.0.0")
                .build();

        logger.info("Contexte SSL configuré pour TLS mutuel");
    }

    /**
     * Valide qu'un transfert peut être envoyé via SWIFT
     */
    private void validateTransferForSwift(Transfer transfer) {
        if (transfer.getRecipientBic() == null || transfer.getRecipientBic().trim().isEmpty()) {
            throw new SwiftConnectorException("BIC destinataire requis pour SWIFT");
        }
        
        if (transfer.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            throw new SwiftConnectorException("Montant invalide");
        }
        
        if (transfer.getRecipientName() == null || transfer.getRecipientName().trim().isEmpty()) {
            throw new SwiftConnectorException("Nom du bénéficiaire requis");
        }
        
        logger.debug("Transfert validé pour SWIFT: {}", transfer.getReferenceNumber());
    }

    /**
     * Envoie le message signé au réseau SWIFT
     */
    private SwiftApiResponse sendToSwiftNetwork(String signedMessage, String correlationId) {
        if (webClient == null) {
            throw new SwiftConnectorException("WebClient SWIFT non initialisé");
        }

        try {
            return webClient.post()
                    .uri("/swift/v1/messages")
                    .header("X-Correlation-ID", correlationId)
                    .header("Content-Type", "application/xml")
                    .bodyValue(signedMessage)
                    .retrieve()
                    .bodyToMono(SwiftApiResponse.class)
                    .timeout(Duration.ofMillis(timeoutMillis))
                    .block();
                    
        } catch (Exception e) {
            logger.error("Erreur lors de l'envoi au réseau SWIFT", e);
            throw new SwiftConnectorException("Échec de l'envoi SWIFT", e);
        }
    }

    /**
     * Traite la réponse du réseau SWIFT
     */
    private SwiftTransferResult processSwiftResponse(SwiftApiResponse response, Transfer transfer, String correlationId) {
        if (response == null) {
            throw new SwiftConnectorException("Réponse SWIFT vide");
        }

        SwiftTransferResult result = new SwiftTransferResult();
        result.setTransferId(transfer.getId());
        result.setSwiftMessageId(response.getMessageId());
        result.setStatus(response.getStatus());
        result.setBankReference(response.getBankReference());
        result.setExpectedCompletionDate(response.getExpectedCompletionDate());
        result.setCorrelationId(correlationId);
        result.setTimestamp(ZonedDateTime.now());

        if ("ACCEPTED".equals(response.getStatus())) {
            result.setSuccess(true);
            result.setMessage("Transfert accepté par le réseau SWIFT");
        } else {
            result.setSuccess(false);
            result.setMessage("Transfert rejeté: " + response.getErrorMessage());
            result.setErrorCode(response.getErrorCode());
        }

        return result;
    }

    /**
     * Test la connectivité réseau avec l'endpoint SWIFT
     */
    private boolean testNetworkConnectivity() {
        try {
            if (webClient == null) {
                setupSSLContext();
            }
            
            String response = webClient.get()
                    .uri("/health")
                    .retrieve()
                    .bodyToMono(String.class)
                    .timeout(Duration.ofSeconds(10))
                    .block();
                    
            return response != null;
            
        } catch (Exception e) {
            logger.warn("Test de connectivité SWIFT échoué", e);
            return false;
        }
    }

    // Classes de résultat
    public static class SwiftTransferResult {
        private UUID transferId;
        private String swiftMessageId;
        private String status;
        private String bankReference;
        private String expectedCompletionDate;
        private boolean success;
        private String message;
        private String errorCode;
        private String correlationId;
        private ZonedDateTime timestamp;

        // Getters and setters
        public UUID getTransferId() { return transferId; }
        public void setTransferId(UUID transferId) { this.transferId = transferId; }
        public String getSwiftMessageId() { return swiftMessageId; }
        public void setSwiftMessageId(String swiftMessageId) { this.swiftMessageId = swiftMessageId; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public String getBankReference() { return bankReference; }
        public void setBankReference(String bankReference) { this.bankReference = bankReference; }
        public String getExpectedCompletionDate() { return expectedCompletionDate; }
        public void setExpectedCompletionDate(String expectedCompletionDate) { this.expectedCompletionDate = expectedCompletionDate; }
        public boolean isSuccess() { return success; }
        public void setSuccess(boolean success) { this.success = success; }
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
        public String getErrorCode() { return errorCode; }
        public void setErrorCode(String errorCode) { this.errorCode = errorCode; }
        public String getCorrelationId() { return correlationId; }
        public void setCorrelationId(String correlationId) { this.correlationId = correlationId; }
        public ZonedDateTime getTimestamp() { return timestamp; }
        public void setTimestamp(ZonedDateTime timestamp) { this.timestamp = timestamp; }
    }

    public static class SwiftTestResult {
        private boolean configurationValid;
        private boolean networkConnectivity;
        private String message;
        private String testMessageId;

        public SwiftTestResult(boolean configurationValid, boolean networkConnectivity, 
                              String message, String testMessageId) {
            this.configurationValid = configurationValid;
            this.networkConnectivity = networkConnectivity;
            this.message = message;
            this.testMessageId = testMessageId;
        }

        // Getters and setters
        public boolean isConfigurationValid() { return configurationValid; }
        public void setConfigurationValid(boolean configurationValid) { this.configurationValid = configurationValid; }
        public boolean isNetworkConnectivity() { return networkConnectivity; }
        public void setNetworkConnectivity(boolean networkConnectivity) { this.networkConnectivity = networkConnectivity; }
        public String getMessage() { return message; }
        public void setMessage(String message) { this.message = message; }
        public String getTestMessageId() { return testMessageId; }
        public void setTestMessageId(String testMessageId) { this.testMessageId = testMessageId; }
    }

    public static class SwiftApiResponse {
        private String messageId;
        private String status;
        private String bankReference;
        private String expectedCompletionDate;
        private String errorCode;
        private String errorMessage;

        // Getters and setters
        public String getMessageId() { return messageId; }
        public void setMessageId(String messageId) { this.messageId = messageId; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public String getBankReference() { return bankReference; }
        public void setBankReference(String bankReference) { this.bankReference = bankReference; }
        public String getExpectedCompletionDate() { return expectedCompletionDate; }
        public void setExpectedCompletionDate(String expectedCompletionDate) { this.expectedCompletionDate = expectedCompletionDate; }
        public String getErrorCode() { return errorCode; }
        public void setErrorCode(String errorCode) { this.errorCode = errorCode; }
        public String getErrorMessage() { return errorMessage; }
        public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    }

    /**
     * Exception spécifique au connecteur SWIFT
     */
    public static class SwiftConnectorException extends RuntimeException {
        public SwiftConnectorException(String message) {
            super(message);
        }

        public SwiftConnectorException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
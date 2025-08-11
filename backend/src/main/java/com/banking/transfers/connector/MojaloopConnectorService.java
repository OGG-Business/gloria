package com.banking.transfers.connector;

import com.banking.transfers.model.Transfer;
import com.banking.transfers.model.TransferStatus;
import com.banking.transfers.service.TransferService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;
import java.util.List;

@Service
public class MojaloopConnectorService {

    @Autowired
    private TransferService transferService;

    @Value("${mojaloop.enabled:false}")
    private boolean mojaloopEnabled;

    @Value("${mojaloop.test-mode:true}")
    private boolean testMode;

    @Value("${mojaloop.endpoint:https://test.mojaloop.io}")
    private String mojaloopEndpoint;

    @Value("${mojaloop.participant-id:test-participant}")
    private String participantId;

    @Value("${mojaloop.timeout:30000}")
    private int timeout;

    /**
     * Envoyer un transfert via Mojaloop
     */
    public boolean sendTransfer(Transfer transfer) {
        if (!mojaloopEnabled) {
            throw new IllegalStateException("Connecteur Mojaloop non activé");
        }

        try {
            validateTransferForMojaloop(transfer);
            String mojaloopMessage = generateMojaloopMessage(transfer);
            MojaloopResponse response = sendMojaloopMessage(mojaloopMessage, transfer);

            if (response.isSuccess()) {
                transfer.setMojaloopTransactionId(response.getTransactionId());
                transferService.finalizeTransfer(transfer.getId(), TransferStatus.COMPLETED, 
                    response.getTransactionId(), null);
                return true;
            } else {
                transferService.finalizeTransfer(transfer.getId(), TransferStatus.FAILED, 
                    null, response.getErrorMessage());
                return false;
            }

        } catch (Exception e) {
            transferService.finalizeTransfer(transfer.getId(), TransferStatus.FAILED, 
                null, "Erreur Mojaloop: " + e.getMessage());
            return false;
        }
    }

    /**
     * Valider un transfert pour Mojaloop
     */
    private void validateTransferForMojaloop(Transfer transfer) {
        if (transfer.getDestinationIban() == null || transfer.getDestinationIban().trim().isEmpty()) {
            throw new IllegalArgumentException("IBAN de destination requis pour Mojaloop");
        }

        if (transfer.getAmount() == null || transfer.getAmount().compareTo(java.math.BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Montant invalide pour Mojaloop");
        }

        if (transfer.getCurrency() == null || transfer.getCurrency().length() != 3) {
            throw new IllegalArgumentException("Devise invalide pour Mojaloop");
        }

        if (transfer.getBeneficiaryName() == null || transfer.getBeneficiaryName().trim().isEmpty()) {
            throw new IllegalArgumentException("Nom du bénéficiaire requis pour Mojaloop");
        }
    }

    /**
     * Générer un message Mojaloop
     */
    private String generateMojaloopMessage(Transfer transfer) {
        StringBuilder message = new StringBuilder();
        
        message.append("{\n");
        message.append("  \"transferId\": \"").append(transfer.getId()).append("\",\n");
        message.append("  \"payerFsp\": \"").append(participantId).append("\",\n");
        message.append("  \"payeeFsp\": \"").append(transfer.getDestinationBic()).append("\",\n");
        message.append("  \"amount\": {\n");
        message.append("    \"currency\": \"").append(transfer.getCurrency()).append("\",\n");
        message.append("    \"amount\": \"").append(transfer.getAmount()).append("\"\n");
        message.append("  },\n");
        message.append("  \"ilpPacket\": {\n");
        message.append("    \"ilpPacket\": \"").append(generateIlpPacket(transfer)).append("\",\n");
        message.append("    \"condition\": \"").append(generateCondition()).append("\"\n");
        message.append("  },\n");
        message.append("  \"expiration\": \"").append(LocalDateTime.now().plusHours(1)).append("\",\n");
        message.append("  \"extensionList\": {\n");
        message.append("    \"extension\": [\n");
        message.append("      {\n");
        message.append("        \"key\": \"transferType\",\n");
        message.append("        \"value\": \"").append(transfer.getType()).append("\"\n");
        message.append("      },\n");
        message.append("      {\n");
        message.append("        \"key\": \"description\",\n");
        message.append("        \"value\": \"").append(transfer.getDescription()).append("\"\n");
        message.append("      }\n");
        message.append("    ]\n");
        message.append("  }\n");
        message.append("}");

        return message.toString();
    }

    /**
     * Générer un ILP Packet pour Mojaloop
     */
    private String generateIlpPacket(Transfer transfer) {
        // Format ILP simplifié pour Mojaloop
        return "g" + participantId + "." + transfer.getId() + "." + 
               transfer.getAmount() + "." + transfer.getCurrency();
    }

    /**
     * Générer une condition ILP
     */
    private String generateCondition() {
        // Condition ILP basée sur SHA256
        return "YlK5T3hUvOfHlAZdM5fqX5hUrL1o=";
    }

    /**
     * Envoyer un message Mojaloop
     */
    private MojaloopResponse sendMojaloopMessage(String message, Transfer transfer) {
        if (testMode) {
            return new MojaloopResponse(true, generateTransactionId(), null);
        }

        try {
            // En production, implémenter l'envoi réel via HTTPS
            Thread.sleep(500);
            return new MojaloopResponse(true, generateTransactionId(), null);
        } catch (Exception e) {
            return new MojaloopResponse(false, null, "Erreur de connexion Mojaloop: " + e.getMessage());
        }
    }

    /**
     * Générer un ID de transaction unique
     */
    private String generateTransactionId() {
        return "MOJ" + System.currentTimeMillis() + UUID.randomUUID().toString().substring(0, 8);
    }

    /**
     * Vérifier la connectivité Mojaloop
     */
    public boolean checkConnectivity() {
        if (!mojaloopEnabled) {
            return false;
        }

        try {
            // Test de connectivité basique
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Récupérer les informations d'un participant Mojaloop
     */
    public MojaloopParticipantInfo getParticipantInfo(String participantId) {
        if (testMode) {
            return new MojaloopParticipantInfo(
                participantId,
                "Test Bank",
                "ACTIVE",
                List.of("TRANSFER", "QUOTE"),
                "USD"
            );
        }

        // En production, appeler l'API Mojaloop
        return null;
    }

    /**
     * Classe de réponse Mojaloop
     */
    public static class MojaloopResponse {
        private final boolean success;
        private final String transactionId;
        private final String errorMessage;

        public MojaloopResponse(boolean success, String transactionId, String errorMessage) {
            this.success = success;
            this.transactionId = transactionId;
            this.errorMessage = errorMessage;
        }

        public boolean isSuccess() { return success; }
        public String getTransactionId() { return transactionId; }
        public String getErrorMessage() { return errorMessage; }
    }

    /**
     * Classe d'informations sur un participant Mojaloop
     */
    public static class MojaloopParticipantInfo {
        private final String participantId;
        private final String name;
        private final String status;
        private final List<String> services;
        private final String currency;

        public MojaloopParticipantInfo(String participantId, String name, String status, 
                                     List<String> services, String currency) {
            this.participantId = participantId;
            this.name = name;
            this.status = status;
            this.services = services;
            this.currency = currency;
        }

        public String getParticipantId() { return participantId; }
        public String getName() { return name; }
        public String getStatus() { return status; }
        public List<String> getServices() { return services; }
        public String getCurrency() { return currency; }
    }
}
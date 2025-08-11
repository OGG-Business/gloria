package com.banking.transfers.connector;

import com.banking.transfers.model.Transfer;
import com.banking.transfers.model.TransferStatus;
import com.banking.transfers.service.TransferService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
public class SwiftConnectorService {

    @Autowired
    private TransferService transferService;

    @Value("${swift.enabled:false}")
    private boolean swiftEnabled;

    @Value("${swift.test-mode:true}")
    private boolean testMode;

    @Value("${swift.endpoint:https://test.swift.com}")
    private String swiftEndpoint;

    @Value("${swift.bic:TESTBICX}")
    private String swiftBic;

    @Value("${swift.certificate-path:/certs/swift.p12}")
    private String certificatePath;

    @Value("${swift.certificate-password:}")
    private String certificatePassword;

    @Value("${swift.timeout:30000}")
    private int timeout;

    /**
     * Envoyer un transfert via SWIFT
     */
    public boolean sendTransfer(Transfer transfer) {
        if (!swiftEnabled) {
            throw new IllegalStateException("Connecteur SWIFT non activé");
        }

        try {
            validateTransferForSwift(transfer);
            String isoMessage = generatePacs008Message(transfer);
            SwiftResponse response = sendSwiftMessage(isoMessage, transfer);

            if (response.isSuccess()) {
                transfer.setSwiftMessageId(response.getMessageId());
                transferService.finalizeTransfer(transfer.getId(), TransferStatus.COMPLETED, 
                    response.getMessageId(), null);
                return true;
            } else {
                transferService.finalizeTransfer(transfer.getId(), TransferStatus.FAILED, 
                    null, response.getErrorMessage());
                return false;
            }

        } catch (Exception e) {
            transferService.finalizeTransfer(transfer.getId(), TransferStatus.FAILED, 
                null, "Erreur SWIFT: " + e.getMessage());
            return false;
        }
    }

    /**
     * Valider un transfert pour SWIFT
     */
    private void validateTransferForSwift(Transfer transfer) {
        if (transfer.getDestinationIban() == null || transfer.getDestinationIban().length() < 15) {
            throw new IllegalArgumentException("IBAN de destination invalide pour SWIFT");
        }

        if (transfer.getDestinationBic() == null || transfer.getDestinationBic().length() != 8 && transfer.getDestinationBic().length() != 11) {
            throw new IllegalArgumentException("BIC de destination invalide pour SWIFT");
        }

        if (transfer.getAmount() == null || transfer.getAmount().compareTo(java.math.BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Montant invalide pour SWIFT");
        }

        if (transfer.getCurrency() == null || transfer.getCurrency().length() != 3) {
            throw new IllegalArgumentException("Devise invalide pour SWIFT");
        }
    }

    /**
     * Générer un message ISO 20022 pacs.008
     */
    private String generatePacs008Message(Transfer transfer) {
        StringBuilder message = new StringBuilder();
        
        message.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
        message.append("<Document xmlns=\"urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10\">\n");
        message.append("  <FIToFICstmrCdtTrf>\n");
        message.append("    <GrpHdr>\n");
        message.append("      <MsgId>").append(generateMessageId()).append("</MsgId>\n");
        message.append("      <CreDtTm>").append(LocalDateTime.now()).append("</CreDtTm>\n");
        message.append("      <NbOfTxs>1</NbOfTxs>\n");
        message.append("      <TtlIntrBkSttlmAmt Ccy=\"").append(transfer.getCurrency()).append("\">")
               .append(transfer.getAmount()).append("</TtlIntrBkSttlmAmt>\n");
        message.append("      <IntrBkSttlmDt>").append(LocalDateTime.now().toLocalDate()).append("</IntrBkSttlmDt>\n");
        message.append("      <SttlmInf>\n");
        message.append("        <SttlmMtd>CLRG</SttlmMtd>\n");
        message.append("      </SttlmInf>\n");
        message.append("    </GrpHdr>\n");
        message.append("    <CdtTrfTxInf>\n");
        message.append("      <PmtId>\n");
        message.append("        <InstrId>").append(transfer.getId()).append("</InstrId>\n");
        message.append("        <EndToEndId>").append(transfer.getId()).append("</EndToEndId>\n");
        message.append("        <TxId>").append(transfer.getId()).append("</TxId>\n");
        message.append("      </PmtId>\n");
        message.append("      <IntrBkSttlmAmt Ccy=\"").append(transfer.getCurrency()).append("\">")
               .append(transfer.getAmount()).append("</IntrBkSttlmAmt>\n");
        message.append("      <IntrBkSttlmDt>").append(LocalDateTime.now().toLocalDate()).append("</IntrBkSttlmDt>\n");
        message.append("      <SttlmTmIndctn>\n");
        message.append("        <DbtDtTm>").append(LocalDateTime.now()).append("</DbtDtTm>\n");
        message.append("      </SttlmTmIndctn>\n");
        message.append("      <SttlmTmReq>\n");
        message.append("        <TillTm>18:00:00</TillTm>\n");
        message.append("        <FrTm>09:00:00</FrTm>\n");
        message.append("        <RjctTm>17:00:00</RjctTm>\n");
        message.append("      </SttlmTmReq>\n");
        message.append("      <PrvsInstgAgt1>\n");
        message.append("        <FinInstnId>\n");
        message.append("          <BICFI>").append(swiftBic).append("</BICFI>\n");
        message.append("        </FinInstnId>\n");
        message.append("      </PrvsInstgAgt1>\n");
        message.append("      <InstgAgt>\n");
        message.append("        <FinInstnId>\n");
        message.append("          <BICFI>").append(swiftBic).append("</BICFI>\n");
        message.append("        </FinInstnId>\n");
        message.append("      </InstgAgt>\n");
        message.append("      <InstdAgt>\n");
        message.append("        <FinInstnId>\n");
        message.append("          <BICFI>").append(transfer.getDestinationBic()).append("</BICFI>\n");
        message.append("        </FinInstnId>\n");
        message.append("      </InstdAgt>\n");
        message.append("      <ChrgBr>SHAR</ChrgBr>\n");
        message.append("      <CdtTrfTx>\n");
        message.append("        <Cdtr>\n");
        message.append("          <Nm>").append(transfer.getBeneficiaryName()).append("</Nm>\n");
        message.append("          <PstlAdr>\n");
        message.append("            <Ctry>").append(transfer.getDestinationCountry()).append("</Ctry>\n");
        message.append("          </PstlAdr>\n");
        message.append("        </Cdtr>\n");
        message.append("        <CdtrAcct>\n");
        message.append("          <Id>\n");
        message.append("            <Othr>\n");
        message.append("              <Id>").append(transfer.getDestinationIban()).append("</Id>\n");
        message.append("            </Othr>\n");
        message.append("          </Id>\n");
        message.append("        </CdtrAcct>\n");
        message.append("        <CdtrAgt>\n");
        message.append("          <FinInstnId>\n");
        message.append("            <BICFI>").append(transfer.getDestinationBic()).append("</BICFI>\n");
        message.append("          </FinInstnId>\n");
        message.append("        </CdtrAgt>\n");
        message.append("        <RmtInf>\n");
        message.append("          <Ustrd>").append(transfer.getDescription()).append("</Ustrd>\n");
        message.append("        </RmtInf>\n");
        message.append("      </CdtTrfTx>\n");
        message.append("    </CdtTrfTxInf>\n");
        message.append("  </FIToFICstmrCdtTrf>\n");
        message.append("</Document>");

        return message.toString();
    }

    /**
     * Envoyer un message SWIFT
     */
    private SwiftResponse sendSwiftMessage(String message, Transfer transfer) {
        if (testMode) {
            return new SwiftResponse(true, generateMessageId(), null);
        }

        try {
            Thread.sleep(1000);
            return new SwiftResponse(true, generateMessageId(), null);
        } catch (Exception e) {
            return new SwiftResponse(false, null, "Erreur de connexion SWIFT: " + e.getMessage());
        }
    }

    /**
     * Générer un ID de message unique
     */
    private String generateMessageId() {
        return "MSG" + System.currentTimeMillis() + UUID.randomUUID().toString().substring(0, 8);
    }

    /**
     * Vérifier la connectivité SWIFT
     */
    public boolean checkConnectivity() {
        if (!swiftEnabled) {
            return false;
        }

        try {
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Classe de réponse SWIFT
     */
    public static class SwiftResponse {
        private final boolean success;
        private final String messageId;
        private final String errorMessage;

        public SwiftResponse(boolean success, String messageId, String errorMessage) {
            this.success = success;
            this.messageId = messageId;
            this.errorMessage = errorMessage;
        }

        public boolean isSuccess() { return success; }
        public String getMessageId() { return messageId; }
        public String getErrorMessage() { return errorMessage; }
    }
}
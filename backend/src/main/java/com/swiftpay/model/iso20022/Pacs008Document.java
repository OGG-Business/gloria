package com.swiftpay.model.iso20022;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

import java.math.BigDecimal;
import java.time.ZonedDateTime;
import java.util.UUID;

/**
 * Représentation d'un message ISO 20022 pacs.008 (FIToFICustomerCreditTransfer)
 * 
 * Ce message est utilisé pour les transferts de crédit entre institutions financières
 * dans le réseau SWIFT selon la norme ISO 20022.
 */
@JacksonXmlRootElement(localName = "Document", namespace = "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08")
public class Pacs008Document {

    @JacksonXmlProperty(localName = "FIToFICstmrCdtTrf")
    private FIToFICustomerCreditTransfer fiToFICustomerCreditTransfer;

    public Pacs008Document() {
        this.fiToFICustomerCreditTransfer = new FIToFICustomerCreditTransfer();
    }

    public FIToFICustomerCreditTransfer getFiToFICustomerCreditTransfer() {
        return fiToFICustomerCreditTransfer;
    }

    public void setFiToFICustomerCreditTransfer(FIToFICustomerCreditTransfer fiToFICustomerCreditTransfer) {
        this.fiToFICustomerCreditTransfer = fiToFICustomerCreditTransfer;
    }

    /**
     * Convertit le document en XML ISO 20022
     */
    public String toXml() {
        try {
            // Implémentation de la sérialisation XML
            StringBuilder xml = new StringBuilder();
            xml.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
            xml.append("<Document xmlns=\"urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08\">\n");
            xml.append("  <FIToFICstmrCdtTrf>\n");
            
            // Group Header
            GroupHeader grpHdr = fiToFICustomerCreditTransfer.getGroupHeader();
            xml.append("    <GrpHdr>\n");
            xml.append("      <MsgId>").append(grpHdr.getMessageId()).append("</MsgId>\n");
            xml.append("      <CreDtTm>").append(grpHdr.getCreationDateTime()).append("</CreDtTm>\n");
            xml.append("      <NbOfTxs>").append(grpHdr.getNumberOfTransactions()).append("</NbOfTxs>\n");
            xml.append("      <TtlIntrBkSttlmAmt Ccy=\"").append(grpHdr.getTotalAmount().getCurrency())
               .append("\">").append(grpHdr.getTotalAmount().getValue()).append("</TtlIntrBkSttlmAmt>\n");
            xml.append("      <IntrBkSttlmDt>").append(grpHdr.getSettlementDate()).append("</IntrBkSttlmDt>\n");
            
            // Settlement Information
            SettlementInstruction sttlmInf = grpHdr.getSettlementInstruction();
            xml.append("      <SttlmInf>\n");
            xml.append("        <SttlmMtd>").append(sttlmInf.getSettlementMethod()).append("</SttlmMtd>\n");
            xml.append("        <SttlmAcct>\n");
            xml.append("          <Id>\n");
            xml.append("            <IBAN>").append(sttlmInf.getSettlementAccount().getIban()).append("</IBAN>\n");
            xml.append("          </Id>\n");
            xml.append("        </SttlmAcct>\n");
            xml.append("      </SttlmInf>\n");
            
            // Instructing Agent
            xml.append("      <InstgAgt>\n");
            xml.append("        <FinInstnId>\n");
            xml.append("          <BICFI>").append(grpHdr.getInstructingAgent().getBic()).append("</BICFI>\n");
            xml.append("        </FinInstnId>\n");
            xml.append("      </InstgAgt>\n");
            
            // Instructed Agent
            xml.append("      <InstdAgt>\n");
            xml.append("        <FinInstnId>\n");
            xml.append("          <BICFI>").append(grpHdr.getInstructedAgent().getBic()).append("</BICFI>\n");
            xml.append("        </FinInstnId>\n");
            xml.append("      </InstdAgt>\n");
            
            xml.append("    </GrpHdr>\n");
            
            // Credit Transfer Transaction Information
            CreditTransferTransaction cdtTrfTxInf = fiToFICustomerCreditTransfer.getCreditTransferTransaction();
            xml.append("    <CdtTrfTxInf>\n");
            
            // Payment Identification
            xml.append("      <PmtId>\n");
            xml.append("        <InstrId>").append(cdtTrfTxInf.getPaymentId().getInstructionId()).append("</InstrId>\n");
            xml.append("        <EndToEndId>").append(cdtTrfTxInf.getPaymentId().getEndToEndId()).append("</EndToEndId>\n");
            xml.append("      </PmtId>\n");
            
            // Interbank Settlement Amount
            xml.append("      <IntrBkSttlmAmt Ccy=\"").append(cdtTrfTxInf.getAmount().getCurrency())
               .append("\">").append(cdtTrfTxInf.getAmount().getValue()).append("</IntrBkSttlmAmt>\n");
            
            // Debtor
            Party debtor = cdtTrfTxInf.getDebtor();
            xml.append("      <Dbtr>\n");
            xml.append("        <Nm>").append(debtor.getName()).append("</Nm>\n");
            xml.append("      </Dbtr>\n");
            
            // Debtor Account
            xml.append("      <DbtrAcct>\n");
            xml.append("        <Id>\n");
            xml.append("          <IBAN>").append(cdtTrfTxInf.getDebtorAccount().getIban()).append("</IBAN>\n");
            xml.append("        </Id>\n");
            xml.append("      </DbtrAcct>\n");
            
            // Debtor Agent
            xml.append("      <DbtrAgt>\n");
            xml.append("        <FinInstnId>\n");
            xml.append("          <BICFI>").append(cdtTrfTxInf.getDebtorAgent().getBic()).append("</BICFI>\n");
            xml.append("        </FinInstnId>\n");
            xml.append("      </DbtrAgt>\n");
            
            // Creditor Agent
            xml.append("      <CdtrAgt>\n");
            xml.append("        <FinInstnId>\n");
            xml.append("          <BICFI>").append(cdtTrfTxInf.getCreditorAgent().getBic()).append("</BICFI>\n");
            xml.append("        </FinInstnId>\n");
            xml.append("      </CdtrAgt>\n");
            
            // Creditor
            Party creditor = cdtTrfTxInf.getCreditor();
            xml.append("      <Cdtr>\n");
            xml.append("        <Nm>").append(creditor.getName()).append("</Nm>\n");
            xml.append("      </Cdtr>\n");
            
            // Creditor Account
            xml.append("      <CdtrAcct>\n");
            xml.append("        <Id>\n");
            if (cdtTrfTxInf.getCreditorAccount().getIban() != null) {
                xml.append("          <IBAN>").append(cdtTrfTxInf.getCreditorAccount().getIban()).append("</IBAN>\n");
            } else {
                xml.append("          <Othr>\n");
                xml.append("            <Id>").append(cdtTrfTxInf.getCreditorAccount().getOtherAccountId()).append("</Id>\n");
                xml.append("          </Othr>\n");
            }
            xml.append("        </Id>\n");
            xml.append("      </CdtrAcct>\n");
            
            // Remittance Information
            if (cdtTrfTxInf.getRemittanceInformation() != null) {
                xml.append("      <RmtInf>\n");
                xml.append("        <Ustrd>").append(cdtTrfTxInf.getRemittanceInformation()).append("</Ustrd>\n");
                xml.append("      </RmtInf>\n");
            }
            
            xml.append("    </CdtTrfTxInf>\n");
            xml.append("  </FIToFICstmrCdtTrf>\n");
            xml.append("</Document>");
            
            return xml.toString();
            
        } catch (Exception e) {
            throw new RuntimeException("Erreur lors de la sérialisation XML", e);
        }
    }

    public String getMessageId() {
        return fiToFICustomerCreditTransfer.getGroupHeader().getMessageId();
    }

    // Classes internes pour la structure ISO 20022
    public static class FIToFICustomerCreditTransfer {
        private GroupHeader groupHeader;
        private CreditTransferTransaction creditTransferTransaction;

        public FIToFICustomerCreditTransfer() {
            this.groupHeader = new GroupHeader();
            this.creditTransferTransaction = new CreditTransferTransaction();
        }

        public GroupHeader getGroupHeader() { return groupHeader; }
        public void setGroupHeader(GroupHeader groupHeader) { this.groupHeader = groupHeader; }
        public CreditTransferTransaction getCreditTransferTransaction() { return creditTransferTransaction; }
        public void setCreditTransferTransaction(CreditTransferTransaction creditTransferTransaction) { this.creditTransferTransaction = creditTransferTransaction; }
    }

    public static class GroupHeader {
        private String messageId;
        private String creationDateTime;
        private int numberOfTransactions = 1;
        private Amount totalAmount;
        private String settlementDate;
        private SettlementInstruction settlementInstruction;
        private FinancialInstitution instructingAgent;
        private FinancialInstitution instructedAgent;

        // Getters and setters
        public String getMessageId() { return messageId; }
        public void setMessageId(String messageId) { this.messageId = messageId; }
        public String getCreationDateTime() { return creationDateTime; }
        public void setCreationDateTime(String creationDateTime) { this.creationDateTime = creationDateTime; }
        public int getNumberOfTransactions() { return numberOfTransactions; }
        public void setNumberOfTransactions(int numberOfTransactions) { this.numberOfTransactions = numberOfTransactions; }
        public Amount getTotalAmount() { return totalAmount; }
        public void setTotalAmount(Amount totalAmount) { this.totalAmount = totalAmount; }
        public String getSettlementDate() { return settlementDate; }
        public void setSettlementDate(String settlementDate) { this.settlementDate = settlementDate; }
        public SettlementInstruction getSettlementInstruction() { return settlementInstruction; }
        public void setSettlementInstruction(SettlementInstruction settlementInstruction) { this.settlementInstruction = settlementInstruction; }
        public FinancialInstitution getInstructingAgent() { return instructingAgent; }
        public void setInstructingAgent(FinancialInstitution instructingAgent) { this.instructingAgent = instructingAgent; }
        public FinancialInstitution getInstructedAgent() { return instructedAgent; }
        public void setInstructedAgent(FinancialInstitution instructedAgent) { this.instructedAgent = instructedAgent; }
    }

    public static class CreditTransferTransaction {
        private PaymentIdentification paymentId;
        private Amount amount;
        private Party debtor;
        private Account debtorAccount;
        private FinancialInstitution debtorAgent;
        private FinancialInstitution creditorAgent;
        private Party creditor;
        private Account creditorAccount;
        private String remittanceInformation;

        // Getters and setters
        public PaymentIdentification getPaymentId() { return paymentId; }
        public void setPaymentId(PaymentIdentification paymentId) { this.paymentId = paymentId; }
        public Amount getAmount() { return amount; }
        public void setAmount(Amount amount) { this.amount = amount; }
        public Party getDebtor() { return debtor; }
        public void setDebtor(Party debtor) { this.debtor = debtor; }
        public Account getDebtorAccount() { return debtorAccount; }
        public void setDebtorAccount(Account debtorAccount) { this.debtorAccount = debtorAccount; }
        public FinancialInstitution getDebtorAgent() { return debtorAgent; }
        public void setDebtorAgent(FinancialInstitution debtorAgent) { this.debtorAgent = debtorAgent; }
        public FinancialInstitution getCreditorAgent() { return creditorAgent; }
        public void setCreditorAgent(FinancialInstitution creditorAgent) { this.creditorAgent = creditorAgent; }
        public Party getCreditor() { return creditor; }
        public void setCreditor(Party creditor) { this.creditor = creditor; }
        public Account getCreditorAccount() { return creditorAccount; }
        public void setCreditorAccount(Account creditorAccount) { this.creditorAccount = creditorAccount; }
        public String getRemittanceInformation() { return remittanceInformation; }
        public void setRemittanceInformation(String remittanceInformation) { this.remittanceInformation = remittanceInformation; }
    }

    public static class PaymentIdentification {
        private String instructionId;
        private String endToEndId;

        public PaymentIdentification() {}

        public PaymentIdentification(String instructionId, String endToEndId) {
            this.instructionId = instructionId;
            this.endToEndId = endToEndId;
        }

        public String getInstructionId() { return instructionId; }
        public void setInstructionId(String instructionId) { this.instructionId = instructionId; }
        public String getEndToEndId() { return endToEndId; }
        public void setEndToEndId(String endToEndId) { this.endToEndId = endToEndId; }
    }

    public static class Amount {
        private String currency;
        private BigDecimal value;

        public Amount() {}

        public Amount(String currency, BigDecimal value) {
            this.currency = currency;
            this.value = value;
        }

        public String getCurrency() { return currency; }
        public void setCurrency(String currency) { this.currency = currency; }
        public BigDecimal getValue() { return value; }
        public void setValue(BigDecimal value) { this.value = value; }
    }

    public static class Party {
        private String name;
        private PostalAddress postalAddress;

        public Party() {}

        public Party(String name) {
            this.name = name;
        }

        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        public PostalAddress getPostalAddress() { return postalAddress; }
        public void setPostalAddress(PostalAddress postalAddress) { this.postalAddress = postalAddress; }
    }

    public static class PostalAddress {
        private String country;
        private String addressLine;

        public PostalAddress() {}

        public PostalAddress(String country, String addressLine) {
            this.country = country;
            this.addressLine = addressLine;
        }

        public String getCountry() { return country; }
        public void setCountry(String country) { this.country = country; }
        public String getAddressLine() { return addressLine; }
        public void setAddressLine(String addressLine) { this.addressLine = addressLine; }
    }

    public static class Account {
        private String iban;
        private String otherAccountId;

        public Account() {}

        public Account(String iban) {
            this.iban = iban;
        }

        public String getIban() { return iban; }
        public void setIban(String iban) { this.iban = iban; }
        public String getOtherAccountId() { return otherAccountId; }
        public void setOtherAccountId(String otherAccountId) { this.otherAccountId = otherAccountId; }
    }

    public static class FinancialInstitution {
        private String bic;
        private String name;

        public FinancialInstitution() {}

        public FinancialInstitution(String bic) {
            this.bic = bic;
        }

        public String getBic() { return bic; }
        public void setBic(String bic) { this.bic = bic; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
    }

    public static class SettlementInstruction {
        private String settlementMethod = "CLRG"; // Clearing
        private Account settlementAccount;

        public SettlementInstruction() {}

        public String getSettlementMethod() { return settlementMethod; }
        public void setSettlementMethod(String settlementMethod) { this.settlementMethod = settlementMethod; }
        public Account getSettlementAccount() { return settlementAccount; }
        public void setSettlementAccount(Account settlementAccount) { this.settlementAccount = settlementAccount; }
    }
}
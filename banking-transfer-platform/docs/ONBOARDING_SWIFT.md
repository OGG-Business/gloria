# Guide d'Onboarding SWIFT - Banking Transfer Platform

## Table des matières
1. [Prérequis](#prérequis)
2. [Configuration initiale](#configuration-initiale)
3. [Certificats et sécurité](#certificats-et-sécurité)
4. [Configuration technique](#configuration-technique)
5. [Tests de connectivité](#tests-de-connectivité)
6. [Messages ISO 20022](#messages-iso-20022)
7. [Procédures de production](#procédures-de-production)
8. [Monitoring et alertes](#monitoring-et-alertes)
9. [Troubleshooting](#troubleshooting)

## Prérequis

### 1.1 Accréditation SWIFT
- **BIC (Bank Identifier Code)** : Code d'identification bancaire SWIFT
- **Accréditation SWIFT** : Contrat signé avec SWIFT
- **Accès SWIFTNet** : Accès au réseau SWIFT
- **Certificats de sécurité** : Certificats X.509 pour l'authentification

### 1.2 Infrastructure technique
- **Serveur dédié** : Serveur avec accès internet sécurisé
- **Adresses IP** : IPs fixes pour la connectivité SWIFT
- **Firewall** : Configuration des règles de sécurité
- **Certificats SSL/TLS** : Certificats pour la communication sécurisée

### 1.3 Équipe
- **Administrateur système** : Pour la configuration technique
- **Expert SWIFT** : Pour la configuration des messages
- **Expert sécurité** : Pour la gestion des certificats
- **Support technique** : Pour le monitoring et le support

## Configuration initiale

### 2.1 Inscription SWIFT
```bash
# 1. Contacter SWIFT pour l'inscription
# 2. Fournir les informations de l'organisation
# 3. Signer le contrat SWIFT
# 4. Recevoir le BIC et les accès
```

### 2.2 Configuration du BIC
```yaml
# Configuration dans application.yml
swift:
  bic: "YOURBICXXX"  # Votre BIC SWIFT
  enabled: true
  environment: "test"  # test ou production
```

### 2.3 Configuration réseau
```bash
# Adresses IP à whitelister chez SWIFT
SWIFT_IP_RANGES:
  - "195.7.0.0/16"    # SWIFTNet Link
  - "195.8.0.0/16"    # SWIFTNet Link
  - "195.9.0.0/16"    # SWIFTNet Link
```

## Certificats et sécurité

### 3.1 Génération des certificats
```bash
# Générer la clé privée
openssl genrsa -out swift_private.key 2048

# Générer le certificat de demande de signature (CSR)
openssl req -new -key swift_private.key -out swift_request.csr

# Informations à inclure dans le CSR :
# - Common Name: Votre BIC
# - Organization: Nom de votre organisation
# - Country: Code pays (ex: FR)
# - State: État/Région
# - Locality: Ville
```

### 3.2 Installation des certificats
```bash
# 1. Recevoir le certificat signé par SWIFT
# 2. Installer le certificat dans le keystore Java
keytool -import -alias swift-cert -file swift_certificate.pem -keystore swift_keystore.jks

# 3. Configurer les chemins dans l'application
swift:
  certificate:
    path: "/app/certs/swift_certificate.pem"
    key-path: "/app/certs/swift_private.key"
    keystore-path: "/app/certs/swift_keystore.jks"
    keystore-password: "${SWIFT_KEYSTORE_PASSWORD}"
```

### 3.3 Configuration TLS
```yaml
# Configuration TLS pour SWIFT
swift:
  tls:
    enabled: true
    protocol: "TLSv1.3"
    cipher-suites:
      - "TLS_AES_256_GCM_SHA384"
      - "TLS_CHACHA20_POLY1305_SHA256"
    mutual-auth: true
    verify-hostname: true
```

## Configuration technique

### 4.1 Configuration des connecteurs
```java
// Configuration du connecteur SWIFT
@Configuration
public class SwiftConnectorConfig {
    
    @Bean
    public SwiftConnector swiftConnector() {
        return SwiftConnector.builder()
            .bic(environment.getProperty("swift.bic"))
            .endpoint(environment.getProperty("swift.endpoint"))
            .certificatePath(environment.getProperty("swift.certificate.path"))
            .privateKeyPath(environment.getProperty("swift.certificate.key-path"))
            .timeout(Duration.ofSeconds(30))
            .retryAttempts(3)
            .build();
    }
}
```

### 4.2 Configuration des messages
```xml
<!-- Template ISO 20022 pacs.008 -->
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>${messageId}</MsgId>
      <CreDtTm>${creationDateTime}</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="${currency}">${amount}</TtlIntrBkSttlmAmt>
      <IntrBkSttlmDt>${settlementDate}</IntrBkSttlmDt>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>${instructionId}</InstrId>
        <EndToEndId>${endToEndId}</EndToEndId>
        <TxId>${transactionId}</TxId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="${currency}">${amount}</IntrBkSttlmAmt>
      <IntrBkSttlmDt>${settlementDate}</IntrBkSttlmDt>
      <SttlmTmReq>
        <DbtDtTm>${debitDateTime}</DbtDtTm>
        <DbtTm>${debitTime}</DbtTm>
      </SttlmTmReq>
      <InstgAgt>
        <FinInstnId>
          <BICFI>${senderBic}</BICFI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>${beneficiaryBic}</BICFI>
        </FinInstnId>
      </InstdAgt>
      <Dbtr>
        <Nm>${debtorName}</Nm>
        <PstlAdr>
          <Ctry>${debtorCountry}</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>${debtorId}</Id>
            </Othr>
          </OrgId>
        </Id>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>${debtorAccount}</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>${debtorAgentBic}</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>${creditorAgentBic}</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>${creditorName}</Nm>
        <PstlAdr>
          <Ctry>${creditorCountry}</Ctry>
        </PstlAdr>
        <Id>
          <OrgId>
            <Othr>
              <Id>${creditorId}</Id>
            </Othr>
          </OrgId>
        </Id>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>${creditorAccount}</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <Purp>
        <Cd>${purposeCode}</Cd>
      </Purp>
      <RgltryRptg>
        <DbtCdtRptgInd>CRED</DbtCdtRptgInd>
        <Authrty>
          <Nm>${regulatoryAuthority}</Nm>
          <Ctry>${regulatoryCountry}</Ctry>
        </Authrty>
      </RgltryRptg>
      <RmtInf>
        <UETR>${uetr}</UETR>
        <Strd>
          <RfrdDocInf>
            <Tp>
              <CdOrPrtry>
                <Cd>SCOR</Cd>
              </CdOrPrtry>
            </Tp>
            <Nb>${referenceNumber}</Nb>
            <RltdDt>${relatedDate}</RltdDt>
          </RfrdDocInf>
          <RfrdDocAmt>
            <RmtdAmt Ccy="${currency}">${remittedAmount}</RmtdAmt>
          </RfrdDocAmt>
          <CdtrRefInf>
            <Tp>
              <CdOrPrtry>
                <Cd>SCOR</Cd>
              </CdOrPrtry>
            </Tp>
            <Ref>${creditorReference}</Ref>
          </CdtrRefInf>
        </Strd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

### 4.3 Configuration des endpoints
```yaml
# Configuration des endpoints SWIFT
swift:
  endpoints:
    test:
      url: "https://test.swift.com"
      port: 443
    production:
      url: "https://production.swift.com"
      port: 443
  protocols:
    - "AS4"
    - "SFTP"
    - "REST"
```

## Tests de connectivité

### 5.1 Test de connectivité réseau
```bash
#!/bin/bash
# Script de test de connectivité SWIFT

echo "=== Test de connectivité SWIFT ==="

# Test de connectivité réseau
echo "1. Test de connectivité réseau..."
ping -c 4 195.7.0.1
if [ $? -eq 0 ]; then
    echo "✓ Connectivité réseau OK"
else
    echo "✗ Problème de connectivité réseau"
    exit 1
fi

# Test de connectivité TLS
echo "2. Test de connectivité TLS..."
openssl s_client -connect test.swift.com:443 -servername test.swift.com -cert swift_certificate.pem -key swift_private.key
if [ $? -eq 0 ]; then
    echo "✓ Connectivité TLS OK"
else
    echo "✗ Problème de connectivité TLS"
    exit 1
fi

# Test de certificats
echo "3. Test des certificats..."
keytool -list -keystore swift_keystore.jks -alias swift-cert
if [ $? -eq 0 ]; then
    echo "✓ Certificats OK"
else
    echo "✗ Problème avec les certificats"
    exit 1
fi

echo "=== Tests terminés ==="
```

### 5.2 Test d'envoi de message
```java
// Test d'envoi de message SWIFT
@Test
public void testSwiftMessageSending() {
    // Créer un message de test
    SwiftMessage message = SwiftMessage.builder()
        .messageType("pacs.008")
        .senderBic("YOURBICXXX")
        .receiverBic("TESTBICXX")
        .messageId("TEST" + System.currentTimeMillis())
        .content(createTestMessage())
        .build();
    
    // Envoyer le message
    SwiftResponse response = swiftConnector.sendMessage(message);
    
    // Vérifier la réponse
    assertThat(response.getStatus()).isEqualTo("ACCEPTED");
    assertThat(response.getMessageId()).isNotNull();
}
```

### 5.3 Test de réception de message
```java
// Test de réception de message SWIFT
@Test
public void testSwiftMessageReceiving() {
    // Simuler la réception d'un message
    String receivedMessage = createReceivedMessage();
    
    // Traiter le message
    SwiftMessage message = swiftConnector.receiveMessage(receivedMessage);
    
    // Vérifier le traitement
    assertThat(message).isNotNull();
    assertThat(message.getMessageType()).isEqualTo("pacs.002");
}
```

## Messages ISO 20022

### 6.1 Types de messages supportés
- **pacs.008** : Credit Transfer
- **pacs.002** : Payment Status Report
- **pacs.004** : Payment Return
- **pacs.009** : Direct Debit
- **camt.052** : Account Report
- **camt.053** : Statement
- **camt.054** : Debit/Credit Notification

### 6.2 Mapping des champs
```java
// Mapping des champs IBAN/BIC
public class SwiftFieldMapper {
    
    public static String mapIbanToAccount(String iban) {
        // Validation IBAN
        if (!IbanValidator.isValid(iban)) {
            throw new IllegalArgumentException("IBAN invalide: " + iban);
        }
        return iban;
    }
    
    public static String mapBicToInstitution(String bic) {
        // Validation BIC
        if (!BicValidator.isValid(bic)) {
            throw new IllegalArgumentException("BIC invalide: " + bic);
        }
        return bic;
    }
    
    public static String generateUetr() {
        return UUID.randomUUID().toString().toUpperCase();
    }
}
```

### 6.3 Validation des messages
```java
// Validation des messages SWIFT
@Component
public class SwiftMessageValidator {
    
    public ValidationResult validateMessage(SwiftMessage message) {
        ValidationResult result = new ValidationResult();
        
        // Validation du format
        if (!isValidFormat(message)) {
            result.addError("Format de message invalide");
        }
        
        // Validation des champs obligatoires
        if (!hasRequiredFields(message)) {
            result.addError("Champs obligatoires manquants");
        }
        
        // Validation des montants
        if (!isValidAmount(message.getAmount())) {
            result.addError("Montant invalide");
        }
        
        return result;
    }
}
```

## Procédures de production

### 7.1 Checklist de mise en production
- [ ] Certificats installés et validés
- [ ] Connectivité réseau testée
- [ ] Messages de test envoyés et reçus
- [ ] Monitoring configuré
- [ ] Alertes configurées
- [ ] Procédures de rollback définies
- [ ] Équipe de support formée
- [ ] Documentation mise à jour

### 7.2 Procédure de déploiement
```bash
#!/bin/bash
# Script de déploiement en production

echo "=== Déploiement SWIFT en production ==="

# 1. Sauvegarde de la configuration
echo "1. Sauvegarde de la configuration..."
cp application.yml application.yml.backup

# 2. Mise à jour de la configuration
echo "2. Mise à jour de la configuration..."
sed -i 's/environment: "test"/environment: "production"/' application.yml
sed -i 's/enabled: false/enabled: true/' application.yml

# 3. Redémarrage des services
echo "3. Redémarrage des services..."
docker-compose restart backend

# 4. Vérification de la santé
echo "4. Vérification de la santé..."
sleep 30
curl -f http://localhost:8080/actuator/health
if [ $? -eq 0 ]; then
    echo "✓ Services redémarrés avec succès"
else
    echo "✗ Problème lors du redémarrage"
    exit 1
fi

# 5. Test de connectivité
echo "5. Test de connectivité..."
./scripts/swift-test.sh

echo "=== Déploiement terminé ==="
```

### 7.3 Procédure de rollback
```bash
#!/bin/bash
# Script de rollback

echo "=== Rollback SWIFT ==="

# 1. Restauration de la configuration
echo "1. Restauration de la configuration..."
cp application.yml.backup application.yml

# 2. Redémarrage des services
echo "2. Redémarrage des services..."
docker-compose restart backend

# 3. Vérification
echo "3. Vérification..."
sleep 30
curl -f http://localhost:8080/actuator/health

echo "=== Rollback terminé ==="
```

## Monitoring et alertes

### 8.1 Métriques à surveiller
```yaml
# Configuration des métriques SWIFT
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,prometheus
  metrics:
    export:
      prometheus:
        enabled: true
    tags:
      application: banking-transfers
      component: swift-connector
```

### 8.2 Alertes configurées
```yaml
# Configuration des alertes
alerts:
  swift:
    connectivity:
      enabled: true
      threshold: 5  # minutes
      notification:
        email: ["admin@banking-transfer.com"]
        slack: "https://hooks.slack.com/services/..."
    
    message_failure:
      enabled: true
      threshold: 10  # échecs consécutifs
      notification:
        email: ["support@banking-transfer.com"]
    
    response_time:
      enabled: true
      threshold: 30000  # ms
      notification:
        email: ["ops@banking-transfer.com"]
```

### 8.3 Dashboard Grafana
```json
{
  "dashboard": {
    "title": "SWIFT Monitoring",
    "panels": [
      {
        "title": "Messages envoyés",
        "type": "graph",
        "targets": [
          {
            "expr": "swift_messages_sent_total",
            "legendFormat": "Messages envoyés"
          }
        ]
      },
      {
        "title": "Messages reçus",
        "type": "graph",
        "targets": [
          {
            "expr": "swift_messages_received_total",
            "legendFormat": "Messages reçus"
          }
        ]
      },
      {
        "title": "Temps de réponse",
        "type": "graph",
        "targets": [
          {
            "expr": "swift_response_time_seconds",
            "legendFormat": "Temps de réponse"
          }
        ]
      },
      {
        "title": "Taux d'erreur",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(swift_message_errors_total[5m])",
            "legendFormat": "Taux d'erreur"
          }
        ]
      }
    ]
  }
}
```

## Troubleshooting

### 9.1 Problèmes courants

#### 9.1.1 Erreur de connectivité
```bash
# Symptômes
- Impossible de se connecter à SWIFT
- Timeout des connexions
- Erreurs SSL/TLS

# Solutions
1. Vérifier la connectivité réseau
2. Vérifier les certificats
3. Vérifier la configuration firewall
4. Contacter SWIFT support
```

#### 9.1.2 Erreur de certificat
```bash
# Symptômes
- Erreur "Certificate not trusted"
- Erreur "Invalid certificate"
- Erreur "Certificate expired"

# Solutions
1. Vérifier la validité des certificats
2. Renouveler les certificats si nécessaire
3. Vérifier l'installation dans le keystore
4. Vérifier la configuration TLS
```

#### 9.1.3 Erreur de message
```bash
# Symptômes
- Messages rejetés par SWIFT
- Erreurs de validation
- Messages non traités

# Solutions
1. Vérifier le format des messages
2. Vérifier les champs obligatoires
3. Vérifier la validation IBAN/BIC
4. Consulter les logs SWIFT
```

### 9.2 Logs à surveiller
```bash
# Logs de l'application
tail -f /app/logs/application.log | grep SWIFT

# Logs de connectivité
tail -f /app/logs/connectivity.log

# Logs de messages
tail -f /app/logs/messages.log

# Logs d'erreurs
tail -f /app/logs/error.log
```

### 9.3 Commandes de diagnostic
```bash
# Vérifier la connectivité
curl -v https://test.swift.com

# Vérifier les certificats
openssl s_client -connect test.swift.com:443 -servername test.swift.com

# Vérifier la configuration
java -jar app.jar --spring.profiles.active=prod --debug

# Vérifier les métriques
curl http://localhost:8080/actuator/metrics/swift_messages_sent_total
```

## Support et contacts

### 10.1 Contacts SWIFT
- **Support technique** : support@swift.com
- **Documentation** : https://www.swift.com/standards
- **Certificats** : certificates@swift.com

### 10.2 Contacts internes
- **Équipe technique** : tech@banking-transfer.com
- **Support utilisateur** : support@banking-transfer.com
- **Sécurité** : security@banking-transfer.com

### 10.3 Documentation supplémentaire
- [Guide SWIFTNet](https://www.swift.com/standards/swiftnet)
- [Messages ISO 20022](https://www.iso20022.org/)
- [Certificats SWIFT](https://www.swift.com/standards/certificates)
- [Monitoring SWIFT](https://www.swift.com/standards/monitoring)

---

**⚠️ IMPORTANT** : Ce guide est destiné à l'utilisation en production. Assurez-vous d'avoir les autorisations nécessaires et les accords contractuels avec SWIFT avant toute utilisation.
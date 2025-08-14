# Guide d'Onboarding SWIFT

Ce guide détaille le processus d'onboarding pour intégrer votre banque au système de transferts bancaires via SWIFT.

## Table des matières

1. [Prérequis](#prérequis)
2. [Configuration des certificats](#configuration-des-certificats)
3. [Configuration réseau](#configuration-réseau)
4. [Tests de connectivité](#tests-de-connectivité)
5. [Tests d'intégration](#tests-dintégration)
6. [Validation et certification](#validation-et-certification)
7. [Mise en production](#mise-en-production)
8. [Support et maintenance](#support-et-maintenance)

## Prérequis

### 1.1 Accords contractuels

- **Accord SWIFT** : Votre banque doit être membre SWIFT avec un BIC actif
- **Accord de service** : Contrat signé avec notre plateforme
- **Accord de conformité** : Validation KYC/AML et conformité réglementaire
- **Accord de sécurité** : Protocoles de sécurité et gestion des incidents

### 1.2 Infrastructure technique

- **BIC** : Code d'identification bancaire SWIFT actif
- **Certificats X.509** : Certificats de signature et de chiffrement
- **Connectivité réseau** : Accès à SWIFTNet avec IPs autorisées
- **Système de messagerie** : Capacité à envoyer/recevoir messages MT/MX

### 1.3 Capacités opérationnelles

- **Équipe technique** : Administrateurs système et développeurs
- **Équipe opérationnelle** : Opérateurs pour la surveillance et le support
- **Procédures** : Processus de gestion des incidents et escalade

## Configuration des certificats

### 2.1 Génération des certificats

```bash
# Générer une clé privée RSA 2048 bits
openssl genrsa -out swift_private.key 2048

# Générer un certificat de signature
openssl req -new -x509 -key swift_private.key -out swift_signing.crt -days 365

# Générer un certificat de chiffrement
openssl req -new -x509 -key swift_private.key -out swift_encryption.crt -days 365
```

### 2.2 Format des certificats

Les certificats doivent être au format PEM et inclure :

```pem
-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKoK8s7hJhQqMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
BAYTAkZSMQ8wDQYDVQQIDAZGcmFuY2UxDzANBgNVBAcMBlBhcmlzMQ4wDAYDVQQK
DAVCYW5rZTAeFw0yNDAxMDEwMDAwMDBaFw0yNTAxMDEwMDAwMDBaMEUxCzAJBgNV
BAYTAkZSMQ8wDQYDVQQIDAZGcmFuY2UxDzANBgNVBAcMBlBhcmlzMQ4wDAYDVQQK
DAVCYW5rZTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAL...
-----END CERTIFICATE-----
```

### 2.3 Installation des certificats

1. **Copier les certificats** dans le répertoire sécurisé :
```bash
mkdir -p /app/certs/swift
cp swift_signing.crt /app/certs/swift/
cp swift_encryption.crt /app/certs/swift/
cp swift_private.key /app/certs/swift/
```

2. **Configurer les permissions** :
```bash
chmod 600 /app/certs/swift/*
chown appuser:appuser /app/certs/swift/*
```

3. **Mettre à jour la configuration** :
```bash
export SWIFT_CERT_PATH=/app/certs/swift/swift_signing.crt
export SWIFT_KEY_PATH=/app/certs/swift/swift_private.key
```

## Configuration réseau

### 3.1 Configuration SWIFTNet

#### 3.1.1 Accès SWIFTNet

- **SWIFTNet Link (SNL)** : Connexion directe à SWIFTNet
- **SWIFTNet PKI** : Infrastructure à clés publiques
- **SWIFTNet RMA** : Gestion des accès et autorisations

#### 3.1.2 Configuration des IPs

```yaml
# Configuration dans docker-compose.yml
environment:
  SWIFT_ENDPOINT: https://swift.example.com
  SWIFT_BIC: YOURBIC
  SWIFT_WHITELIST_IPS:
    - "195.7.0.0/16"  # SWIFTNet IPs
    - "195.8.0.0/16"
    - "195.9.0.0/16"
```

### 3.2 Configuration TLS

#### 3.2.1 TLS Mutual Authentication

```python
# Configuration TLS dans le connecteur SWIFT
tls_config = {
    "cert_file": "/app/certs/swift/swift_signing.crt",
    "key_file": "/app/certs/swift/swift_private.key",
    "ca_file": "/app/certs/swift/swift_ca.crt",
    "verify": True,
    "version": "1.3"
}
```

#### 3.2.2 Ciphers supportés

```bash
# Ciphers recommandés pour SWIFT
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
```

## Tests de connectivité

### 4.1 Test de base

```bash
# Test de connectivité réseau
curl -v --cert /app/certs/swift/swift_signing.crt \
     --key /app/certs/swift/swift_private.key \
     https://swift.example.com/health

# Test avec OpenSSL
openssl s_client -connect swift.example.com:443 \
    -cert /app/certs/swift/swift_signing.crt \
    -key /app/certs/swift/swift_private.key \
    -CAfile /app/certs/swift/swift_ca.crt
```

### 4.2 Test de validation des certificats

```python
# Script de test des certificats
import ssl
import socket
from cryptography import x509
from cryptography.hazmat.backends import default_backend

def test_certificate(cert_path, key_path):
    """Test de validation des certificats"""
    try:
        # Charger le certificat
        with open(cert_path, 'rb') as f:
            cert_data = f.read()
        
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
        
        # Vérifier la validité
        print(f"Certificat valide jusqu'au: {cert.not_valid_after}")
        print(f"Sujet: {cert.subject}")
        print(f"Émetteur: {cert.issuer}")
        
        return True
    except Exception as e:
        print(f"Erreur de validation: {e}")
        return False
```

### 4.3 Test de connectivité SWIFT

```python
# Test de connectivité SWIFT
import requests
import ssl

def test_swift_connectivity():
    """Test de connectivité SWIFT"""
    session = requests.Session()
    
    # Configuration TLS
    session.verify = True
    session.cert = ('/app/certs/swift/swift_signing.crt', 
                   '/app/certs/swift/swift_private.key')
    
    try:
        # Test de connexion
        response = session.get('https://swift.example.com/api/v1/status')
        
        if response.status_code == 200:
            print("✅ Connectivité SWIFT OK")
            return True
        else:
            print(f"❌ Erreur de connectivité: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
```

## Tests d'intégration

### 5.1 Test de message MT

#### 5.1.1 Message MT103 (Transfert de fonds)

```xml
<!-- Exemple de message MT103 -->
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.10">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>SWIFT123456789</MsgId>
      <CreDtTm>2024-01-01T10:00:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="USD">10000.00</TtlIntrBkSttlmAmt>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <InstrId>SWIFT123456789</InstrId>
        <EndToEndId>E2E123456789</EndToEndId>
      </PmtId>
      <IntrBkSttlmAmt Ccy="USD">10000.00</IntrBkSttlmAmt>
      <ChrgBr>SHAR</ChrgBr>
      <Dbtr>
        <Nm>John Doe</Nm>
        <PstlAdr>
          <Ctry>US</Ctry>
        </PstlAdr>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>1234567890</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>YOURBIC</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtrAgt>
        <FinInstnId>
          <BICFI>DESTBIC</BICFI>
        </FinInstnId>
      </CdtrAgt>
      <Cdtr>
        <Nm>Jane Smith</Nm>
        <PstlAdr>
          <Ctry>GB</Ctry>
        </PstlAdr>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>0987654321</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <RmtInf>
        <Ustrd>Payment for services</Ustrd>
      </RmtInf>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>
```

#### 5.1.2 Script de test d'envoi

```python
# Script de test d'envoi de message SWIFT
import requests
import json
import xml.etree.ElementTree as ET

def send_test_swift_message():
    """Envoyer un message SWIFT de test"""
    
    # Message de test
    test_message = {
        "message_type": "MT103",
        "bic": "YOURBIC",
        "amount": 1000.00,
        "currency": "USD",
        "debtor_name": "Test Sender",
        "creditor_name": "Test Receiver",
        "debtor_account": "1234567890",
        "creditor_account": "0987654321",
        "purpose": "Test payment"
    }
    
    # Headers avec authentification
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_TOKEN",
        "X-SWIFT-BIC": "YOURBIC"
    }
    
    try:
        # Envoi du message
        response = requests.post(
            "https://api.banking-platform.com/swift/send",
            json=test_message,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Message envoyé avec succès")
            print(f"Message ID: {result.get('message_id')}")
            print(f"Status: {result.get('status')}")
            return True
        else:
            print(f"❌ Erreur d'envoi: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False
```

### 5.2 Test de réception

#### 5.2.1 Webhook de réception

```python
# Endpoint de réception des messages SWIFT
from fastapi import APIRouter, Request, HTTPException
from app.swift.models import SwiftMessage

router = APIRouter()

@router.post("/swift/webhook")
async def swift_webhook(request: Request):
    """Webhook pour recevoir les messages SWIFT"""
    
    try:
        # Vérifier l'authentification
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        # Récupérer le message
        message_data = await request.json()
        
        # Valider le message
        swift_message = SwiftMessage(**message_data)
        
        # Traiter le message
        await process_swift_message(swift_message)
        
        return {"status": "received", "message_id": swift_message.message_id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 5.2.2 Test de réception

```python
# Test de réception de message
def test_swift_reception():
    """Test de réception de message SWIFT"""
    
    # Simuler un message reçu
    test_received_message = {
        "message_id": "SWIFT987654321",
        "message_type": "MT910",
        "bic": "YOURBIC",
        "amount": 1000.00,
        "currency": "USD",
        "status": "CONFIRMED"
    }
    
    # Envoyer au webhook
    response = requests.post(
        "http://localhost:8000/swift/webhook",
        json=test_received_message,
        headers={"Authorization": "Bearer test_token"}
    )
    
    if response.status_code == 200:
        print("✅ Réception de message OK")
        return True
    else:
        print(f"❌ Erreur de réception: {response.status_code}")
        return False
```

## Validation et certification

### 6.1 Tests de conformité

#### 6.1.1 Validation des messages

```python
# Validation des messages SWIFT
from app.swift.validators import SwiftMessageValidator

def validate_swift_message(message_xml):
    """Valider un message SWIFT"""
    
    validator = SwiftMessageValidator()
    
    # Validation XML
    if not validator.validate_xml(message_xml):
        print("❌ Message XML invalide")
        return False
    
    # Validation des champs obligatoires
    if not validator.validate_required_fields(message_xml):
        print("❌ Champs obligatoires manquants")
        return False
    
    # Validation des montants
    if not validator.validate_amounts(message_xml):
        print("❌ Montants invalides")
        return False
    
    print("✅ Message SWIFT valide")
    return True
```

#### 6.1.2 Tests de performance

```python
# Tests de performance SWIFT
import time
import asyncio

async def performance_test():
    """Test de performance SWIFT"""
    
    start_time = time.time()
    success_count = 0
    total_messages = 100
    
    for i in range(total_messages):
        try:
            # Envoyer un message
            success = await send_swift_message(f"TEST{i}")
            if success:
                success_count += 1
        except Exception as e:
            print(f"Erreur message {i}: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Performance test results:")
    print(f"Messages envoyés: {success_count}/{total_messages}")
    print(f"Temps total: {duration:.2f} secondes")
    print(f"Messages/seconde: {success_count/duration:.2f}")
    
    return success_count == total_messages
```

### 6.2 Certification SWIFT

#### 6.2.1 Checklist de certification

- [ ] **Connectivité réseau** : Tests de connectivité réussis
- [ ] **Certificats** : Certificats X.509 valides et installés
- [ ] **Messages** : Validation des messages MT/MX
- [ ] **Performance** : Tests de performance satisfaisants
- [ ] **Sécurité** : Audit de sécurité passé
- [ ] **Conformité** : Validation réglementaire
- [ ] **Documentation** : Documentation technique complète
- [ ] **Support** : Équipe de support formée

#### 6.2.2 Rapport de certification

```markdown
# Rapport de Certification SWIFT

## Informations générales
- **Banque** : [Nom de la banque]
- **BIC** : [BIC de la banque]
- **Date de certification** : [Date]
- **Version de la plateforme** : [Version]

## Résultats des tests

### Connectivité
- ✅ Test de connectivité réseau : PASSED
- ✅ Test de certificats TLS : PASSED
- ✅ Test d'authentification : PASSED

### Messages
- ✅ Validation MT103 : PASSED
- ✅ Validation MT910 : PASSED
- ✅ Validation MX pacs.008 : PASSED

### Performance
- ✅ Tests de charge : PASSED
- ✅ Tests de latence : PASSED
- ✅ Tests de disponibilité : PASSED

### Sécurité
- ✅ Audit de sécurité : PASSED
- ✅ Tests de pénétration : PASSED
- ✅ Validation des certificats : PASSED

## Recommandations
1. Surveillance continue des performances
2. Mise à jour régulière des certificats
3. Tests de régression mensuels
4. Formation continue de l'équipe

## Signature
- **Certifié par** : [Nom du certificateur]
- **Date** : [Date]
- **Signature** : [Signature]
```

## Mise en production

### 7.1 Plan de déploiement

#### 7.1.1 Phase de préparation

1. **Configuration finale**
   - Certificats de production installés
   - Configuration réseau validée
   - Tests de connectivité réussis

2. **Formation de l'équipe**
   - Formation technique complète
   - Procédures opérationnelles
   - Gestion des incidents

3. **Documentation**
   - Procédures opérationnelles
   - Guide de dépannage
   - Contacts d'escalade

#### 7.1.2 Phase de déploiement

1. **Déploiement en production**
   ```bash
   # Déploiement avec docker-compose
   docker-compose -f docker-compose.prod.yml up -d
   
   # Vérification de la santé
   curl -f http://localhost:8000/health
   ```

2. **Tests de validation**
   - Tests de connectivité SWIFT
   - Tests d'envoi de messages
   - Tests de réception de messages

3. **Activation progressive**
   - Activation pour un sous-ensemble d'utilisateurs
   - Surveillance renforcée
   - Extension progressive

### 7.2 Configuration de production

#### 7.2.1 Variables d'environnement

```bash
# Configuration de production
export ENVIRONMENT=production
export SWIFT_DRY_RUN=false
export SWIFT_ENDPOINT=https://swift.production.com
export SWIFT_BIC=YOURBIC
export SWIFT_CERT_PATH=/app/certs/swift/prod_signing.crt
export SWIFT_KEY_PATH=/app/certs/swift/prod_private.key

# Sécurité renforcée
export LOG_LEVEL=WARNING
export DEBUG=false
export SECRET_KEY=your-super-secure-production-key
export ENCRYPTION_KEY=your-32-char-encryption-key
```

#### 7.2.2 Monitoring de production

```yaml
# Configuration Prometheus pour SWIFT
scrape_configs:
  - job_name: 'swift-metrics'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```

### 7.3 Procédures opérationnelles

#### 7.3.1 Surveillance quotidienne

```bash
#!/bin/bash
# Script de surveillance SWIFT

echo "=== Surveillance SWIFT $(date) ==="

# Vérifier la connectivité
if curl -f https://swift.production.com/health; then
    echo "✅ Connectivité SWIFT OK"
else
    echo "❌ Problème de connectivité SWIFT"
    # Envoyer alerte
fi

# Vérifier les certificats
if openssl x509 -checkend 86400 -noout -in /app/certs/swift/prod_signing.crt; then
    echo "✅ Certificats valides"
else
    echo "⚠️  Certificats expirant bientôt"
fi

# Vérifier les métriques
curl -s http://localhost:8000/metrics | grep swift_messages_total
```

#### 7.3.2 Gestion des incidents

```python
# Procédure de gestion d'incident SWIFT
class SwiftIncidentManager:
    
    def __init__(self):
        self.incident_levels = {
            "critical": ["connectivity_loss", "certificate_expired"],
            "high": ["message_failure", "performance_degradation"],
            "medium": ["delayed_messages", "partial_failure"],
            "low": ["minor_issues", "warnings"]
        }
    
    def handle_incident(self, incident_type, details):
        """Gérer un incident SWIFT"""
        
        # Déterminer le niveau
        level = self.get_incident_level(incident_type)
        
        # Actions selon le niveau
        if level == "critical":
            self.handle_critical_incident(incident_type, details)
        elif level == "high":
            self.handle_high_incident(incident_type, details)
        # ...
    
    def handle_critical_incident(self, incident_type, details):
        """Gérer un incident critique"""
        # 1. Notifier l'équipe
        self.notify_team(incident_type, details, urgency="immediate")
        
        # 2. Activer le mode dégradé
        self.activate_degraded_mode()
        
        # 3. Escalader
        self.escalate_incident(incident_type, details)
```

## Support et maintenance

### 8.1 Support technique

#### 8.1.1 Contacts de support

- **Support technique** : tech-support@banking-platform.com
- **Support SWIFT** : swift-support@banking-platform.com
- **Urgences** : +1-555-0123 (24/7)

#### 8.1.2 Niveaux de support

| Niveau | Temps de réponse | Description |
|--------|------------------|-------------|
| P0 | 15 minutes | Incident critique (connectivité perdue) |
| P1 | 1 heure | Incident majeur (dégradation importante) |
| P2 | 4 heures | Incident mineur (fonctionnalité limitée) |
| P3 | 24 heures | Demande d'amélioration |

### 8.2 Maintenance

#### 8.2.1 Maintenance préventive

```bash
#!/bin/bash
# Script de maintenance SWIFT

echo "=== Maintenance SWIFT $(date) ==="

# Sauvegarde des certificats
cp -r /app/certs/swift /backup/certs/swift_$(date +%Y%m%d)

# Vérification des logs
tail -1000 /var/log/swift.log | grep -i error

# Nettoyage des anciens messages
find /app/swift/messages -name "*.xml" -mtime +30 -delete

# Vérification de l'espace disque
df -h /app

echo "Maintenance terminée"
```

#### 8.2.2 Mise à jour des certificats

```bash
#!/bin/bash
# Script de renouvellement des certificats

echo "Renouvellement des certificats SWIFT..."

# Générer nouveaux certificats
openssl genrsa -out swift_new.key 2048
openssl req -new -x509 -key swift_new.key -out swift_new.crt -days 365

# Tester les nouveaux certificats
if test_certificates swift_new.crt swift_new.key; then
    # Sauvegarder les anciens
    mv /app/certs/swift/swift_signing.crt /app/certs/swift/swift_signing.crt.backup
    
    # Installer les nouveaux
    cp swift_new.crt /app/certs/swift/swift_signing.crt
    cp swift_new.key /app/certs/swift/swift_private.key
    
    # Redémarrer le service
    docker-compose restart backend
    
    echo "Certificats renouvelés avec succès"
else
    echo "Erreur lors du test des nouveaux certificats"
    exit 1
fi
```

### 8.3 Documentation continue

#### 8.3.1 Journal des modifications

```markdown
# Journal des modifications SWIFT

## 2024-01-15
- Mise à jour des certificats SWIFT
- Amélioration de la validation des messages
- Correction du bug de connectivité TLS

## 2024-01-10
- Ajout du support MX pacs.008
- Optimisation des performances
- Mise à jour de la documentation

## 2024-01-05
- Correction du problème de timeouts
- Amélioration du monitoring
- Ajout de nouveaux tests
```

#### 8.3.2 Procédures de dépannage

```markdown
# Guide de dépannage SWIFT

## Problème : Perte de connectivité

### Symptômes
- Erreur "Connection refused"
- Timeout sur les requêtes SWIFT
- Messages non envoyés

### Diagnostic
1. Vérifier la connectivité réseau
2. Tester les certificats
3. Vérifier les logs

### Solution
1. Redémarrer le service SWIFT
2. Vérifier la configuration réseau
3. Contacter le support si nécessaire

## Problème : Certificats expirés

### Symptômes
- Erreur "Certificate expired"
- Échec d'authentification TLS

### Solution
1. Générer de nouveaux certificats
2. Installer les certificats
3. Redémarrer le service
```

---

## Conclusion

Ce guide d'onboarding SWIFT fournit toutes les informations nécessaires pour intégrer votre banque à notre plateforme de transferts bancaires. Suivez attentivement chaque étape et n'hésitez pas à contacter notre équipe de support pour toute question.

**⚠️ Important** : Ce guide est destiné à un usage en environnement de test. Pour la production, contactez notre équipe pour une assistance personnalisée et des configurations spécifiques à votre infrastructure.
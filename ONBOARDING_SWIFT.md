# Guide d'Onboarding SWIFT - SwiftPay

## 🎯 Objectif

Ce document détaille le processus complet pour activer les transferts bancaires réels via le réseau SWIFT. **ATTENTION**: Ce processus implique des fonds réels et nécessite une coordination étroite avec votre institution financière.

## ⚠️ Avertissements Critiques

1. **NE JAMAIS** exécuter de transferts réels sans autorisation écrite de la banque
2. **TOUJOURS** commencer par l'environnement de test/sandbox
3. **VÉRIFIER** tous les certificats et credentials avant utilisation
4. **SAUVEGARDER** tous les certificats et clés de manière sécurisée
5. **RESPECTER** les horaires d'opération SWIFT (généralement 7j/7, 24h/24 sauf maintenance)

## 📋 Prérequis Bancaires

### 1. Éléments à Obtenir de Votre Banque/Partenaire SWIFT

#### 1.1 Informations de Base
- [ ] **BIC/SWIFT Code** de votre institution (format: AAAABBCCXXX)
- [ ] **Numéro de participant SWIFT** 
- [ ] **Coordonnées du responsable technique SWIFT** (nom, email, téléphone)
- [ ] **Coordonnées du responsable compliance** (pour KYC/AML)

#### 1.2 Endpoints et Connectivité
- [ ] **URL de l'endpoint SWIFT** (test et production)
  - Format: `https://swift-api.yourbank.com` ou `https://10.x.x.x:8443`
- [ ] **Protocole de communication** :
  - [ ] AS4 (recommandé pour ISO 20022)
  - [ ] SFTP (pour messages MT)
  - [ ] REST API (si disponible)
  - [ ] MQ Series (legacy)
- [ ] **Ports réseau** utilisés (généralement 443 pour HTTPS, 22 pour SFTP)
- [ ] **Plages d'adresses IP** autorisées (whitelist)
- [ ] **Horaires de service** et fenêtres de maintenance

#### 1.3 Certificats X.509 et Sécurité
- [ ] **Certificat client** (.p12 ou .pem) pour authentification mutuelle
- [ ] **Mot de passe du certificat client**
- [ ] **Certificat de l'autorité de certification (CA)** de la banque
- [ ] **Chaîne de certificats complète** (root CA + intermediate CAs)
- [ ] **Certificat de signature** (si différent du certificat d'authentification)
- [ ] **Politique de rotation des certificats** (fréquence, procédure)

#### 1.4 Credentials et Identifiants
- [ ] **Identifiant d'entreprise** (Enterprise ID)
- [ ] **Clé API** (si protocole REST)
- [ ] **Nom d'utilisateur SFTP** (si protocole SFTP)
- [ ] **Mot de passe SFTP** (si protocole SFTP)
- [ ] **Identifiants de test** (environnement sandbox)

#### 1.5 Configuration Technique
- [ ] **Format de message supporté** :
  - [ ] ISO 20022 (pacs.008, pacs.002, camt.053, etc.)
  - [ ] MT (MT103, MT202, etc.)
- [ ] **Version du schéma ISO 20022** (ex: pacs.008.001.08)
- [ ] **Encoding** (UTF-8, ISO-8859-1)
- [ ] **Compression** supportée (gzip, deflate)
- [ ] **Taille maximale des messages**
- [ ] **Timeout des requêtes** (recommandé: 30-60 secondes)

#### 1.6 Tests et Validation
- [ ] **Suite de tests SWIFT gpi** (si applicable)
- [ ] **Messages de test ISO 20022** fournis par la banque
- [ ] **Scénarios de test obligatoires** :
  - [ ] Transfert standard réussi
  - [ ] Transfert avec erreur de format
  - [ ] Transfert avec bénéficiaire inexistant
  - [ ] Test de timeout
  - [ ] Test de reconnexion
- [ ] **Critères d'acceptation** pour passer en production

### 2. Obligations Contractuelles et Compliance

#### 2.1 Contrats et Accords
- [ ] **Contrat de service SWIFT** signé
- [ ] **Accord de niveau de service (SLA)** défini
- [ ] **Accord de confidentialité (NDA)** signé
- [ ] **Assurance responsabilité civile** adaptée

#### 2.2 Compliance KYC/AML
- [ ] **Procédures KYC** validées par la banque
- [ ] **Règles AML** configurées selon la juridiction
- [ ] **Liste de sanctions** à utiliser (OFAC, EU, UN, etc.)
- [ ] **Seuils de déclaration** (SAR/STR) par pays
- [ ] **Conservation des logs** (durée, format, accès)

#### 2.3 Audit et Monitoring
- [ ] **Accès audit** pour la banque (lecture seule)
- [ ] **Rapports de transaction** (fréquence, format)
- [ ] **Procédures d'incident** et escalation
- [ ] **Tests de continuité** (disaster recovery)

## 🔧 Configuration Technique

### 3. Installation des Certificats

#### 3.1 Préparation de l'Environnement
```bash
# Créer les répertoires pour les certificats
sudo mkdir -p /etc/ssl/swiftpay/{client,ca,backup}
sudo chown -R swiftpay:swiftpay /etc/ssl/swiftpay
sudo chmod 700 /etc/ssl/swiftpay

# Créer le répertoire de sauvegarde
sudo mkdir -p /var/backups/swiftpay/certificates
```

#### 3.2 Installation du Certificat Client
```bash
# Copier le certificat client (fourni par la banque)
sudo cp swift-client-cert.p12 /etc/ssl/swiftpay/client/
sudo chmod 600 /etc/ssl/swiftpay/client/swift-client-cert.p12

# Vérifier le certificat
openssl pkcs12 -in /etc/ssl/swiftpay/client/swift-client-cert.p12 -info -noout

# Extraire le certificat public (pour vérification)
openssl pkcs12 -in /etc/ssl/swiftpay/client/swift-client-cert.p12 \
    -clcerts -nokeys -out /etc/ssl/swiftpay/client/client-cert.pem

# Vérifier les dates d'expiration
openssl x509 -in /etc/ssl/swiftpay/client/client-cert.pem -dates -noout
```

#### 3.3 Installation du Certificat CA
```bash
# Copier le certificat CA (fourni par la banque)
sudo cp swift-ca-cert.pem /etc/ssl/swiftpay/ca/
sudo chmod 644 /etc/ssl/swiftpay/ca/swift-ca-cert.pem

# Vérifier le certificat CA
openssl x509 -in /etc/ssl/swiftpay/ca/swift-ca-cert.pem -text -noout

# Ajouter au trust store du système (optionnel)
sudo cp /etc/ssl/swiftpay/ca/swift-ca-cert.pem /usr/local/share/ca-certificates/swift-ca.crt
sudo update-ca-certificates
```

### 4. Configuration de l'Application

#### 4.1 Variables d'Environnement Production
```bash
# Créer le fichier de configuration production
cat > /etc/swiftpay/production.env << EOF
# SWIFT Configuration
SWIFT_ENABLED=true
SWIFT_BIC=VOTRE_BIC_ICI
SWIFT_ENDPOINT_URL=https://swift-api.yourbank.com
SWIFT_CLIENT_CERT_PATH=/etc/ssl/swiftpay/client/swift-client-cert.p12
SWIFT_CLIENT_CERT_PASSWORD=VOTRE_MOT_DE_PASSE_CERT
SWIFT_CA_CERT_PATH=/etc/ssl/swiftpay/ca/swift-ca-cert.pem
SWIFT_MUTUAL_TLS_ENABLED=true

# Sécurité
JWT_SECRET=$(openssl rand -base64 32)
SESSION_SECRET=$(openssl rand -base64 32)
CSRF_SECRET=$(openssl rand -base64 32)

# Base de données (production)
DB_HOST=prod-postgres.yourcompany.com
DB_NAME=swiftpay_prod
DB_USERNAME=swiftpay_prod
DB_PASSWORD=VOTRE_MOT_DE_PASSE_DB

# Vault (production)
VAULT_HOST=vault.yourcompany.com
VAULT_SCHEME=https
VAULT_TOKEN=VOTRE_TOKEN_VAULT_PROD
EOF

# Sécuriser le fichier
sudo chown root:swiftpay /etc/swiftpay/production.env
sudo chmod 640 /etc/swiftpay/production.env
```

#### 4.2 Configuration HashiCorp Vault
```bash
# Stocker les secrets dans Vault
vault kv put secret/swiftpay/swift \
    client_cert_password="VOTRE_MOT_DE_PASSE_CERT" \
    api_key="VOTRE_CLE_API"

vault kv put secret/swiftpay/database \
    password="VOTRE_MOT_DE_PASSE_DB"

vault kv put secret/swiftpay/encryption \
    master_key="$(openssl rand -base64 32)"
```

### 5. Tests de Connectivité

#### 5.1 Test TLS Mutuel avec OpenSSL
```bash
# Test de connexion TLS avec certificat client
openssl s_client -connect swift-api.yourbank.com:443 \
    -cert /etc/ssl/swiftpay/client/client-cert.pem \
    -key /etc/ssl/swiftpay/client/client-key.pem \
    -CAfile /etc/ssl/swiftpay/ca/swift-ca-cert.pem \
    -verify_return_error \
    -servername swift-api.yourbank.com

# Vérifier la chaîne de certificats
openssl s_client -connect swift-api.yourbank.com:443 \
    -showcerts -verify 5 \
    -CAfile /etc/ssl/swiftpay/ca/swift-ca-cert.pem
```

#### 5.2 Test avec cURL
```bash
# Test HTTP avec certificat client
curl -v \
    --cert /etc/ssl/swiftpay/client/client-cert.pem \
    --key /etc/ssl/swiftpay/client/client-key.pem \
    --cacert /etc/ssl/swiftpay/ca/swift-ca-cert.pem \
    https://swift-api.yourbank.com/health

# Test avec certificat PKCS12
curl -v \
    --cert-type P12 \
    --cert /etc/ssl/swiftpay/client/swift-client-cert.p12:VOTRE_MOT_DE_PASSE \
    --cacert /etc/ssl/swiftpay/ca/swift-ca-cert.pem \
    https://swift-api.yourbank.com/health
```

#### 5.3 Test de Connectivité SwiftPay
```bash
# Utiliser le script de test intégré
./scripts/swift-test.sh --dry-run --endpoint https://swift-api.yourbank.com

# Test avec l'API SwiftPay
curl -X POST http://localhost:8080/api/admin/swift/test-connectivity \
    -H "Authorization: Bearer VOTRE_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "testTransfer": {
            "amount": 100.00,
            "currency": "USD",
            "recipientBic": "TESTBICXXX",
            "recipientName": "Test Recipient"
        }
    }'
```

## 🧪 Plan de Tests d'Intégration

### 6. Scénarios de Test Obligatoires

#### 6.1 Phase 1: Tests de Connectivité
1. **Test de handshake TLS**
   - Vérification des certificats
   - Validation de la chaîne de confiance
   - Test de révocation des certificats

2. **Test d'authentification**
   - Authentification mutuelle réussie
   - Rejet avec certificat invalide
   - Rejet avec certificat expiré

3. **Test de format de message**
   - Génération de message ISO 20022 valide
   - Validation du schéma XML
   - Test de signature électronique

#### 6.2 Phase 2: Tests Fonctionnels (Sandbox)
1. **Transfert standard réussi**
```json
{
  "amount": 100.00,
  "currency": "USD",
  "recipientName": "Test Beneficiary",
  "recipientIban": "DE89370400440532013000",
  "recipientBic": "COBADEFFXXX",
  "remittanceInfo": "Test payment - DO NOT PROCESS"
}
```

2. **Transfert avec erreur de format**
```json
{
  "amount": 100.00,
  "currency": "USD",
  "recipientName": "",
  "recipientIban": "INVALID_IBAN",
  "recipientBic": "INVALID_BIC"
}
```

3. **Test de timeout**
   - Simuler une connexion lente
   - Vérifier la gestion des timeouts
   - Test de reconnexion automatique

4. **Test de volume**
   - Envoi de 100 transferts simultanés
   - Vérification des limites de débit
   - Test de la file d'attente

#### 6.3 Phase 3: Tests de Production (Montants Minimaux)
1. **Premier transfert réel** (1 EUR/USD vers compte de test)
2. **Vérification du cycle complet** (envoi → accusé → statut final)
3. **Test de réconciliation** avec les rapports bancaires

### 7. Validation des Messages ISO 20022

#### 7.1 Messages Obligatoires à Tester

1. **pacs.008 (Credit Transfer)**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>SWIFTPAY-TEST-001</MsgId>
      <CreDtTm>2024-01-15T10:30:00Z</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <TtlIntrBkSttlmAmt Ccy="USD">100.00</TtlIntrBkSttlmAmt>
      <!-- ... reste du message ... -->
    </GrpHdr>
    <!-- ... -->
  </FIToFICstmrCdtTrf>
</Document>
```

2. **pacs.002 (Payment Status Report)** - Réception
3. **camt.053 (Bank to Customer Statement)** - Réconciliation

#### 7.2 Validation Automatique
```bash
# Utiliser l'outil de validation SwiftPay
./scripts/validate-iso20022.sh \
    --message-file test-pacs008.xml \
    --schema-version pacs.008.001.08 \
    --validate-signature
```

## 🔐 Sécurité et Gestion des Clés

### 8. Procédures de Sécurité

#### 8.1 Gestion des Certificats
```bash
# Script de rotation des certificats
#!/bin/bash
# rotate-certificates.sh

CERT_DIR="/etc/ssl/swiftpay"
BACKUP_DIR="/var/backups/swiftpay/certificates/$(date +%Y%m%d)"

# Créer la sauvegarde
mkdir -p "$BACKUP_DIR"
cp -r "$CERT_DIR"/* "$BACKUP_DIR/"

# Installer les nouveaux certificats
cp new-swift-client-cert.p12 "$CERT_DIR/client/"
cp new-swift-ca-cert.pem "$CERT_DIR/ca/"

# Redémarrer les services
systemctl restart swiftpay-backend

# Vérifier la connectivité
./scripts/swift-test.sh --verify-certificates
```

#### 8.2 Backup et Restauration
```bash
# Sauvegarde automatique quotidienne
#!/bin/bash
# backup-swift-config.sh

DATE=$(date +%Y%m%d)
BACKUP_PATH="/var/backups/swiftpay/$DATE"

mkdir -p "$BACKUP_PATH"

# Sauvegarder les certificats
tar -czf "$BACKUP_PATH/certificates.tar.gz" /etc/ssl/swiftpay/

# Sauvegarder la configuration
cp /etc/swiftpay/production.env "$BACKUP_PATH/"

# Chiffrer la sauvegarde
gpg --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 \
    --s2k-digest-algo SHA512 --s2k-count 65536 \
    --symmetric --output "$BACKUP_PATH/swift-backup-$DATE.gpg" \
    "$BACKUP_PATH/certificates.tar.gz"

# Nettoyer les fichiers temporaires
rm "$BACKUP_PATH/certificates.tar.gz"
```

### 9. Monitoring et Alertes

#### 9.1 Métriques Critiques à Surveiller
- **Taux de succès des transferts SWIFT** (>99.5%)
- **Temps de réponse moyen** (<30 secondes)
- **Disponibilité de l'endpoint SWIFT** (>99.9%)
- **Expiration des certificats** (alerte 30 jours avant)
- **Erreurs de validation ISO 20022** (<0.1%)

#### 9.2 Configuration des Alertes
```yaml
# Exemple de règle Prometheus
groups:
  - name: swift.rules
    rules:
      - alert: SwiftTransferFailureRate
        expr: rate(swift_transfer_failures_total[5m]) > 0.01
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'échec SWIFT élevé"
          description: "{{ $value }} transferts SWIFT échouent par seconde"

      - alert: SwiftCertificateExpiring
        expr: (swift_certificate_expiry_timestamp - time()) / 86400 < 30
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Certificat SWIFT expire bientôt"
          description: "Le certificat SWIFT expire dans {{ $value }} jours"
```

## 🚀 Mise en Production

### 10. Checklist de Déploiement

#### 10.1 Avant le Déploiement
- [ ] Tests d'intégration réussis en sandbox
- [ ] Validation par l'équipe compliance de la banque
- [ ] Certificats de production installés et testés
- [ ] Monitoring et alertes configurés
- [ ] Plan de rollback préparé
- [ ] Équipe d'astreinte informée

#### 10.2 Déploiement Progressif
1. **Phase 1**: Activation en lecture seule (monitoring uniquement)
2. **Phase 2**: Transferts de test avec montants minimaux (1-10 EUR/USD)
3. **Phase 3**: Montants limités (max 1000 EUR/USD)
4. **Phase 4**: Production complète

#### 10.3 Validation Post-Déploiement
```bash
# Script de validation post-déploiement
#!/bin/bash
# validate-production.sh

echo "🔍 Validation de la production SwiftPay..."

# 1. Vérifier la connectivité
echo "1. Test de connectivité SWIFT..."
curl -f http://localhost:8081/actuator/health/swift || exit 1

# 2. Vérifier les certificats
echo "2. Vérification des certificats..."
./scripts/certificate-check.sh || exit 1

# 3. Test de transfert minimal
echo "3. Test de transfert minimal..."
./scripts/test-minimal-transfer.sh || exit 1

# 4. Vérifier les métriques
echo "4. Vérification des métriques..."
curl -f http://localhost:9090/api/v1/query?query=swift_connector_status || exit 1

echo "✅ Validation production réussie!"
```

## 📞 Support et Escalation

### 11. Contacts d'Urgence

#### 11.1 Équipe SwiftPay
- **Support technique**: support@swiftpay.com
- **Escalation sécurité**: security@swiftpay.com
- **Astreinte 24/7**: +33 1 XX XX XX XX

#### 11.2 Partenaires Bancaires
- **Support SWIFT de la banque**: [À compléter]
- **Responsable technique**: [À compléter]
- **Astreinte bancaire**: [À compléter]

### 12. Procédures d'Incident

#### 12.1 Incident Critique (Transferts Bloqués)
1. **Immédiat** (0-5 min):
   - Vérifier le statut des services
   - Consulter les logs d'erreur
   - Alerter l'équipe d'astreinte

2. **Court terme** (5-30 min):
   - Diagnostiquer la cause racine
   - Contacter le support bancaire si nécessaire
   - Implémenter un contournement si possible

3. **Résolution** (30 min - 4h):
   - Corriger le problème
   - Tester la résolution
   - Reprendre les transferts en attente

#### 12.2 Incident de Sécurité
1. **Isoler** immédiatement le système
2. **Alerter** l'équipe sécurité et la banque
3. **Analyser** les logs d'audit
4. **Documenter** l'incident pour compliance

## 📊 Rapports et Compliance

### 13. Rapports Obligatoires

#### 13.1 Rapports Quotidiens
- Nombre de transferts traités
- Volume total par devise
- Taux de succès/échec
- Temps de traitement moyen

#### 13.2 Rapports Mensuels
- Analyse des tendances
- Rapport de compliance KYC/AML
- Incidents de sécurité
- Performance des SLA

#### 13.3 Rapports Annuels
- Audit de sécurité complet
- Révision des procédures
- Plan de continuité d'activité
- Formation du personnel

## ✅ Checklist d'Acceptation

### 14. Critères de Validation Finale

#### 14.1 Tests Techniques
- [ ] Connectivité SWIFT stable (>99.9% uptime sur 7 jours)
- [ ] Messages ISO 20022 validés par la banque
- [ ] Certificats installés et testés
- [ ] Monitoring opérationnel
- [ ] Logs d'audit complets

#### 14.2 Tests Fonctionnels
- [ ] Transfert test réussi avec accusé de réception
- [ ] Gestion des erreurs validée
- [ ] Interface utilisateur fonctionnelle
- [ ] Notifications temps réel opérationnelles

#### 14.3 Compliance et Sécurité
- [ ] Procédures KYC/AML validées
- [ ] Tests de pénétration réalisés
- [ ] Audit de sécurité approuvé
- [ ] Formation équipe complétée

#### 14.4 Documentation
- [ ] Runbook opérationnel complet
- [ ] Procédures d'incident documentées
- [ ] Guide utilisateur finalisé
- [ ] Documentation technique à jour

---

## 🆘 En Cas de Problème

### Problèmes Courants et Solutions

1. **Erreur de certificat**
   - Vérifier les dates d'expiration
   - Contrôler les permissions de fichiers
   - Valider la chaîne de certificats

2. **Timeout de connexion**
   - Vérifier la connectivité réseau
   - Contrôler les firewalls
   - Augmenter les timeouts si nécessaire

3. **Message ISO 20022 invalide**
   - Utiliser l'outil de validation
   - Vérifier le schéma XSD
   - Contrôler l'encoding (UTF-8)

4. **Erreur d'authentification**
   - Vérifier les credentials
   - Contrôler la configuration Keycloak
   - Valider les rôles utilisateur

### Logs à Consulter
- `/app/logs/swiftpay.log` - Logs applicatifs
- `/var/log/nginx/access.log` - Logs d'accès web
- `docker logs swiftpay-backend` - Logs conteneur
- Vault audit logs - Accès aux secrets

---

**⚠️ RAPPEL IMPORTANT**: Ce système gère des fonds réels. Toute modification en production doit être validée par l'équipe de sécurité et approuvée par la banque partenaire.
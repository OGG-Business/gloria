# SWIFT Connectivity & Onboarding Guide

This document describes the steps to onboard with a partner bank for SWIFT payments and how to configure connectivity.

## Endpoints & Protocols
- Production SWIFT connectivity varies by bank: REST over mTLS, SFTP file drops, or AS4
- BIC: Provided by bank
- IP Whitelist: Provide egress static IPs for allowlisting
- SLA: Agree per corridor and currency

## Certificates
- Generate client keypair (RSA 2048+ or EC) and CSR
- Bank CA issues client cert; obtain bank CA chain
- Store client key/cert in Vault or Google Secret Manager; never commit secrets

## mTLS Procedure (REST)
1. Prepare PEM files: client.crt, client.key, bank_ca.crt
2. Configure environment:
   - SWIFT_MODE=rest
   - SWIFT_REST_BASE_URL=https://bank.example.com/swift
   - SWIFT_REST_MTLS=true
   - SWIFT_CLIENT_CERT_PATH=/secrets/client.crt
   - SWIFT_CLIENT_KEY_PATH=/secrets/client.key
   - SWIFT_CA_CERT_PATH=/secrets/bank_ca.crt
3. Deploy with volumes mounted at /secrets (Kubernetes Secret or Secret Manager CSI)
4. Test using curl:
```bash
curl --cert /secrets/client.crt --key /secrets/client.key --cacert /secrets/bank_ca.crt \
  -H 'Content-Type: application/xml' \
  --data-binary @sample_pacs008.xml \
  https://bank.example.com/swift/payments
```

## SFTP / AS4
- For SFTP: exchange SSH keys; push files in agreed folder; poll ACK folder
- For AS4: coordinate endpoint URL, certificates, compression, signing and encryption

## ISO 20022 Messages
- Outbound: pacs.008.001.xx (customer credit transfer FI-to-FI)
- Inbound: pain.002 / camt.054 for status/settlement (bank-dependent)

## Dry-run Mode
- Keep DRY_RUN=true until bank confirms test window and credentials
- In dry-run, messages are built but not transmitted

## Compliance & Contracts
- Ensure KYC/AML obligations are implemented: logs, audit trails, sanctions screening, retention
- Keep written approval from the bank before any production traffic

## Sample Connectivity Tests
```bash
# TLS handshake check
openssl s_client -connect bank.example.com:443 -servername bank.example.com -cert client.crt -key client.key -CAfile bank_ca.crt </dev/null | head -n 20

# REST ping
curl --cert client.crt --key client.key --cacert bank_ca.crt https://bank.example.com/ping
```
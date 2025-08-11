# SWIFT Connectivity Onboarding

This document outlines the steps to integrate with your bank over SWIFT or bank-provided channels (AS4/SFTP/REST). No production traffic is sent without bank-provided credentials, certificates, and written approval.

## Integration Parameters
- Endpoints: As provided by bank (AS4 endpoint URL, SFTP hostname, REST base URL)
- Protocols: AS4 over TLS 1.2/1.3, SFTP (SSH), REST over TLS 1.2/1.3
- Certificates: X.509 client certificate for mutual TLS, server CA chain
- BIC: Your institution and counterparty BICs
- SLA: Bank-specific window and acknowledgements (ACK/NAK)
- IP Whitelist: Provide egress IPs from GCP (Cloud NAT) for allow-listing

## Mutual TLS Procedure (REST/AS4)
1. Generate a private key and CSR:
```bash
openssl req -newkey rsa:4096 -keyout client.key -out client.csr -subj "/CN=your-cn/O=your-org/C=CD" -nodes
```
2. Provide CSR to bank; receive signed client certificate and server CA bundle.
3. Configure backend connector with:
   - client cert: `client.crt`
   - client key: `client.key`
   - server CA: `ca-bundle.crt`
4. Test connectivity:
```bash
curl https://bank.example.com/endpoint \
  --cert client.crt --key client.key \
  --cacert ca-bundle.crt -v
```

## ISO 20022 Test Plan (pacs.008)
- Validate pacs.008 schema against XSD
- Send test messages in dry-run mode
- Verify ACK/NAK receipt and map to transfer events

## Compliance & Contracts
- Ensure KYC/AML obligations met; enable audit and log retention
- Document all credentials in Vault/GSM with restricted access and rotation schedule

## Scripts
- See `scripts/connectivity/` for `openssl` and `curl` examples
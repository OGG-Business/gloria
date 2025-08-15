# SWIFT/BANK CONNECTIVITY ONBOARDING GUIDE

This guide details the exact artifacts to request from your bank/SWIFT partner or Service Bureau and the steps to activate real transfers in production.

## Primary Integration Method: AZQORE Service Bureau

The platform is now primarily configured to work via a Service Bureau, specifically AZQORE. This method uses a REST API with JWT authentication instead of direct mTLS connection to SWIFT.

### Required Configuration for AZQORE
To enable the AZQORE integration, you must first configure a "Client" within your Keycloak realm that is authorized to request tokens. This client should use the "Client Credentials" flow.

Once the client is created in Keycloak, you must configure the following environment variables for this application:
- `CONNECTOR_AZQORE_API_URL`: The base URL for the AZQORE API (e.g., `https://api.azqore.com`).
- `CONNECTOR_AZQORE_BIC`: Your assigned Service Bureau BIC (e.g., `SBXACHSS`).
- `KEYCLOAK_AZQORE_CLIENT_ID`: The "Client ID" of the client you created in Keycloak.
- `KEYCLOAK_AZQORE_CLIENT_SECRET`: The "Client Secret" for that client. This is a sensitive value.

---

## Legacy Integration Method: Direct SWIFT Connection

This details the original direct mTLS/SFTP connection method. This is no longer the primary, tested integration.

### Required artifacts from bank/partner
- Endpoints: hostnames/IPs for Test and Prod, protocols (AS4/SFTP/REST)
- Bank BIC(s), enterprise identifiers (e.g., DN), gpi details (if applicable)
- X.509 certificates: client cert/key, server certs, full CA trust chain, CRL/OCSP info
- TLS policies: versions (TLS 1.3 preferred), cipher suites, mTLS requirements
- Authentication: usernames/passwords or tokens (if REST), key exchange procedures
- IP whitelisting ranges and change process
- Test suites: SWIFT gpi, bank-specific scenarios, acceptance criteria
- SLAs: availability windows, maintenance windows, cut-off times
- Message specs: ISO 20022 profiles (pacs.008), any MT mapping specifics
- Environments: endpoints, credentials, certificates for both Test and Prod

## Preparation in this platform
1. Load secrets and certificates into Vault:
   - `secrets/swift/client_key.pem`, `secrets/swift/client_cert.pem`, `secrets/swift/ca_chain.pem`
   - Bank endpoints and credentials as secret strings
2. Configure Keycloak realms/clients and roles (user/operator/admin). Enforce MFA for admin.
3. Configure RBAC in backend via OIDC claims.
4. Enable TLS 1.3 certificates for public endpoints (frontend/backend).

## Dry-run / validation mode
- Use scripts/test_tls.sh to validate connectivity with client certificate without submitting payment.
- Use `/transfers/validate` endpoint to validate ISO 20022 messages and credentials.
- Dry-run can perform TLS handshake, message envelope signing, and schema validation, but will not submit.

## Certificate installation (Linux)
See `scripts/install_certs.sh` to install provided CA chain and client certificates into the container or host trust stores. Never commit certificates.

## Connectivity tests
- `openssl s_client -connect bank.example.com:443 -showcerts -tls1_3 -cert client_cert.pem -key client_key.pem -CAfile ca_chain.pem`
- `curl --http1.1 --tlsv1.3 --cert client_cert.pem --key client_key.pem --cacert ca_chain.pem https://bank.example.com/ping`

## End-to-end test plan with bank
- Scenario 1: Happy path pacs.008 with valid IBAN/BIC, amount < 10k USD
- Scenario 2: KYC pending: block due to missing docs
- Scenario 3: AML threshold breach (>10k USD) triggers manual review
- Scenario 4: Invalid BIC/IBAN returns schema/validation error
- Scenario 5: Network error path, retries and FAILED state with audit trail
For each scenario, exchange test pacs.008 samples and expected acknowledgements.

## Compliance obligations
- Retain logs/audit for mandated duration (e.g., 7 years).
- Ensure KYC/AML per local/international regulations.
- Maintain SLAs and incident response processes.
- Perform periodic key rotation and certificate renewal.

## Activation
- Obtain written approval from bank.
- Switch connectors from dry-run to live by setting `CONNECTOR_SWIFT_MODE=live` (operator action only).
- Validate final connectivity and send a test message in production window.
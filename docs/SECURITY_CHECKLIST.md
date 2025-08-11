# Security & Compliance Checklist (Pre-Prod)

- OAuth2/OIDC enforced, MFA enabled for admin roles
- TLS 1.3 enabled end-to-end, certs via Certificate Manager
- Secrets in Vault/GSM, least-privilege access, rotation configured
- AES-256 encryption at rest for sensitive fields
- KYC docs encrypted, access logged
- Automatic block for transfers > 10,000 USD (configurable)
- Sanctions screening integrated (test mode for dev)
- Audit logs append-only with hash chain; retention policy set
- CI security scans (SAST/Dependency/Container) passing
- Observability: metrics, logs, traces visible in Cloud Monitoring/Grafana
- Backup/restore procedures tested
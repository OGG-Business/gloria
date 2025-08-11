Install:

- Create secrets:
  - `kubectl create secret generic gpp-secrets --from-literal=database_url=... --from-literal=oidc_issuer_url=... --from-literal=oidc_audience=...`
  - `kubectl create secret tls gpp-tls --key dev-key.pem --cert dev-cert.pem`
- Deploy:

```bash
helm upgrade -i gpp ./infra/helm -n payments --create-namespace
```
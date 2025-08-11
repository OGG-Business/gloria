# Connectivity Tests

## TLS mutual auth test
```bash
scripts/connectivity/test_tls.sh https://bank.example.com/endpoint certs/client.crt certs/client.key certs/ca.crt
```

## cURL with mTLS
```bash
scripts/connectivity/curl_mtls.sh https://bank.example.com/endpoint certs/client.crt certs/client.key certs/ca.crt
```

## Dry-run transfer
```bash
python scripts/send_real_transfer.py --dry-run --amount 100 --currency USD --debtor-iban ...
```
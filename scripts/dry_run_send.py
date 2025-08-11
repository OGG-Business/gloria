#!/usr/bin/env python3
import requests
import sys

API = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8000'

# Create a demo transfer (assumes an account with id 1 exists)
transfer = requests.post(f"{API}/transfers", json={
  "debtor_account_id": 1,
  "creditor_name": "Demo Beneficiary",
  "creditor_iban": "FR1420041010050500013M02606",
  "amount": 25.50,
  "currency": "USD"
}).json()
print("Transfer created:", transfer)
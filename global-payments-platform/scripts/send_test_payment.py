#!/usr/bin/env python3
import os
import requests

API = os.environ.get("API", "https://localhost:8443")
TOKEN = os.environ["TOKEN"]
DEBTOR_ACCOUNT_ID = int(os.environ["DEBTOR_ACCOUNT_ID"])
CREDITOR_IBAN = os.environ.get("CREDITOR_IBAN", "DE12500105170648489890")
CREDITOR_BIC = os.environ.get("CREDITOR_BIC", "DEUTDEFF")
AMOUNT = os.environ.get("AMOUNT", "100.00")
CURRENCY = os.environ.get("CURRENCY", "USD")
REFERENCE = os.environ.get("REFERENCE", "Test payment")
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() in ("1","true","yes")

headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

resp = requests.post(f"{API}/transfers/", headers=headers, json={
  "debtor_account_id": DEBTOR_ACCOUNT_ID,
  "creditor_iban": CREDITOR_IBAN,
  "creditor_bic": CREDITOR_BIC,
  "amount": float(AMOUNT),
  "currency": CURRENCY,
  "reference": REFERENCE,
  "dry_run": DRY_RUN
}, verify=False)
print(resp.status_code, resp.text)
#!/usr/bin/env python3
import argparse
import requests

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--base-url', default='http://localhost:8080')
    p.add_argument('--amount', type=float, required=True)
    p.add_argument('--currency', default='USD')
    p.add_argument('--debtor-iban', required=True)
    p.add_argument('--debtor-bic', required=True)
    p.add_argument('--creditor-iban', required=True)
    p.add_argument('--creditor-bic', required=True)
    p.add_argument('--remittance-info', default='')
    p.add_argument('--channel', choices=['swift','mojaloop'], default='swift')
    p.add_argument('--dry-run', action='store_true', default=True)
    args = p.parse_args()

    payload = {
        'amount': args.amount,
        'currency': args.currency,
        'debtor_iban': args.debtor_iban,
        'debtor_bic': args.debtor_bic,
        'creditor_iban': args.creditor_iban,
        'creditor_bic': args.creditor_bic,
        'remittance_info': args.remittance_info,
        'channel': args.channel
    }
    r = requests.post(f"{args.base_url}/transfers/", json=payload)
    print(r.status_code)
    print(r.json())

if __name__ == '__main__':
    main()
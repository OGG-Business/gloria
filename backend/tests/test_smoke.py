from fastapi.testclient import TestClient
from app.main import app

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200


def test_accounts_flow():
    client = TestClient(app)
    r = client.post("/accounts/", json={
        "owner_name": "Alice",
        "iban": "DE89370400440532013000",
        "bic": "DEUTDEFF"
    })
    assert r.status_code == 200
    data = r.json()
    assert data["iban"].startswith("DE")


def test_transfer_flow():
    client = TestClient(app)
    r = client.post("/transfers/", json={
        "amount": 100.5,
        "currency": "USD",
        "debtor_iban": "DE89370400440532013000",
        "debtor_bic": "DEUTDEFF",
        "creditor_iban": "GB29NWBK60161331926819",
        "creditor_bic": "NWBKGB2L",
        "remittance_info": "Invoice 123"
    })
    assert r.status_code == 200
    tid = r.json()["id"]
    r2 = client.get(f"/transfers/{tid}/events")
    assert r2.status_code == 200
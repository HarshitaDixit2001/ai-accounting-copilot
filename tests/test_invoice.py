from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_invoice():
    response = client.post(
        "/invoices",
        json={
            "invoice_number": "INV-TEST-001",
            "vendor": "ABC Traders",
            "amount": 25000,
            "description": "Office equipment",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Invoice created successfully"
    assert data["invoice"]["invoice_number"] == "INV-TEST-001"
    assert data["invoice"]["vendor"] == "ABC Traders"
    assert data["invoice"]["amount"] == 25000


def test_create_invoice_rejects_negative_amount():
    response = client.post(
        "/invoices",
        json={
            "invoice_number": "INV-TEST-002",
            "vendor": "ABC Traders",
            "amount": -500,
            "description": "Invalid invoice",
        },
    )

    assert response.status_code == 422


def test_invoice_not_found():
    response = client.get("/invoices/999999")

    assert response.status_code == 404

    data = response.json()

    assert data["error"] == "invoice_not_found"

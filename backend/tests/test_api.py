import os
import uuid
import pytest
from fastapi.testclient import TestClient

# Tests require a dedicated test database URL, never point these tests at production.
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_superas.db")
os.environ.setdefault("JWT_SECRET", "test-only-secret-that-is-not-for-production")
os.environ.setdefault("BOOTSTRAP_ADMIN_USERNAME", "testadmin")
os.environ.setdefault("BOOTSTRAP_ADMIN_PASSWORD", "test-only-password")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

from app.main import app
from app.db import Base, engine

@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)

def auth_headers(client):
    response = client.post("/api/auth/login", json={
        "username": os.environ["BOOTSTRAP_ADMIN_USERNAME"],
        "password": os.environ["BOOTSTRAP_ADMIN_PASSWORD"],
    })
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

def test_products_require_auth(client):
    response = client.get("/api/products")
    assert response.status_code == 401

def test_create_and_search_product(client):
    headers = auth_headers(client)
    barcode = "TEST" + uuid.uuid4().hex[:12]
    response = client.post("/api/products", headers=headers, json={
        "barcode": barcode,
        "name": "Arroz teste",
        "unit": "UN",
        "cost_price": "4.50",
        "sale_price": "6.99",
        "stock_qty": "10.000",
        "min_stock": "2.000",
    })
    assert response.status_code == 201, response.text
    assert response.json()["sale_price"] == "6.99"
    search = client.get("/api/products", headers=headers, params={"search": "Arroz teste"})
    assert search.status_code == 200
    assert any(item["barcode"] == barcode for item in search.json())

def test_duplicate_barcode_rejected(client):
    headers = auth_headers(client)
    barcode = "DUP" + uuid.uuid4().hex[:10]
    payload = {"barcode": barcode, "name": "Produto A", "sale_price": "2.50"}
    assert client.post("/api/products", headers=headers, json=payload).status_code == 201
    response = client.post("/api/products", headers=headers, json={**payload, "name": "Produto B"})
    assert response.status_code == 409

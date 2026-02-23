import pytest
from fastapi.testclient import TestClient


def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Copywriter"


def test_copy_types(client: TestClient):
    response = client.get("/api/v1/copy/types")
    assert response.status_code == 200
    data = response.json()
    assert "types" in data
    assert len(data["types"]) == 6
    
    type_ids = [t["id"] for t in data["types"]]
    assert "marketing" in type_ids
    assert "product" in type_ids
    assert "ad" in type_ids


def test_generate_requires_device_id(client: TestClient):
    response = client.post("/api/v1/copy/generate", json={
        "copy_type": "marketing",
        "topic": "Test product"
    })
    assert response.status_code == 422  # Validation error


def test_products(client: TestClient):
    response = client.get("/api/v1/payment/products")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert len(data["products"]) == 3
    
    for product in data["products"]:
        assert "sku" in product
        assert "name" in product
        assert "generations" in product
        assert "price_cents" in product


def test_token_status(client: TestClient):
    response = client.get("/api/v1/tokens/status/test-device-123")
    assert response.status_code == 200
    data = response.json()
    assert "can_generate" in data
    assert "remaining_generations" in data
    assert data["can_generate"] == True  # First time = free trial


def test_token_status_free_trial(client: TestClient):
    response = client.get("/api/v1/tokens/status/new-device-xyz")
    assert response.status_code == 200
    data = response.json()
    assert data["is_free_trial"] == True
    assert data["remaining_generations"] == 3  # FREE_GENERATIONS_PER_DEVICE


def test_tokens_by_device_empty(client: TestClient):
    response = client.get("/api/v1/tokens/by-device/no-tokens-device")
    assert response.status_code == 200
    data = response.json()
    assert data["tokens"] == []
    assert data["total_remaining"] == 0


def test_metrics_endpoint(client: TestClient):
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "payment_success_total" in response.text


def test_checkout_invalid_sku(client: TestClient):
    response = client.post("/api/v1/payment/create-checkout", json={
        "product_sku": "invalid_sku",
        "device_id": "test-device",
        "success_url": "http://localhost/success",
        "cancel_url": "http://localhost/cancel"
    })
    assert response.status_code == 400
    data = response.json()
    detail = data.get("detail", "")
    if isinstance(detail, dict):
        assert "error" in detail or "message" in detail or "Invalid" in str(detail)
    else:
        assert "Invalid" in detail


def test_error_detail_format_402(client: TestClient, db):
    """Test that 402 errors return properly serializable detail"""
    from app.models import FreeTrialUsage
    
    # Exhaust free trial
    usage = FreeTrialUsage(device_id="exhausted-device", generations_used=10)
    db.add(usage)
    db.commit()
    
    response = client.post("/api/v1/copy/generate", json={
        "copy_type": "marketing",
        "topic": "Test",
        "device_id": "exhausted-device",
        "tone": "professional",
        "language": "en",
        "variations": 1
    })
    
    assert response.status_code == 402
    data = response.json()
    detail = data.get("detail")
    
    # Detail must be string or object with error/message
    if isinstance(detail, dict):
        assert "error" in detail or "message" in detail, \
            f"Object detail must have 'error' or 'message': {detail}"
    else:
        assert isinstance(detail, str), f"Detail must be string or dict: {detail}"

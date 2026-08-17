"""
Automated tests for CORS headers, OpenAPI schema completeness, and HTTP status codes.
"""
import os
import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app

app = create_app()
client = TestClient(app)


def test_cors_preflight_allowed_origin():
    """Verify CORS preflight OPTIONS request returns correct Access-Control-Allow-Origin header."""
    headers = {
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    }
    response = client.options("/batches/create", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_preflight_chat_production_frontend():
    """Verify CORS preflight OPTIONS request for /chat returns 200 and allowed origin for production Vercel frontend."""
    headers = {
        "Origin": "https://dravya-ayurvedic-blockchain-platfor-nine.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type, Authorization",
    }
    response = client.options("/chat", headers=headers)
    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://dravya-ayurvedic-blockchain-platfor-nine.vercel.app"
    )
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert response.headers.get("access-control-allow-credentials") == "true"


def test_cors_custom_origin_env_var(monkeypatch):
    """Verify DRAVYA_CORS_ORIGINS and DRAVYA_FRONTEND_ORIGIN environment variables add allowed origins."""
    monkeypatch.setenv("DRAVYA_CORS_ORIGINS", "http://custom-frontend.org, https://another-domain.com/")
    monkeypatch.setenv("DRAVYA_FRONTEND_ORIGIN", "https://deployed-app.vercel.app")
    custom_app = create_app()
    custom_client = TestClient(custom_app)

    # Test custom origin 1
    headers1 = {
        "Origin": "http://custom-frontend.org",
        "Access-Control-Request-Method": "GET",
    }
    response1 = custom_client.options("/inventory/summary", headers=headers1)
    assert response1.status_code == 200
    assert response1.headers.get("access-control-allow-origin") == "http://custom-frontend.org"

    # Test custom origin 2 (trailing slash stripped)
    headers2 = {
        "Origin": "https://another-domain.com",
        "Access-Control-Request-Method": "POST",
    }
    response2 = custom_client.options("/chat", headers=headers2)
    assert response2.status_code == 200
    assert response2.headers.get("access-control-allow-origin") == "https://another-domain.com"

    # Test frontend origin env var
    headers3 = {
        "Origin": "https://deployed-app.vercel.app",
        "Access-Control-Request-Method": "POST",
    }
    response3 = custom_client.options("/chat", headers=headers3)
    assert response3.status_code == 200
    assert response3.headers.get("access-control-allow-origin") == "https://deployed-app.vercel.app"


def test_cors_disallowed_origin():
    """Verify unallowed origin does not receive Access-Control-Allow-Origin header on OPTIONS preflight."""
    headers = {
        "Origin": "https://malicious-site.evil.com",
        "Access-Control-Request-Method": "POST",
    }
    response = client.options("/chat", headers=headers)
    assert response.headers.get("access-control-allow-origin") is None


def test_openapi_json_completeness():
    """Verify OpenAPI schema contains all expected paths and metadata."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()

    assert "paths" in schema
    paths = schema["paths"]

    expected_paths = [
        "/health",
        "/batches/create",
        "/batches/create-from-image",
        "/batches/{batch_id}",
        "/batches/{batch_id}/traceability",
        "/batches/herb/{herb_name}",
        "/batches/farmer/{farmer_id}",
        "/batches/summary/herb/{herb_name}",
        "/batches/summary/farmer/{farmer_id}",
        "/inventory/summary",
        "/chat",
    ]

    for ep in expected_paths:
        assert ep in paths, f"Expected endpoint '{ep}' missing from OpenAPI paths."


def test_endpoint_error_status_codes():
    """Verify standard status codes and error formats for invalid inputs."""
    # 1. 404 Batch Not Found
    resp_404 = client.get("/batches/NONEXISTENT-BATCH-12345")
    assert resp_404.status_code == 404
    err_404 = resp_404.json()
    assert "error" in err_404 or "detail" in err_404

    # 2. 400 Invalid Quantity
    resp_400 = client.post(
        "/batches/create",
        json={
          "herb_species": "Ashwagandha",
          "farmer_id": "F001",
          "quantity": -10.0,
          "harvest_date": "2026-08-10",
        },
    )
    assert resp_400.status_code == 400 or resp_400.status_code == 422

    # 3. 422 Missing Required Field
    resp_422 = client.post(
        "/batches/create",
        json={"farmer_id": "F001"},
    )
    assert resp_422.status_code == 422

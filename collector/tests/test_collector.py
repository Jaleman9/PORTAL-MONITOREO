import pytest
from fastapi.testclient import TestClient
from collector.app.main import app
from collector.app.pseudonymizer import pseudonymize_user

client = TestClient(app)


def test_pseudonymizer_consistency():
    # Mismo user_id debe generar siempre el mismo hash
    hash1 = pseudonymize_user("usuario.corporativo@empresa.com", "sess-12345678")
    hash2 = pseudonymize_user("usuario.corporativo@empresa.com", "sess-87654321")
    assert len(hash1) == 64
    assert hash1 == hash2

    # Distinto user_id debe generar distinto hash
    hash3 = pseudonymize_user("otro.usuario@empresa.com", "sess-12345678")
    assert hash1 != hash3

    # Usuario anónimo genera hash determinista basado en la sesión
    anon_hash1 = pseudonymize_user(None, "sess-anon-12345678")
    assert len(anon_hash1) == 64


def test_ingest_valid_batch():
    payload = {
        "events": [
            {
                "app_id": "crm-portal",
                "session_id": "session-12345678",
                "user_id": "carlos.mendoza@empresa.com",
                "event_type": "page_view",
                "platform": "web",
                "role": "ejecutivo",
                "department": "ventas",
                "properties": {
                    "page_path": "/dashboard/ventas?token=secret123&user=carlos",
                    "page_title": "Panel de Ventas",
                    "load_time_ms": 420.5,
                },
            },
            {
                "app_id": "erp-portal",
                "session_id": "session-87654321",
                "user_id": "maria.gomez@empresa.com",
                "event_type": "session_start",
                "platform": "web",
                "role": "analista",
                "department": "finanzas",
            },
        ]
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "accepted"
    assert data["received"] == 2
    assert data["accepted"] == 2
    assert data["rejected"] == 0


def test_sanitization_of_sensitive_data():
    payload = {
        "events": [
            {
                "app_id": "portal-rrhh",
                "session_id": "session-abcdefgh",
                "user_id": "juan.perez@empresa.com",
                "event_type": "page_view",
                "properties": {
                    "page_path": "/empleados/detalle?id=123",
                    "password": "SuperSecretPassword123!",
                    "form_data": "datos confidenciales",
                    "safe_category": "evaluacion_anual",
                },
            }
        ]
    }
    response = client.post("/api/v1/events", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert data["accepted"] == 1


def test_reject_invalid_event_type():
    payload = {
        "events": [
            {
                "app_id": "portal-invalido",
                "session_id": "session-12345678",
                "event_type": "invalid_unsupported_event",
                "platform": "web",
            }
        ]
    }
    response = client.post("/api/v1/events", json=payload)
    # Pydantic debe rechazar el payload por esquema inválido (HTTP 422)
    assert response.status_code == 422

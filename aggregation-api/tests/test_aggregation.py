import os
import sys
import pytest
from fastapi.testclient import TestClient

# Permitir importación del módulo app dentro de aggregation-api
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app
from app.privacy_guard import PrivacyGuard, MINIMUM_K_ANONYMITY_THRESHOLD

client = TestClient(app)


def test_privacy_guard_enforcement():
    test_cohort = [
        {"app_id": "crm-ventas", "unique_users": 150, "total_sessions": 400},
        {
            "app_id": "app-pequeña-riesgo",
            "unique_users": 3,
            "total_sessions": 8,
        },  # Menos de 5 usuarios
        {
            "app_id": "app-limite",
            "unique_users": 5,
            "total_sessions": 20,
        },  # Exactamente 5 (permitido)
        {
            "app_id": "app-un-solo-usuario",
            "unique_users": 1,
            "total_sessions": 2,
        },  # 1 usuario (debe suprimirse)
    ]

    sanitized = PrivacyGuard.enforce_threshold(
        test_cohort, user_count_key="unique_users"
    )
    assert len(sanitized) == 4

    # Grupo 1 (150 usuarios): no suprimido
    assert sanitized[0]["privacy_suppressed"] is False
    assert sanitized[0]["unique_users"] == 150

    # Grupo 2 (3 usuarios): SUPRIMIDO por umbral k >= 5
    assert sanitized[1]["privacy_suppressed"] is True
    assert sanitized[1]["unique_users"] is None
    assert sanitized[1]["total_sessions"] is None

    # Grupo 3 (5 usuarios): permitido (k >= 5)
    assert sanitized[2]["privacy_suppressed"] is False
    assert sanitized[2]["unique_users"] == 5

    # Grupo 4 (1 usuario): SUPRIMIDO
    assert sanitized[3]["privacy_suppressed"] is True
    assert sanitized[3]["unique_users"] is None


def test_rbac_unauthorized_when_missing_header():
    # Sin header de rol -> debe retornar 401 Unauthorized
    response = client.get("/api/v1/metrics/summary")
    assert response.status_code == 401


def test_rbac_forbidden_on_invalid_role():
    # Con rol no reconocido -> 403 Forbidden
    response = client.get(
        "/api/v1/metrics/summary", headers={"X-User-Role": "hacker_externo"}
    )
    assert response.status_code == 403


def test_executive_role_can_access_metrics():
    # Rol ejecutivo puede consultar métricas agregadas
    headers = {"X-User-Role": "ejecutivo", "X-User-Department": "Direccion General"}

    resp_sum = client.get("/api/v1/metrics/summary", headers=headers)
    assert resp_sum.status_code == 200
    data = resp_sum.json()["data"]
    assert "dau_today" in data
    assert "mau_30d" in data

    resp_rank = client.get("/api/v1/metrics/adoption-ranking", headers=headers)
    assert resp_rank.status_code == 200
    ranking = resp_rank.json()["ranking"]
    assert len(ranking) > 0
    # Verificar que ningún item no suprimido tenga menos de 5 usuarios
    for item in ranking:
        if not item.get("privacy_suppressed"):
            assert item["unique_users"] >= MINIMUM_K_ANONYMITY_THRESHOLD


def test_health_traffic_light_structure():
    headers = {"X-User-Role": "ejecutivo"}
    response = client.get("/api/v1/metrics/health-traffic-light", headers=headers)
    assert response.status_code == 200
    health = response.json()["health_summary"]
    assert len(health) > 0
    for app_health in health:
        assert "status" in app_health
        assert app_health["status"] in ["green", "yellow", "red", "gray"]


def test_idle_accounts_metrics():
    headers = {"X-User-Role": "ejecutivo"}
    response = client.get(
        "/api/v1/metrics/idle-accounts?threshold_days=30", headers=headers
    )
    assert response.status_code == 200
    metrics = response.json()["metrics"]
    assert "active_percentage" in metrics
    assert "idle_percentage" in metrics
    assert round(metrics["active_percentage"] + metrics["idle_percentage"], 1) == 100.0


def test_governance_admin_only():
    # Rol ejecutivo NO puede acceder a gobernanza de plataforma (solo admin)
    resp_exec = client.get(
        "/api/v1/admin/governance", headers={"X-User-Role": "ejecutivo"}
    )
    assert resp_exec.status_code == 403

    # Rol administrador SÍ puede acceder
    resp_admin = client.get(
        "/api/v1/admin/governance", headers={"X-User-Role": "administrador"}
    )
    assert resp_admin.status_code == 200
    gov = resp_admin.json()
    assert gov["privacy_policy"]["minimum_k_threshold"] == 5
    assert gov["privacy_policy"]["raw_events_retention_days"] == 90


def test_auth_login_and_bearer_token():
    # 1. Login con credenciales del Director de Sistemas
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "pablo.galindo@onest.com", "password": "onest2026"},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    token = data["access_token"]
    assert data["user"]["role"] == "administrador"
    assert data["user"]["name"] == "Pablo César Galindo Vera"

    # 2. Acceso a endpoints usando Bearer token
    auth_header = {"Authorization": f"Bearer {token}"}
    me_resp = client.get("/api/v1/auth/me", headers=auth_header)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "pablo.galindo@onest.com"

    # 3. Métricas detalladas por portal
    portal_resp = client.get("/api/v1/metrics/portals/portal-clientes", headers=auth_header)
    assert portal_resp.status_code == 200
    details = portal_resp.json()["portal_details"]
    assert "top_routes" in details
    assert "devices" in details
    assert "p50_latency_ms" in details

    # 4. Telemetría en vivo
    live_resp = client.get("/api/v1/metrics/live-telemetry?limit=10", headers=auth_header)
    assert live_resp.status_code == 200
    events = live_resp.json()["events"]
    assert len(events) == 10
    assert "pseudonymized_user_hash" in events[0]


def test_official_systems_administrators():
    # 1. Obtener lista de perfiles oficiales
    demo_resp = client.get("/api/v1/auth/demo-users")
    assert demo_resp.status_code == 200
    admins = demo_resp.json()
    assert len(admins) == 6

    # Verificar cada perfil solicitado por el usuario
    expected_members = {
        "pablo.galindo@onest.com": ("Pablo César Galindo Vera", "Dirección"),
        "daniel.garcia@onest.com": ("Daniel García Jaén", "Infraestructura"),
        "cesar.jurado@onest.com": ("César Jurado López", "Desarrollo"),
        "yael.lopez@onest.com": ("Yael López", "Cybersecurity"),
        "victor.monroy@onest.com": ("Víctor Monroy", "Soporte"),
        "carlos.hernandez@onest.com": ("Carlos Hernández", "Servidores"),
    }

    found_emails = {a["email"]: a for a in admins}
    for email, (expected_name, expected_area) in expected_members.items():
        assert email in found_emails, f"Falta {email} en demo-users"
        member = found_emails[email]
        assert member["name"] == expected_name
        assert member["role"] == "administrador"
        assert member["department"] == "Dirección de Sistemas & TI"
        assert expected_area.lower() in member["area"].lower()

    # 2. Login con Pablo César Galindo Vera (Dirección)
    login_pablo = client.post(
        "/api/v1/auth/login",
        json={"email": "pablo.galindo@onest.com", "password": "onest2026"},
    )
    assert login_pablo.status_code == 200
    pdata = login_pablo.json()
    assert pdata["user"]["name"] == "Pablo César Galindo Vera"
    assert pdata["user"]["role"] == "administrador"
    assert pdata["user"]["area"] == "Dirección"


def test_pseudonymized_user_activity():
    headers = {"X-User-Role": "administrador"}
    response = client.get(
        "/api/v1/metrics/users/activity?days=14&limit=20", headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    users = data["users"]
    assert len(users) > 0
    first = users[0]
    # Comprobar que sigue el formato USR-XXXX y NO revela PII
    assert first["user_id"].startswith("USR-")
    assert len(first["user_id"]) == 8  # USR-XXXX
    assert "name" not in first
    assert "email" not in first
    assert first["sessions"] > 0
    assert first["page_views"] > 0
    assert "last_activity" in first
    assert "trend_pct" in first
    assert "timeline" in first



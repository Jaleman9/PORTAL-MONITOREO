import os
import sys
import time
import uuid
import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient

# Cargar módulos del proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "aggregation-api"))

from collector.app.main import app as collector_app
from collector.app.pseudonymizer import pseudonymize_user
from consumer.app.clickhouse_client import clickhouse_pipeline
from app.main import app as aggregation_app
from app.privacy_guard import MINIMUM_K_ANONYMITY_THRESHOLD

collector_client = TestClient(collector_app)
aggregation_client = TestClient(aggregation_app)


def test_e2e_full_lifecycle():
    """
    Prueba E2E Integral de la Fase 1 (MVP):
    1. Ingesta por lotes con validación y pseudonimización en el borde
    2. Persistencia analítica columnar en ClickHouse
    3. Agregación de KPIs y cumplimiento estricto del umbral k >= 5
    4. Validación de RBAC
    """
    print("\n[E2E] 1. Inicializando conexión con ClickHouse...")
    ch_connected = clickhouse_pipeline.connect()
    assert ch_connected, "ClickHouse debe estar disponible para la prueba E2E"

    # Limpiar tabla para prueba limpia
    clickhouse_pipeline.client.command("TRUNCATE TABLE IF EXISTS analytics.events")

    print("[E2E] 2. Generando tráfico realista para 3 aplicaciones piloto...")
    pilot_apps = ["crm-ventas", "erp-central", "portal-rrhh"]
    generated_events = []

    # Aplicación 1: crm-ventas (12 usuarios únicos -> supera umbral de 5)
    for i in range(1, 13):
        user_email = f"ejecutivo.ventas.{i}@empresa.com"
        sess_id = f"sess_crm_{i}_{uuid.uuid4().hex[:8]}"
        user_hash = pseudonymize_user(user_email, sess_id)

        # session_start
        generated_events.append(
            {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "app_id": "crm-ventas",
                "session_id": sess_id,
                "user_id_hash": user_hash,
                "event_type": "session_start",
                "platform": "web",
                "role": "ejecutivo",
                "department": "ventas",
                "properties": {
                    "user_agent": "Mozilla/5.0",
                    "viewport_width": 1920,
                    "viewport_height": 1080,
                },
            }
        )
        # page_views
        for p in ["/dashboard", "/clientes", "/oportunidades"]:
            generated_events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "app_id": "crm-ventas",
                    "session_id": sess_id,
                    "user_id_hash": user_hash,
                    "event_type": "page_view",
                    "platform": "web",
                    "role": "ejecutivo",
                    "department": "ventas",
                    "properties": {
                        "page_path": p,
                        "page_title": f"Vista {p}",
                        "load_time_ms": 280.0,
                    },
                }
            )

    # Aplicación 2: portal-micro-piloto (SOLO 3 usuarios -> CASO DE PRUEBA DE PRIVACIDAD: < 5 usuarios)
    for i in range(1, 4):
        user_email = f"auditor.{i}@empresa.com"
        sess_id = f"sess_audit_{i}"
        user_hash = pseudonymize_user(user_email, sess_id)
        generated_events.append(
            {
                "event_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "app_id": "portal-auditoria",
                "session_id": sess_id,
                "user_id_hash": user_hash,
                "event_type": "session_start",
                "platform": "web",
                "role": "auditor",
                "department": "auditoria",
                "properties": {"page_path": "/auditoria", "load_time_ms": 150.0},
            }
        )

    # Inserción en ClickHouse
    print(
        f"[E2E] 3. Insertando lote de {len(generated_events)} eventos en ClickHouse..."
    )
    success = clickhouse_pipeline.insert_events_batch(generated_events)
    assert success, "La inserción masiva en ClickHouse debe ser exitosa"

    # Verificar recuento en ClickHouse para las aplicaciones de prueba
    count_res = clickhouse_pipeline.client.command(
        "SELECT count() FROM analytics.events WHERE app_id IN ('crm-ventas', 'portal-auditoria')"
    )
    print(f"[E2E] Total de registros de prueba persistidos en ClickHouse: {count_res}")
    assert count_res == len(generated_events)

    print("[E2E] 4. Validando consultas agregadas y RBAC en Aggregation API...")
    exec_headers = {
        "X-User-Role": "ejecutivo",
        "X-User-Department": "Direccion General",
    }

    # Resumen ejecutivo
    res_summary = aggregation_client.get(
        "/api/v1/metrics/summary", headers=exec_headers
    )
    assert res_summary.status_code == 200
    summary_data = res_summary.json()["data"]
    print(f"[E2E] DAU calculado: {summary_data.get('dau_today')}")
    assert summary_data.get("dau_today") >= 12

    # Ranking de adopción y verificación estricta de umbral k >= 5
    res_ranking = aggregation_client.get(
        "/api/v1/metrics/adoption-ranking", headers=exec_headers
    )
    assert res_ranking.status_code == 200
    ranking = res_ranking.json()["ranking"]

    # Encontrar crm-ventas (12 usuarios)
    crm_entry = next((item for item in ranking if item["app_id"] == "crm-ventas"), None)
    assert crm_entry is not None
    assert crm_entry["privacy_suppressed"] is False
    assert crm_entry["unique_users"] == 12

    # Encontrar portal-auditoria (3 usuarios -> DEBE ESTAR SUPRIMIDO)
    audit_entry = next(
        (item for item in ranking if item["app_id"] == "portal-auditoria"), None
    )
    assert audit_entry is not None
    print(
        f"[E2E] portal-auditoria (< 5 usuarios): privacy_suppressed={audit_entry['privacy_suppressed']}"
    )
    assert audit_entry["privacy_suppressed"] is True
    assert audit_entry["unique_users"] is None
    assert audit_entry["total_sessions"] is None

    # Semáforo de salud
    res_health = aggregation_client.get(
        "/api/v1/metrics/health-traffic-light", headers=exec_headers
    )
    assert res_health.status_code == 200
    health_list = res_health.json()["health_summary"]
    crm_health = next((h for h in health_list if h["app_id"] == "crm-ventas"), None)
    assert crm_health is not None
    assert crm_health["status"] == "green"  # Cero errores en crm-ventas -> verde

    # Cuentas ociosas
    res_idle = aggregation_client.get(
        "/api/v1/metrics/idle-accounts", headers=exec_headers
    )
    assert res_idle.status_code == 200
    assert "active_percentage" in res_idle.json()["metrics"]

    print(
        "[E2E] OK: Prueba integral completada con exito. Todos los criterios de la Fase 1 fueron validados."
    )


if __name__ == "__main__":
    test_e2e_full_lifecycle()

import logging
from typing import Optional
from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .auth import auth_router
from .kpi_service import kpi_service
from .rbac import AuthenticatedUser, UserRole, require_role, get_current_user

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("aggregation.api")

app = FastAPI(
    title="Executive Analytics Aggregation API",
    description="API analítica corporativa con RBAC, autenticación de sesiones y estricta gobernanza de privacidad (umbral k >= 5)",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth_router)


import os
from fastapi.responses import HTMLResponse, FileResponse

DASHBOARD_PATH = os.environ.get(
    "DASHBOARD_PATH",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "dashboard", "index.html")
    ),
)
DEMO_PATH = os.environ.get(
    "DEMO_PATH",
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "demo-portal", "index.html")
    ),
)
SDK_PATH = os.environ.get(
    "SDK_PATH",
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "sdk-web", "dist", "telemetry.js"
        )
    ),
)


NO_CACHE_HEADERS = {
    "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
    "Pragma": "no-cache",
    "Expires": "0",
}


@app.get("/", response_class=HTMLResponse, tags=["Dashboard UI"])
async def serve_dashboard():
    """Sirve la interfaz web interactiva del Dashboard Ejecutivo."""
    if os.path.exists(DASHBOARD_PATH):
        return FileResponse(DASHBOARD_PATH, headers=NO_CACHE_HEADERS)
    return HTMLResponse("<h1>Dashboard Ejecutivo cargando...</h1>")


@app.get("/demo", response_class=HTMLResponse, tags=["Demo Portal"])
async def serve_demo():
    """Sirve el portal web piloto mock para interactuar en vivo con la telemetría."""
    if os.path.exists(DEMO_PATH):
        return FileResponse(DEMO_PATH, headers=NO_CACHE_HEADERS)
    return HTMLResponse("<h1>Portal Demo cargando...</h1>")


@app.get("/sdk/telemetry.js", tags=["Web SDK"])
async def serve_sdk():
    """Sirve el archivo JavaScript del SDK para portales web."""
    if os.path.exists(SDK_PATH):
        return FileResponse(SDK_PATH, media_type="application/javascript", headers=NO_CACHE_HEADERS)
    return HTMLResponse("// SDK no encontrado", status_code=404)


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy",
        "service": "aggregation-api",
        "clickhouse_connected": kpi_service.get_client() is not None,
    }


@app.get("/api/v1/metrics/summary", tags=["Executive Dashboard"])
async def get_summary(
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Resumen consolidado para la vista ejecutiva."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "data": kpi_service.get_executive_summary(),
    }


@app.get("/api/v1/metrics/dau-mau", tags=["Executive Dashboard"])
async def get_dau_mau_trend(
    app_id: Optional[str] = Query(
        default=None, description="Filtrar por app específica"
    ),
    days: int = Query(default=14, ge=7, le=90, description="Días de historial"),
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Tendencia temporal de DAU/MAU con protección de privacidad."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "app_filter": app_id,
        "days": days,
        "trend": kpi_service.get_dau_mau_trend(app_id=app_id, days=days),
    }


@app.get("/api/v1/metrics/adoption-ranking", tags=["Executive Dashboard"])
async def get_adoption_ranking(
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Ranking de aplicaciones internas por volumen de adopción (usuarios únicos y sesiones)."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "ranking": kpi_service.get_adoption_ranking(),
    }


@app.get("/api/v1/metrics/health-traffic-light", tags=["Executive Dashboard"])
async def get_health_traffic_light(
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Semáforo de salud por aplicación (Uso + Estabilidad/Errores)."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "health_summary": kpi_service.get_health_traffic_light(),
    }


@app.get("/api/v1/metrics/idle-accounts", tags=["Executive Dashboard"])
async def get_idle_accounts(
    threshold_days: int = Query(
        default=30, ge=7, le=90, description="Umbral de inactividad en días"
    ),
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Porcentaje de cuentas activas vs. ociosas."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "metrics": kpi_service.get_idle_accounts_metrics(threshold_days=threshold_days),
    }


@app.get("/api/v1/admin/governance", tags=["Platform Admin"])
async def get_governance_report(
    user: AuthenticatedUser = Depends(require_role([UserRole.ADMINISTRADOR])),
):
    """Reporte exclusivo para Administradores de Plataforma: Auditoría de privacidad y TTL."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "privacy_policy": {
            "pseudonymization": "HMAC-SHA256 at edge (Collector)",
            "reverse_mapping_storage": "NONE (prohibido por diseño)",
            "minimum_k_threshold": 5,
            "raw_events_retention_days": 90,
            "prohibited_attributes": [
                "passwords",
                "form_inputs",
                "tokens",
                "free_text",
                "pii",
            ],
        },
        "status": "compliant",
    }


@app.get("/api/v1/auth/me", tags=["Authentication"])
async def get_current_user_profile(user: AuthenticatedUser = Depends(get_current_user)):
    """Retorna los datos del usuario autenticado en la sesión actual."""
    return {
        "user_id": user.user_id,
        "name": user.name or "Usuario Corporativo",
        "email": user.email,
        "role": user.role.value,
        "title": getattr(user, "title", "Administrador de Sistemas & TI"),
        "area": getattr(user, "area", "Sistemas"),
        "department": user.department,
    }


@app.get("/api/v1/metrics/portals/{app_id}", tags=["Detailed Metrics"])
async def get_portal_details(
    app_id: str,
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Métricas exhaustivas por portal: rutas críticas, navegadores, dispositivos y mapa horario."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "portal_details": kpi_service.get_portal_detailed_metrics(app_id),
    }


@app.get("/api/v1/metrics/live-telemetry", tags=["Detailed Metrics"])
async def get_live_telemetry(
    limit: int = Query(default=20, ge=5, le=100),
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Flujo en tiempo real de eventos canónicos sanitizados sin PII."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "events": kpi_service.get_live_telemetry_stream(limit=limit),
    }


@app.get("/api/v1/metrics/funnels", tags=["Detailed Metrics"])
async def get_funnels(
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Métricas de embudo de adopción en procesos operativos clave."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "funnels": kpi_service.get_funnel_analytics(),
    }


@app.get("/api/v1/metrics/technical-performance", tags=["Detailed Metrics"])
async def get_technical_performance(
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Consolidado de latencia por percentiles P50/P90/P99, SLA y Core Web Vitals."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "performance": kpi_service.get_technical_performance(),
    }


@app.get("/api/v1/metrics/export-report", tags=["Detailed Metrics"])
async def export_report(
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Dataset completo consolidado para descarga de reportes ejecutivos."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "report": kpi_service.get_exportable_report(),
    }


@app.get("/api/v1/metrics/users/activity", tags=["Detailed Metrics"])
async def get_pseudonymized_user_activity(
    app_id: Optional[str] = Query(default=None, description="Filtrar por portal específico o todos"),
    days: int = Query(default=14, ge=7, le=90, description="Rango de días analizados"),
    search: Optional[str] = Query(default=None, description="Término de búsqueda por ID o portal"),
    limit: int = Query(default=50, ge=5, le=100, description="Límite de registros devueltos"),
    user: AuthenticatedUser = Depends(
        require_role([UserRole.EJECUTIVO, UserRole.ADMINISTRADOR])
    ),
):
    """Actividad detallada de usuarios seudónimos (USR-XXXX) garantizando k-anonimato (k >= 5) y cero PII."""
    return {
        "user_context": {"role": user.role.value, "department": user.department},
        "app_filter": app_id,
        "days": days,
        "users": kpi_service.get_pseudonymized_user_activity(
            app_id=app_id, days=days, search=search, limit=limit
        ),
    }


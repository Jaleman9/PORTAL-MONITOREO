import hashlib
import time
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from .rbac import UserRole

auth_router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Catálogo oficial de Administradores de Sistemas & TI (ONEST Logistics)
OFFICIAL_ADMINS: Dict[str, dict] = {
    "pablo.galindo@onest.com": {
        "id": "usr-sys-01",
        "email": "pablo.galindo@onest.com",
        "name": "Pablo César Galindo Vera",
        "role": UserRole.ADMINISTRADOR,
        "title": "Director de Sistemas & TI",
        "area": "Dirección",
        "department": "Dirección de Sistemas & TI",
        "password_hash": hashlib.sha256("onest2026".encode()).hexdigest(),
        "avatar_initials": "PG",
    },
    "daniel.garcia@onest.com": {
        "id": "usr-sys-02",
        "email": "daniel.garcia@onest.com",
        "name": "Daniel García Jaén",
        "role": UserRole.ADMINISTRADOR,
        "title": "Administrador de Infraestructura",
        "area": "Infraestructura",
        "department": "Dirección de Sistemas & TI",
        "password_hash": hashlib.sha256("onest2026".encode()).hexdigest(),
        "avatar_initials": "DG",
    },
    "cesar.jurado@onest.com": {
        "id": "usr-sys-03",
        "email": "cesar.jurado@onest.com",
        "name": "César Jurado López",
        "role": UserRole.ADMINISTRADOR,
        "title": "Administrador de Desarrollo",
        "area": "Desarrollo",
        "department": "Dirección de Sistemas & TI",
        "password_hash": hashlib.sha256("onest2026".encode()).hexdigest(),
        "avatar_initials": "CJ",
    },
    "yael.lopez@onest.com": {
        "id": "usr-sys-04",
        "email": "yael.lopez@onest.com",
        "name": "Yael López",
        "role": UserRole.ADMINISTRADOR,
        "title": "Administrador de Cybersecurity",
        "area": "Cybersecurity",
        "department": "Dirección de Sistemas & TI",
        "password_hash": hashlib.sha256("onest2026".encode()).hexdigest(),
        "avatar_initials": "YL",
    },
    "victor.monroy@onest.com": {
        "id": "usr-sys-05",
        "email": "victor.monroy@onest.com",
        "name": "Víctor Monroy",
        "role": UserRole.ADMINISTRADOR,
        "title": "Administrador de Soporte (Alcance por confirmar)",
        "area": "Soporte",
        "department": "Dirección de Sistemas & TI",
        "password_hash": hashlib.sha256("onest2026".encode()).hexdigest(),
        "avatar_initials": "VM",
    },
    "carlos.hernandez@onest.com": {
        "id": "usr-sys-06",
        "email": "carlos.hernandez@onest.com",
        "name": "Carlos Hernández",
        "role": UserRole.ADMINISTRADOR,
        "title": "Administrador de Servidores (Alcance por confirmar)",
        "area": "Servidores",
        "department": "Dirección de Sistemas & TI",
        "password_hash": hashlib.sha256("onest2026".encode()).hexdigest(),
        "avatar_initials": "CH",
    },
}

# Diccionario ampliado con aliases para testing y retrocompatibilidad
DEMO_USERS: Dict[str, dict] = dict(OFFICIAL_ADMINS)
DEMO_USERS["director@onest.com"] = OFFICIAL_ADMINS["pablo.galindo@onest.com"]
DEMO_USERS["admin.ti@onest.com"] = OFFICIAL_ADMINS["pablo.galindo@onest.com"]
DEMO_USERS["infra@onest.com"] = OFFICIAL_ADMINS["daniel.garcia@onest.com"]
DEMO_USERS["devops@onest.com"] = OFFICIAL_ADMINS["daniel.garcia@onest.com"]
DEMO_USERS["dev@onest.com"] = OFFICIAL_ADMINS["cesar.jurado@onest.com"]
DEMO_USERS["vpn@onest.com"] = OFFICIAL_ADMINS["yael.lopez@onest.com"]
DEMO_USERS["secops@onest.com"] = OFFICIAL_ADMINS["yael.lopez@onest.com"]
DEMO_USERS["soporte@onest.com"] = OFFICIAL_ADMINS["victor.monroy@onest.com"]
DEMO_USERS["servidores@onest.com"] = OFFICIAL_ADMINS["carlos.hernandez@onest.com"]
DEMO_USERS["dba@onest.com"] = OFFICIAL_ADMINS["carlos.hernandez@onest.com"]
DEMO_USERS["ops.lead@onest.com"] = OFFICIAL_ADMINS["cesar.jurado@onest.com"]

# Almacén en memoria de tokens de sesión activos
ACTIVE_SESSIONS: Dict[str, dict] = {}


class LoginRequest(BaseModel):
    email: str
    password: Optional[str] = None
    quick_role: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    role: str
    title: str
    area: Optional[str] = None
    department: str
    avatar_initials: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in_seconds: int
    user: UserProfileResponse


def create_session_token(user_data: dict) -> str:
    raw = f"{user_data['id']}:{user_data['role'].value}:{time.time()}"
    token = "onest_tok_" + hashlib.sha256(raw.encode()).hexdigest()[:32]
    ACTIVE_SESSIONS[token] = {
        "user_id": user_data["id"],
        "email": user_data["email"],
        "name": user_data["name"],
        "role": user_data["role"],
        "title": user_data["title"],
        "area": user_data.get("area", "Sistemas"),
        "department": user_data["department"],
        "avatar_initials": user_data["avatar_initials"],
        "created_at": time.time(),
    }
    return token


@auth_router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    """Permite iniciar sesión con email/password o mediante selección rápida de perfil de demo."""
    email_clean = payload.email.strip().lower()

    user = DEMO_USERS.get(email_clean)
    if not user:
        # En esta plataforma exclusiva para Sistemas, cualquier usuario corporativo es Administrador de Sistemas
        clean_name = email_clean.split("@")[0].replace(".", " ").replace("_", " ").title()
        user = {
            "id": f"usr-sys-{hashlib.md5(email_clean.encode()).hexdigest()[:6]}",
            "email": email_clean,
            "name": f"Ing. {clean_name}" if clean_name else "Ingeniero de Sistemas",
            "role": UserRole.ADMINISTRADOR,
            "title": "Administrador de Sistemas & TI",
            "area": "Sistemas",
            "department": "Dirección de Sistemas & TI",
            "password_hash": hashlib.sha256("onest2026".encode()).hexdigest(),
            "avatar_initials": (email_clean[:2] if len(email_clean) >= 2 else "TI").upper(),
        }

    # Todos los usuarios son administradores
    user["role"] = UserRole.ADMINISTRADOR

    # Si se envía contraseña, verificar el hash (contraseña por defecto 'onest2026' para todos los demos)
    if payload.password and payload.password != "onest2026":
        pwd_hash = hashlib.sha256(payload.password.encode()).hexdigest()
        if pwd_hash != user.get("password_hash"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña incorrecta. (Demo: 'onest2026')",
            )

    token = create_session_token(user)

    return LoginResponse(
        access_token=token,
        token_type="Bearer",
        expires_in_seconds=86400,
        user=UserProfileResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"].value,
            title=user["title"],
            area=user.get("area", "Sistemas"),
            department=user["department"],
            avatar_initials=user["avatar_initials"],
        ),
    )


@auth_router.get("/demo-users")
async def get_demo_users():
    """Retorna los 7 perfiles oficiales de Administradores de Sistemas para inicio de sesión en un clic."""
    return [
        {
            "email": u["email"],
            "name": u["name"],
            "role": u["role"].value,
            "title": u["title"],
            "area": u.get("area", "Sistemas"),
            "department": u["department"],
            "avatar_initials": u["avatar_initials"],
        }
        for u in OFFICIAL_ADMINS.values()
    ]


@auth_router.post("/logout")
async def logout(payload: dict):
    token = payload.get("token")
    if token and token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
    return {"message": "Sesión finalizada exitosamente."}

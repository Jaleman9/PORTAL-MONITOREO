from enum import Enum
from typing import List, Optional
# pyrefly: ignore [missing-import]
from fastapi import Depends, Header, HTTPException, Query, status
from pydantic import BaseModel


class UserRole(str, Enum):
    EJECUTIVO = "ejecutivo"
    ADMINISTRADOR = "administrador"


class AuthenticatedUser(BaseModel):
    user_id: str
    role: UserRole
    department: str
    name: Optional[str] = "Usuario ONEST"
    email: Optional[str] = None
    title: Optional[str] = "Administrador de Sistemas & TI"
    area: Optional[str] = "Sistemas"


def get_current_user(
    authorization: Optional[str] = Header(default=None, alias="Authorization"),
    x_user_role: Optional[str] = Header(default=None, alias="X-User-Role"),
    x_user_department: Optional[str] = Header(
        default="Corporativo", alias="X-User-Department"
    ),
    x_user_id: Optional[str] = Header(default="usr-intern-01", alias="X-User-Id"),
    role: Optional[str] = Query(
        default=None, description="Fallback de rol para entorno de pruebas/dashboard"
    ),
) -> AuthenticatedUser:
    # 1. Verificar si viene sesión Bearer activa
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        from .auth import ACTIVE_SESSIONS

        if token in ACTIVE_SESSIONS:
            sess = ACTIVE_SESSIONS[token]
            return AuthenticatedUser(
                user_id=sess["user_id"],
                role=sess["role"],
                department=sess.get("department", "Corporativo"),
                name=sess.get("name", "Usuario ONEST"),
                email=sess.get("email"),
                title=sess.get("title", "Administrador de Sistemas & TI"),
                area=sess.get("area", "Sistemas"),
            )

    # 2. Fallback a headers corporativos directos
    raw_role = x_user_role or role
    if not raw_role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida. Falta encabezado corporativo 'X-User-Role' o Token Bearer.",
        )

    normalized_role = raw_role.strip().lower()
    try:
        validated_role = UserRole(normalized_role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Rol '{raw_role}' no autorizado. Roles permitidos en Fase 1: 'ejecutivo', 'administrador'.",
        )

    return AuthenticatedUser(
        user_id=x_user_id or "usr-intern-01",
        role=validated_role,
        department=x_user_department or "Corporativo",
    )


def require_role(allowed_roles: List[UserRole]):
    def role_checker(
        user: AuthenticatedUser = Depends(get_current_user),
    ) -> AuthenticatedUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado para el rol '{user.role.value}'. Se requiere uno de: {[r.value for r in allowed_roles]}",
            )
        return user

    return role_checker

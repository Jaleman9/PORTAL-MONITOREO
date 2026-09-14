import re
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator, ConfigDict


class EventType(str, Enum):
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    PAGE_VIEW = "page_view"
    ERROR = "error"
    CUSTOM = "custom"


class EventProperties(BaseModel):
    model_config = ConfigDict(extra="allow")

    page_path: Optional[str] = Field(default=None, max_length=512)
    page_title: Optional[str] = Field(default=None, max_length=256)
    referrer: Optional[str] = Field(default=None, max_length=512)
    load_time_ms: Optional[float] = Field(default=None, ge=0, le=600000)
    error_message: Optional[str] = Field(default=None, max_length=256)
    error_type: Optional[str] = Field(default=None, max_length=128)
    user_agent: Optional[str] = Field(default=None, max_length=256)
    viewport_width: Optional[int] = Field(default=None, ge=0)
    viewport_height: Optional[int] = Field(default=None, ge=0)

    @field_validator("page_path", mode="before")
    def sanitize_page_path(cls, v: Any) -> Optional[str]:
        if not v or not isinstance(v, str):
            return None
        # Sanitizar URLs: eliminar query string y fragments para prevenir fuga de tokens o emails
        parsed = urlparse(v)
        path = parsed.path if parsed.path else v.split("?")[0].split("#")[0]
        return path[:512]

    @field_validator("error_message", mode="before")
    def sanitize_error_message(cls, v: Any) -> Optional[str]:
        if not v or not isinstance(v, str):
            return None
        # Enmascarar posibles emails o números largos en mensajes de error
        sanitized = re.sub(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "[EMAIL_REDACTED]", v
        )
        sanitized = re.sub(r"\b\d{8,16}\b", "[ID_REDACTED]", sanitized)
        return sanitized[:256]


class IncomingEvent(BaseModel):
    """Evento tal como es enviado por el SDK Web."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    app_id: str = Field(..., min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    session_id: str = Field(
        ..., min_length=8, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$"
    )
    user_id: Optional[str] = Field(default=None, max_length=128)
    event_type: EventType
    platform: str = Field(default="web", pattern=r"^web$")
    role: str = Field(default="guest", max_length=64)
    department: str = Field(default="unknown", max_length=64)
    properties: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_id", mode="before")
    def ensure_event_id(cls, v: Any) -> str:
        if v and isinstance(v, str):
            try:
                UUID(v)
                return v
            except ValueError:
                pass
        return str(uuid4())

    @field_validator("timestamp", mode="before")
    def ensure_timestamp(cls, v: Any) -> datetime:
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except Exception:
                pass
        return datetime.now(timezone.utc)

    @field_validator("properties", mode="before")
    def validate_and_filter_properties(cls, v: Any) -> Dict[str, Any]:
        if not isinstance(v, dict):
            return {}
        # Filtrar claves explícitamente prohibidas para prevenir fuga de datos sensibles
        forbidden_keys = {
            "password",
            "passwd",
            "token",
            "auth",
            "secret",
            "credit_card",
            "cvv",
            "ssn",
            "rut",
            "dni",
            "cedula",
            "form_data",
            "input_value",
            "search_query",
            "message_body",
        }
        filtered: Dict[str, Any] = {}
        for key, val in v.items():
            lower_key = key.lower()
            if any(forbidden in lower_key for forbidden in forbidden_keys):
                continue  # Descartar dato sensible silenciosamente
            if isinstance(val, (str, int, float, bool)):
                filtered[key] = val
        return filtered


class CanonicalEvent(BaseModel):
    """Evento canónico tras enriquecimiento y pseudonimización en el borde."""

    event_id: str
    timestamp: str  # ISO 8601 UTC
    app_id: str
    session_id: str
    user_id_hash: str
    event_type: str
    platform: str = "web"
    role: str
    department: str
    properties: Dict[str, Any]


class EventBatchPayload(BaseModel):
    events: List[IncomingEvent] = Field(..., min_length=1, max_length=500)

import hmac
import hashlib
import os

# Salt secreto cargado por variable de entorno; debe ser rotativo y seguro
DEFAULT_SALT = "corporacion-analytics-secret-salt-latam-2026"
PEPPER_SALT = os.environ.get("ANALYTICS_SALT", DEFAULT_SALT).encode("utf-8")


def pseudonymize_user(user_id: str | None, session_id: str) -> str:
    """
    Aplica HMAC-SHA256 en el borde para garantizar pseudonimización unidireccional consistente.
    Si el user_id está ausente (visitante no autenticado), se deriva un hash basado en session_id
    con prefijo especial 'anon_'.
    El valor en texto plano nunca se conserva ni se transmite hacia RabbitMQ o ClickHouse.
    """
    if not user_id or user_id.strip() == "":
        source = f"anon:{session_id}".encode("utf-8")
    else:
        source = user_id.strip().lower().encode("utf-8")

    h = hmac.new(PEPPER_SALT, source, hashlib.sha256)
    return h.hexdigest()

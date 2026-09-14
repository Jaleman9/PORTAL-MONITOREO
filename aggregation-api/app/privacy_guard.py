import logging
from typing import Any, Dict, List

logger = logging.getLogger("aggregation.privacy")

# Umbral mínimo no negociable de anonimato para Fase 1
MINIMUM_K_ANONYMITY_THRESHOLD = 5


class PrivacyGuard:
    @staticmethod
    def enforce_threshold(
        data: List[Dict[str, Any]], user_count_key: str = "unique_users"
    ) -> List[Dict[str, Any]]:
        """
        Garantiza que ningún grupo o desglose reporte datos cuando el conteo de usuarios
        únicos sea inferior al umbral mínimo de 5 usuarios.
        Si unique_users < 5:
          - privacy_suppressed: True
          - unique_users se enmascara a None o "< 5"
          - métricas sensibles secundarias se enmascaran
        """
        sanitized = []
        for item in data:
            entry = dict(item)
            count = entry.get(user_count_key, 0)
            if count < MINIMUM_K_ANONYMITY_THRESHOLD:
                logger.info(
                    "Supresión de privacidad aplicada: grupo '%s' tiene solo %d usuarios (umbral >= 5)",
                    entry.get("group_name", entry.get("app_id", "anónimo")),
                    count,
                )
                entry["privacy_suppressed"] = True
                entry["suppression_reason"] = (
                    f"Menos de {MINIMUM_K_ANONYMITY_THRESHOLD} usuarios únicos activos."
                )
                entry[user_count_key] = None
                # Suprimir métricas derivadas que permitan inferencia inversa
                if "total_sessions" in entry:
                    entry["total_sessions"] = None
                if "total_page_views" in entry:
                    entry["total_page_views"] = None
            else:
                entry["privacy_suppressed"] = False
            sanitized.append(entry)
        return sanitized

    @staticmethod
    def is_safe(unique_users: int) -> bool:
        return unique_users >= MINIMUM_K_ANONYMITY_THRESHOLD

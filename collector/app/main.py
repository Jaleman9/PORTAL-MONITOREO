import logging
import os
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .pseudonymizer import pseudonymize_user
from .queue_producer import queue_producer
from .validator import CanonicalEvent, EventBatchPayload, IncomingEvent

# Configuración de Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("collector.api")

# Métricas internas en memoria para observabilidad
METRICS = {
    "batches_received": 0,
    "events_received": 0,
    "events_accepted": 0,
    "events_rejected": 0,
    "start_time": time.time(),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando Collector Service...")
    queue_producer.connect()
    yield
    logger.info("Deteniendo Collector Service...")
    queue_producer.close()


app = FastAPI(
    title="Internal Web Telemetry Collector",
    description="Servicio de ingesta y pseudonimización en el borde para eventos de adopción web",
    version="1.0.0",
    lifespan=lifespan,
)

# Permitir CORS para permitir envíos desde las 20+ aplicaciones web internas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
async def health_check():
    rabbitmq_status = (
        "connected"
        if (queue_producer.channel and not queue_producer.channel.is_closed)
        else "disconnected/fallback"
    )
    return {
        "status": "healthy",
        "service": "collector",
        "rabbitmq": rabbitmq_status,
        "fallback_buffer_size": len(queue_producer.fallback_buffer),
        "uptime_seconds": round(time.time() - METRICS["start_time"], 2),
    }


@app.get("/metrics", tags=["Observability"])
async def get_metrics():
    return {
        **METRICS,
        "fallback_buffer_size": len(queue_producer.fallback_buffer),
        "acceptance_rate": (
            round(METRICS["events_accepted"] / METRICS["events_received"] * 100, 2)
            if METRICS["events_received"] > 0
            else 100.0
        ),
    }


@app.post("/api/v1/events", status_code=status.HTTP_202_ACCEPTED, tags=["Ingestion"])
async def ingest_events(payload: EventBatchPayload, request: Request):
    METRICS["batches_received"] += 1
    total_in_batch = len(payload.events)
    METRICS["events_received"] += total_in_batch

    accepted_events = []
    rejected_count = 0

    for item in payload.events:
        try:
            # 1. Pseudonimización estricta en el borde
            user_hash = pseudonymize_user(item.user_id, item.session_id)

            # 2. Construcción del evento canónico (user_id en texto plano NUNCA se conserva)
            canonical = CanonicalEvent(
                event_id=item.event_id,
                timestamp=item.timestamp.isoformat(),
                app_id=item.app_id,
                session_id=item.session_id,
                user_id_hash=user_hash,
                event_type=item.event_type.value,
                platform="web",
                role=item.role,
                department=item.department,
                properties=item.properties,
            )
            accepted_events.append(canonical.model_dump())
        except Exception as exc:
            logger.warning(
                "Evento descartado por falla de validación o transformación: %s", exc
            )
            rejected_count += 1

    METRICS["events_accepted"] += len(accepted_events)
    METRICS["events_rejected"] += rejected_count

    if rejected_count > 0:
        logger.warning(
            "Alerta de esquema: %d eventos mal formados rechazados en lote de %d",
            rejected_count,
            total_in_batch,
        )

    # 3. Publicación hacia la cola de RabbitMQ
    published = queue_producer.publish_batch(accepted_events)

    return {
        "status": "accepted",
        "received": total_in_batch,
        "accepted": len(accepted_events),
        "rejected": rejected_count,
        "queued": published,
    }

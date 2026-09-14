import json
import logging
import os
import time
from typing import List
import pika

logger = logging.getLogger("collector.queue")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")
EXCHANGE_NAME = "telemetry.events"
QUEUE_NAME = "events.raw"
ROUTING_KEY = "events.web"


class QueueProducer:
    def __init__(self) -> None:
        self.connection: pika.BlockingConnection | None = None
        self.channel: pika.adapters.blocking_connection.BlockingChannel | None = None
        self.fallback_buffer: List[dict] = []
        self.max_buffer_size = 5000
        self.last_connect_attempt: float = 0.0
        self.connect_cooldown: float = 5.0

    def connect(self) -> bool:
        now = time.time()
        if now - self.last_connect_attempt < self.connect_cooldown:
            return False
        self.last_connect_attempt = now

        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials,
                connection_attempts=1,
                retry_delay=1,
                socket_timeout=1,
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.exchange_declare(
                exchange=EXCHANGE_NAME, exchange_type="direct", durable=True
            )
            self.channel.queue_declare(queue=QUEUE_NAME, durable=True)
            self.channel.queue_bind(
                queue=QUEUE_NAME, exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY
            )
            logger.info(
                "Conectado exitosamente a RabbitMQ (%s:%s)",
                RABBITMQ_HOST,
                RABBITMQ_PORT,
            )
            self._flush_fallback_buffer()
            return True
        except Exception as exc:
            logger.warning(
                "No se pudo conectar a RabbitMQ: %s. Operando con buffer en memoria.",
                exc,
            )
            self.connection = None
            self.channel = None
            return False

    def _flush_fallback_buffer(self) -> None:
        if not self.fallback_buffer or not self.channel:
            return
        logger.info(
            "Vaciando %d eventos acumulados en buffer hacia RabbitMQ",
            len(self.fallback_buffer),
        )
        to_send = list(self.fallback_buffer)
        self.fallback_buffer.clear()
        for evt in to_send:
            self.publish(evt)

    def publish(self, event_dict: dict) -> bool:
        body = json.dumps(event_dict)
        if not self.channel or self.channel.is_closed:
            if not self.connect():
                if len(self.fallback_buffer) < self.max_buffer_size:
                    self.fallback_buffer.append(event_dict)
                    return True
                else:
                    logger.error(
                        "Buffer de contingencia lleno. Descartando evento para proteger memoria."
                    )
                    return False

        try:
            self.channel.basic_publish(
                exchange=EXCHANGE_NAME,
                routing_key=ROUTING_KEY,
                body=body,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensaje persistente en disco
                    content_type="application/json",
                ),
            )
            return True
        except Exception as exc:
            logger.warning(
                "Error publicando en RabbitMQ: %s. Almacenando en fallback.", exc
            )
            self.connection = None
            self.channel = None
            if len(self.fallback_buffer) < self.max_buffer_size:
                self.fallback_buffer.append(event_dict)
            return True

    def publish_batch(self, events: List[dict]) -> int:
        published_count = 0
        for evt in events:
            if self.publish(evt):
                published_count += 1
        return published_count

    def close(self) -> None:
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
        except Exception:
            pass


queue_producer = QueueProducer()

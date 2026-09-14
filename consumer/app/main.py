import json
import logging
import os
import signal
import sys
import time
from typing import List, Tuple
import pika

from .clickhouse_client import clickhouse_pipeline

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("consumer.worker")

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")
QUEUE_NAME = "events.raw"

BATCH_SIZE = int(os.environ.get("CONSUMER_BATCH_SIZE", "100"))
BATCH_TIMEOUT_SECONDS = float(os.environ.get("CONSUMER_BATCH_TIMEOUT", "1.5"))


class TelemetryConsumer:
    def __init__(self) -> None:
        self.running = True
        self.connection: pika.BlockingConnection | None = None
        self.channel: pika.adapters.blocking_connection.BlockingChannel | None = None
        self.current_batch: List[dict] = []
        self.delivery_tags: List[int] = []
        self.last_flush_time = time.time()

    def stop(self, *args) -> None:
        logger.info("Señal de parada recibida. Vaciando lote pendiente...")
        self.running = False
        self.flush()
        if self.connection and not self.connection.is_closed:
            self.connection.close()
        sys.exit(0)

    def connect(self) -> bool:
        retries = 15
        for i in range(retries):
            try:
                credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
                parameters = pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials,
                    connection_attempts=3,
                    retry_delay=2,
                    socket_timeout=10,
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=QUEUE_NAME, durable=True)
                self.channel.basic_qos(prefetch_count=BATCH_SIZE * 2)
                logger.info(
                    "Consumidor conectado a RabbitMQ en %s:%s",
                    RABBITMQ_HOST,
                    RABBITMQ_PORT,
                )
                return True
            except Exception as exc:
                logger.warning(
                    "RabbitMQ no disponible aún (intento %d/%d): %s",
                    i + 1,
                    retries,
                    exc,
                )
                time.sleep(3)
        return False

    def flush(self) -> None:
        if not self.current_batch:
            return

        success = clickhouse_pipeline.insert_events_batch(self.current_batch)
        if success:
            for tag in self.delivery_tags:
                try:
                    self.channel.basic_ack(delivery_tag=tag)
                except Exception as exc:
                    logger.warning("Error confirmando tag %s: %s", tag, exc)
            logger.info("Confirmados %d eventos a RabbitMQ", len(self.current_batch))
            self.current_batch.clear()
            self.delivery_tags.clear()
            self.last_flush_time = time.time()
        else:
            logger.error(
                "Fallo al insertar en ClickHouse. Los mensajes se conservan para reintento."
            )

    def run(self) -> None:
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        # 1. Conectar a ClickHouse
        if not clickhouse_pipeline.connect():
            logger.error("No se pudo establecer conexión con ClickHouse. Abortando.")
            sys.exit(1)

        # 2. Conectar a RabbitMQ
        if not self.connect():
            logger.error("No se pudo establecer conexión con RabbitMQ. Abortando.")
            sys.exit(1)

        logger.info("Iniciando bucle de consumo de eventos...")

        while self.running:
            try:
                method_frame, header_frame, body = self.channel.basic_get(
                    queue=QUEUE_NAME, auto_ack=False
                )
                if method_frame:
                    event = json.loads(body.decode("utf-8"))
                    self.current_batch.append(event)
                    self.delivery_tags.append(method_frame.delivery_tag)

                    if len(self.current_batch) >= BATCH_SIZE:
                        self.flush()
                else:
                    # Si no hay mensajes, verificar si el tiempo límite expiró para vaciar lote parcial
                    if (
                        self.current_batch
                        and (time.time() - self.last_flush_time)
                        >= BATCH_TIMEOUT_SECONDS
                    ):
                        self.flush()
                    time.sleep(0.1)
            except pika.exceptions.AMQPConnectionError:
                logger.warning("Conexión perdida con RabbitMQ. Reconectando...")
                time.sleep(3)
                self.connect()
            except Exception as exc:
                logger.error("Error inesperado en ciclo de consumo: %s", exc)
                time.sleep(1)


if __name__ == "__main__":
    consumer = TelemetryConsumer()
    consumer.run()

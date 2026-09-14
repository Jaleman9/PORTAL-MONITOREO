import json
import logging
import os
import time
from typing import Any, Dict, List
import clickhouse_connect

logger = logging.getLogger("consumer.clickhouse")

CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DB = os.environ.get("CLICKHOUSE_DB", "analytics")


class ClickHousePipeline:
    def __init__(self) -> None:
        self.client = None

    def connect(self) -> bool:
        retries = 10
        for i in range(retries):
            try:
                self.client = clickhouse_connect.get_client(
                    host=CLICKHOUSE_HOST,
                    port=CLICKHOUSE_PORT,
                    username=CLICKHOUSE_USER,
                    password=CLICKHOUSE_PASSWORD,
                    connect_timeout=5,
                    send_receive_timeout=15,
                )
                logger.info(
                    "Conectado a ClickHouse en %s:%s", CLICKHOUSE_HOST, CLICKHOUSE_PORT
                )
                self.init_schema()
                return True
            except Exception as exc:
                logger.warning(
                    "ClickHouse no disponible aún (intento %d/%d): %s",
                    i + 1,
                    retries,
                    exc,
                )
                time.sleep(3)
        return False

    def init_schema(self) -> None:
        if not self.client:
            return
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        if os.path.exists(schema_path):
            with open(schema_path, "r", encoding="utf-8") as f:
                ddl = f.read()
            for statement in ddl.split(";"):
                stmt = statement.strip()
                if stmt:
                    self.client.command(stmt)
            logger.info("Esquema DDL inicializado en ClickHouse")

    def insert_events_batch(self, events: List[Dict[str, Any]]) -> bool:
        if not events or not self.client:
            return False

        columns = [
            "event_id",
            "timestamp",
            "app_id",
            "session_id",
            "user_id_hash",
            "event_type",
            "platform",
            "role",
            "department",
            "page_path",
            "page_title",
            "referrer",
            "load_time_ms",
            "error_message",
            "error_type",
            "properties_json",
        ]

        rows = []
        for e in events:
            props = e.get("properties", {})
            rows.append(
                [
                    e.get("event_id"),
                    e.get("timestamp"),
                    e.get("app_id"),
                    e.get("session_id"),
                    e.get("user_id_hash"),
                    e.get("event_type"),
                    e.get("platform", "web"),
                    e.get("role", "guest"),
                    e.get("department", "unknown"),
                    props.get("page_path", ""),
                    props.get("page_title", ""),
                    props.get("referrer", ""),
                    float(props.get("load_time_ms", 0.0) or 0.0),
                    props.get("error_message", ""),
                    props.get("error_type", ""),
                    json.dumps(props),
                ]
            )

        try:
            self.client.insert("analytics.events", rows, column_names=columns)
            logger.info("Lote de %d eventos insertado en ClickHouse", len(rows))
            return True
        except Exception as exc:
            logger.error("Error insertando lote en ClickHouse: %s", exc)
            return False


clickhouse_pipeline = ClickHousePipeline()

-- Base de datos de analítica
CREATE DATABASE IF NOT EXISTS analytics;

-- Tabla canónica de eventos crudos
-- Motor MergeTree particionado por mes con TTL de 90 días para estricta minimización de datos
CREATE TABLE IF NOT EXISTS analytics.events (
    event_id UUID,
    timestamp DateTime64(3, 'UTC'),
    event_date Date MATERIALIZED toDate(timestamp),
    app_id LowCardinality(String),
    session_id String,
    user_id_hash FixedString(64),
    event_type LowCardinality(String),
    platform LowCardinality(String) DEFAULT 'web',
    role LowCardinality(String) DEFAULT 'guest',
    department LowCardinality(String) DEFAULT 'unknown',
    page_path String DEFAULT '',
    page_title String DEFAULT '',
    referrer String DEFAULT '',
    load_time_ms Float64 DEFAULT 0.0,
    error_message String DEFAULT '',
    error_type LowCardinality(String) DEFAULT '',
    properties_json String DEFAULT '{}',
    created_at DateTime64(3, 'UTC') DEFAULT now64()
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (app_id, event_type, event_date, user_id_hash, timestamp)
TTL event_date + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;

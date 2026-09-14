# Guía de Ejecución, Formateo y Subida a Git

Este documento describe el estado del proyecto, cómo ejecutarlo, formatear el código y cómo subirlo a un repositorio remoto (GitHub/GitLab).

---

## 1. Estado Actual de la Plataforma

Los servicios se encuentran actualmente activos y validados:

| Servicio / Recurso | Dirección / Puerto | Estado | Descripción |
| :--- | :--- | :--- | :--- |
| **RabbitMQ (Broker)** | `localhost:5672` (AMQP)<br>`http://localhost:15672` (Web UI) | 🟢 Activo | Cola de eventos (usuario: `guest`, contraseña: `guest`) |
| **ClickHouse (OLAP)** | `http://localhost:8123` (HTTP)<br>`localhost:9009` (Nativo) | 🟢 Activo | Base de datos analítica columnar |
| **Collector Service** | `http://localhost:8000` | 🟢 Activo | API FastAPI de ingesta y pseudonimización HMAC-SHA256 |
| **Consumer Worker** | Proceso en segundo plano | 🟢 Activo | Consume de RabbitMQ e inserta en micro-lotes en ClickHouse |
| **Aggregation API & Dashboard** | `http://localhost:8001/` | 🟢 Activo | Dashboard Ejecutivo y API de métricas k-anonymity |

### Endpoints de Verificación Rápida
- **Salud del Collector:** `GET http://localhost:8000/health`
- **Métricas del Collector:** `GET http://localhost:8000/metrics`
- **Salud de la Aggregation API:** `GET http://localhost:8001/health`
- **Dashboard Web Ejecutivo:** [http://localhost:8001/](http://localhost:8001/)

---

## 2. Cómo Correr la Plataforma Localmente

Si en algún momento detienes los servicios o reinicias el equipo, puedes arrancarlos con estos comandos:

### Paso 2.1: Iniciar Contenedores de Base de Datos y Mensajería
```powershell
docker compose up -d rabbitmq clickhouse
```

### Paso 2.2: Iniciar los Microservicios de Python
Abre terminales independientes o ejecútalos en segundo plano:

```powershell
# Terminal 1 - Collector (Ingesta)
uvicorn collector.app.main:app --host 0.0.0.0 --port 8000

# Terminal 2 - Consumer (Worker RabbitMQ -> ClickHouse)
python -m consumer.app.main

# Terminal 3 - Aggregation API & Dashboard Frontend
uvicorn app.main:app --app-dir aggregation-api --host 0.0.0.0 --port 8001
```

---

## 3. Pruebas y Validación Automática

Para ejecutar toda la suite de pruebas unitarias y de integración de extremo a extremo (E2E):

```powershell
python -m pytest
```

> **Resultado actual:** `12 passed in ~6.0s` (Collector, Aggregation RBAC, k-anonymity, y E2E pipeline completo).

---

## 4. Cómo Darle Formato al Código

El proyecto utiliza **Ruff** (un formateador ultra-rápido compatible con Black):

```powershell
uvx ruff format .
```

Para verificar si hay errores de sintaxis o estilo sin modificar archivos:
```powershell
uvx ruff check .
```

---

## 5. Cómo Subir el Proyecto a GitHub / Repositorio Remoto

Sigue estos pasos desde PowerShell en la raíz del proyecto:

### 1. Inicializar el repositorio Git
```powershell
git init
```

### 2. Agregar los archivos al área de preparación (staging)
El archivo `.gitignore` ya está configurado para omitir cachés y entornos virtuales.
```powershell
git add .
```

### 3. Crear el primer commit
```powershell
git commit -m "feat: inicializacion de plataforma web-analytics-platform con pipelines e2e y dashboard"
```

### 4. Renombrar la rama principal a `main` (recomendado)
```powershell
git branch -M main
```

### 5. Vincular tu repositorio remoto de GitHub
Reemplaza `<TU_URL_DE_GITHUB>` por la URL de tu repositorio (ej. `https://github.com/tu-usuario/web-analytics-platform.git`):
```powershell
git remote add origin <TU_URL_DE_GITHUB>
```

### 6. Subir tus cambios
```powershell
git push -u origin main
```

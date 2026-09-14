# Política de Privacidad y Minimización de Datos (Fase 1 - MVP)

## 1. Principios Rectores
1. **Minimización de Datos:** Solo se recolecta la telemetría estrictamente necesaria para medir adopción, uso y estabilidad técnica de las aplicaciones internas.
2. **Pseudonimización en el Borde:** El identificador real del usuario (`user_id` corporativo, ej. email, nómina o rut) es transformado en el Collector mediante `HMAC-SHA256(user_id, SECRET_SALT)`. El hash resultante es unidireccional y consistente. El almacén analítico (ClickHouse) **NUNCA** almacena ni recibe el `user_id` en texto plano.
3. **Mapeo Inverso Prohibido:** La tabla de equivalencia entre `user_id` real y `user_id_hash` no existe en la plataforma de analítica ni en el Collector.
4. **Agregación Obligatoria (k-Anonymity):** Toda métrica expuesta a través de la Aggregation API o visualizada en el Dashboard Ejecutivo debe agrupar como mínimo a **5 usuarios únicos** (umbral `k >= 5`). Grupos con menor número de usuarios se reportan como suprimidos (`privacy_suppressed`).
5. **Retención de Datos:** 
   - Eventos crudos en ClickHouse: Retención máxima de **90 días** (gobernado por particiones `TTL timestamp + INTERVAL 90 DAY`).
   - Posteriormente, los datos se consolidan en tablas de agregación diaria/mensual irreversibles sin `user_id_hash`.

---

## 2. Lo que SÍ se recolecta
- `event_id`: UUIDv4 único por evento.
- `timestamp`: Fecha y hora UTC del evento.
- `app_id`: Código de la aplicación interna (ej. `crm-portal`, `erp-web`).
- `session_id`: UUID de sesión efímera que caduca tras 30 minutos de inactividad.
- `user_id_hash`: Hash consistente de 64 caracteres hexadecimales.
- `event_type`: `session_start`, `session_end`, `page_view`, `error`, `custom`.
- `platform`: `web`.
- `role`: Rol funcional corporativo (ej. `analista`, `supervisor`, `gerente`).
- `department`: Área de la organización (ej. `operaciones`, `finanzas`, `comercial`).
- Metadatos de interacción técnica:
  - Ruta de página sanitizada (`/ventas/reporte` — sin query parameters personales).
  - Título de página (`Reporte de Ventas`).
  - Tiempos de carga en ms (Performance Navigation Timing).
  - Errores de JS (tipo de error y mensaje técnico sanitizado).
  - Características del entorno: User-Agent genérico, resolución de viewport.

---

## 3. Lo que NUNCA se recolecta (Estrictamente Prohibido)
- ❌ **Contenido de formularios:** Valores de inputs de texto, select, checkboxes, textareas.
- ❌ **Datos de autenticación o credenciales:** Contraseñas, tokens JWT, headers Authorization, cookies de sesión externa.
- ❌ **Texto libre:** Búsquedas del usuario, mensajes de chat, notas, descripciones.
- ❌ **Parámetros URL sensibles:** Query strings que contengan tokens, correos, nombres, DNI o identificadores personales (el SDK sanitiza la URL antes de enviar).
- ❌ **Datos personales directos:** Nombres y apellidos, correos electrónicos, teléfonos, direcciones físicas o IP públicas completas.

# Prompt para Antigravity — Rediseño visual del Dashboard ONEST Logistics

Copia y pega el siguiente prompt completo en Antigravity.

---

## PROMPT

Trabaja sobre el proyecto en `C:\Users\josea\.gemini\antigravity\scratch\web-analytics-platform`. Es una plataforma de telemetría web B2B para ONEST Logistics. El archivo principal a editar es `dashboard/index.html` — un único archivo HTML autocontenido que carga React 18 (UMD, sin JSX, usa `React.createElement`), Tailwind CSS vía Play CDN (sin `tailwind.config.js` real) y Chart.js, todo por `<script>` tags sin bundler ni build step. No hay `package.json` ni proceso de compilación: los cambios se editan directamente en ese HTML y se ven recargando el navegador.

Antes de tocar nada, lee `ONEST_DIGITAL_DESIGN_SYSTEM.md` en la raíz del proyecto — es la fuente de verdad del sistema de diseño (paleta 70/20/10, tipografía, spacing, radios, componentes Bento Grid). El objetivo es una **evolución del mismo lenguaje visual** (Bento Grid corporativo azul/blanco estilo Stripe/Linear), no una ruptura de estilo. Nada de glassmorphism pesado, degradados neón ni sombras difusas irreales — mantener el acabado mate de interfaces de ingeniería de precisión que ya define el design system.

### Contexto de negocio
El dashboard muestra: 4 KPIs (DAU, MAU, tasa de error, portales activos), curva de adopción de 14 días, ranking de portales con badge de cumplimiento `k-Anonymity k>=5`, salud técnica de 3 servicios (Collector, Queue, Engine), y eficiencia de licencias (cuentas inactivas >30 días). Además tiene pestañas de Detalle de Portales, Telemetría en Vivo, Rendimiento SLA y Gobernanza de Privacidad.

### Hallazgos actuales que hay que corregir

1. **Tipografía ausente**: `dashboard/index.html` usa la pila de fuente del sistema (`-apple-system, Segoe UI...`) y NO carga Montserrat/Inter vía Google Fonts, aunque el design system las exige (Montserrat SemiBold para títulos, Inter para datos/tablas con figuras tabulares). El archivo hermano `demo-portal/index.html` sí las carga correctamente — úsalo como referencia exacta del `<link>` y la config de Tailwind (`font-sans: Inter`, `font-heading: Montserrat`).

2. **Tokens de color incompletos**: el bloque `<style>` de `dashboard/index.html` (líneas ~18-32) solo define `--onest-blue-900/700/500/100`, `--onest-green-700/500/100` y unos pocos neutros. Faltan respecto al design system: la escala de grises completa, los semánticos `--success/warning/danger/info`, y `--radius-sm/md/lg`. Además el color se usa mayormente hardcodeado como clases arbitrarias de Tailwind (`bg-[#003E75]`) repetidas por todo el archivo en vez de clases reutilizables — consolídalo.

3. **Funcionalidad "fantasma" sin UI**: el estado `healthSummary` (salud de Collector/Queue/Engine, viene del endpoint `health-traffic-light`) y `idleMetrics` (cuentas inactivas) ya se obtienen del backend y se pasan como props a los componentes, pero **nunca se renderizan** en ningún JSX. Hay que activarlos visualmente (ver requerimientos abajo).

4. **Navegación por tabs en vez de sidebar**: el design system especifica un sidebar vertical de 240px (Dashboard, Portales Web, Telemetría Live, Rendimiento SLA, Privacidad), pero la implementación actual usa tabs horizontales dentro de `App()`. Hay que migrar a sidebar.

5. **Gráficos inconsistentes**: las barras de "compatibilidad de navegadores" en `PortalsDetailTab()` están hechas a mano con `<div>` y `width: %` en vez de usar Chart.js como el resto de los gráficos (línea de tendencia, barras horarias, doughnut de dispositivos). Unifícalo a Chart.js.

6. **Selector de fecha rudimentario**: hoy son 4 botones fijos (7/14/30/90 días) sin jerarquía visual clara. Mejorar el componente visualmente (pill group con mejor contraste de estado activo) sin construir un date-picker de rango arbitrario — eso está fuera de alcance.

### Requerimientos de la nueva versión

**A. Base tipográfica y de tokens**
- Cargar `Inter` (400/500/600/700) y `Montserrat` (600/700/800) vía Google Fonts, igual que en `demo-portal/index.html`.
- Completar en `:root` las variables CSS faltantes del design system: escala de grises `--gray-950` a `--gray-50`, semánticos `--success/--warning/--danger/--info`, y `--radius-sm/md/lg`.
- Reemplazar los `bg-[#hex]` arbitrarios repetidos por clases basadas en las variables CSS ya definidas (o utilidades Tailwind custom vía `tailwind.config` inline si el Play CDN lo permite).
- Mantener la regla 70/20/10: 70% neutros, 20% azul corporativo, 10% verde acento — el verde solo debe significar "saludable / cumplimiento OK", nunca decorativo.

**B. Sidebar vertical (240px)**
- Reemplaza los tabs horizontales actuales de `App()`.
- Logo "O" + branding ONEST arriba, fondo azul corporativo `#003E75`.
- Ítems: Dashboard, Portales Web, Telemetría Live, Rendimiento SLA, Privacidad — con estado activo resaltado en `#00549E` y el resto en opacidad reducida.
- El header superior queda liberado para: breadcrumb, selector de rango de fechas (pill group mejorado), pulse de salud global (ver C), y perfil de usuario en 1-clic (ya existe, mantenerlo).
- Debe verse bien en viewport de escritorio típico (1440px+); no es prioritario el responsive mobile para esta fase.

**C. Pulse de salud técnica en el header**
- Un indicador compacto en el header (punto animado + texto corto, ej. "● Todo operativo" en verde o "● Atención requerida" en ámbar) que resume el peor estado entre Collector, Queue y Engine usando los datos de `healthSummary` que ya llegan al frontend.
- Al hacer hover o clic, un popover/dropdown muestra el detalle de los 3 servicios individualmente, cada uno con su punto de color semántico (verde=óptimo, ámbar=atención, rojo=crítico, gris=desconocido) y nombre.
- No crear una tarjeta Bento separada en Overview para esto — va integrado en el header, como se definió.

**D. Modo oscuro automático por horario**
- Sin botón de toggle manual. Detectar la hora local del cliente y aplicar automáticamente un tema oscuro cuando la hora esté dentro de una ventana configurable (variable en el código, por defecto 20:00–06:00), pensado para turnos NOC.
- Definir una segunda paleta de superficies oscuras (ej. fondo `#0B1220`, superficie `#1B2A41`) manteniendo el azul y verde de marca con saturación ajustada para buen contraste sobre fondo oscuro (no reutilizar los mismos hex del modo claro sin ajuste).
- Aplicar como clase `dark` en `<html>` o `<body>`, con las reglas CSS correspondientes ya presentes en el `<style>` embebido.
- Revisar el estado cada pocos minutos (o al reenfocar la pestaña) para que el cambio ocurra sin necesitar recargar la página si el usuario deja la sesión abierta cruzando el horario límite.

**E. Activar datos ya disponibles**
- Renderizar `idleMetrics` (cuentas inactivas >30 días) en su tarjeta correspondiente dentro de la pestaña de Gobernanza — el dato ya llega, solo falta el JSX.

**F. Unificación de gráficos**
- Reemplazar las barras de navegador hechas a mano en `PortalsDetailTab()` por un gráfico de barras horizontal de Chart.js, con el mismo estilo visual (colores, tooltips, radios) que el resto de los charts del dashboard.

**G. Nueva vista: Actividad detallada por usuario (dentro de "Portales Web")**

Agregar, como sub-vista o tab interno dentro de `PortalsDetailTab()` (junto a lo que ya existe de dispositivos/navegadores/horario), una tabla dinámica de actividad por usuario individual con estas características:

- **Columnas**: identificador de usuario, portal, número de sesiones, páginas vistas, última actividad (relativa, ej. "hace 2h"), tendencia (↑/↓/= vs. periodo anterior).
- **Identidad del usuario**: usar un identificador seudónimo tipo `USR-XXXX` (hash corto derivado del `user_id` real, fuente tipográfica monoespaciada para diferenciarlo visualmente de texto normal) — **nunca** mostrar nombre ni email real. Esto es intencional: preserva el principio de privacy-by-design que ya aplica `PrivacyGuard` en el backend (`aggregation-api/app/privacy_guard.py`), que existe específicamente para evitar exponer identidad individual cuando no hay masa crítica de usuarios (`k-anonymity >= 5`). No construyas ni sugieras un mecanismo para revelar identidad real en esta fase — quedó fuera de alcance a propósito.
- **Búsqueda y ordenamiento**: campo de búsqueda por identificador de usuario o portal; encabezados de columna clicables para ordenar ascendente/descendente (por sesiones, por última actividad, etc.).
- **Filtros interactivos**: selector de portal (o "todos"), y el mismo selector de rango de fechas del header (7/14/30/90 días) debe afectar también esta tabla — la vista se recalcula al cambiar el filtro sin recargar la página.
- **Auto-refresh**: polling periódico (cada 15-30s, similar al patrón ya usado en `LiveTelemetryTab()` con su intervalo de 3s, pero más espaciado porque esto no es telemetría cruda) para mantener sesiones y última actividad actualizadas sin que el usuario tenga que recargar.
- **Drill-down**: al hacer clic en una fila, expandir inline (o abrir un panel lateral) con el detalle de ese usuario seudónimo: gráfico simple de sesiones en el tiempo, lista de páginas más visitadas, y dispositivos/navegadores usados — reutilizando componentes de gráfico ya existentes en Chart.js donde aplique.
- Si el endpoint de backend para este detalle por usuario no existe todavía en `aggregation-api/app/`, genera datos mock realistas en el frontend (siguiendo el mismo patrón de datos de ejemplo que ya use el resto del dashboard) y dilo explícitamente en tu resumen final, para conectar el endpoint real después.

### Restricciones explícitas (no hacer)
- No agregar un date-picker de rango arbitrario con calendario — mantener el pill group de rangos fijos, solo mejorado visualmente.
- No construir un sistema de notificaciones push en tiempo real — no hay backend para eso en esta fase.
- No agregar toggle manual de modo oscuro — es automático por horario únicamente.
- No migrar el proyecto a Next.js/React con build tooling — debe seguir funcionando como HTML autocontenido sin bundler, editado directamente.
- No introducir glassmorphism, degradados vistosos ni sombras difusas — mantener el acabado sobrio de ingeniería de precisión.
- No mostrar nombre real, email ni ningún dato que permita identificar a una persona física en la vista de actividad por usuario — solo el identificador seudónimo `USR-XXXX`.

### Criterio de aceptación
Al abrir `dashboard/index.html` en el navegador (sirviéndolo con cualquier servidor estático simple, ej. `python -m http.server`), se debe ver: sidebar vertical funcional con navegación entre las 5 secciones, header con pulse de salud interactivo, tipografía Montserrat/Inter aplicada correctamente, paleta de colores consistente sin hex arbitrarios sueltos, cuentas inactivas visibles en Gobernanza, gráfico de navegadores usando Chart.js, tema oscuro activándose automáticamente si la hora del sistema cae dentro de la ventana nocturna configurada, y dentro de "Portales Web" una tabla de actividad por usuario (seudónima) con búsqueda, ordenamiento, filtros por portal/rango de fechas, auto-refresh y drill-down funcional al hacer clic en una fila.

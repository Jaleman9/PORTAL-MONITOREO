# Sistema de Diseño ONEST — Guía de Homologación
**17 sep 2026 · @José Alemán**

---

## 1. Objetivo y alcance

Esta guía documenta el **Onest Digital Design System v1.0** tal como quedó implementado en el portal Launcher SSO, para que cualquier equipo pueda replicarlo ("homologarlo") en otros portales web de Onest SmartLogistics sin reinventar la paleta, la tipografía o los patrones de componentes.

Está pensada para quien construye o mantiene un portal interno: desarrolladores frontend que necesitan los tokens y el CSS exacto, y diseñadores que necesitan entender las reglas detrás de las decisiones (por qué se eliminó el verde, por qué hay una sola escala azul, cómo se arma un banner con foto real).

Cubre cuatro capas, de fundamento a patrón visible:
1. Tokens de color y tipografía.
2. Arquitectura de dos hojas de estilo.
3. Componentes base (sidebar, botones, cards, badges).
4. Sistema de identidad fotográfica (`page-banner` / `hero-band`).
5. Checklist de implementación y lista de errores ya detectados.

---

## 2. Principio de marca: una sola escala de color

El cambio de fondo respecto al template original no fue "quitar el verde y poner azul" como retoque cosmético: es una **regla de sistema** que cualquier portal nuevo debe seguir desde el inicio.

Antes existían dos ejes de color (azul "corporativo" + verde "Smart" para éxito/activo), lo que generaba inconsistencias: un mismo estado ("activo") se veía azul en una pantalla y verde en otra, y no había regla clara de cuándo usar cada uno. **Se retiró el verde por completo y todo el sistema —marca, botones, badges, estados— vive ahora sobre una única escala azul (11 pasos, de `--onest-blue-950` a `--onest-blue-50`).**

La jerarquía que antes resolvía el segundo color se resuelve ahora con dos tonos distintos de la misma familia:
* **`--onest-blue-700` (`#00549E`):** Azul primario / marca.
* **`--onest-blue-600` (`#0A6CBE`):** Azul "activo / permitido / éxito". Perceptiblemente distinto en pantalla sin salir de la paleta.

Rojo (error) y ámbar (advertencia) de Bootstrap se conservan intactos a propósito: no deben verse "de marca", porque son señales de estado universales que el usuario ya reconoce.

> **Regla para portales nuevos:** Cero verde, cero colores de marca fuera de la escala azul definida abajo. Si un estado nuevo necesita distinguirse de "activo", se resuelve con otro tono de azul o con texto/ícono, nunca con un color adicional.

---

## 3. Tokens de color

Definidos como CSS custom properties en `onest-skin.css`, bajo el selector `html[data-brand="onest"]`. Un portal nuevo copia este bloque tal cual como punto de partida.

| Token | Hex | Uso recomendado |
| :--- | :--- | :--- |
| `--onest-blue-950` | `#001F3D` | Extremo más oscuro; fondo inferior del degradado del sidebar |
| `--onest-blue-900` | `#003E75` | Sidebar, footer del sidebar, estado `:active` de botón primario |
| `--onest-blue-800` | `#004686` | Texto sobre chips claros (badge "Producción") |
| `--onest-blue-700` | `#00549E` | Azul primario / marca. Botón primario, links, títulos activos, badges bg-primary/bg-info |
| `--onest-blue-600` | `#0A6CBE` | Azul "activo/éxito". Badges `bg-success`, `.status-active`, `.text-success` — nunca verde |
| `--onest-blue-500` | `#1677BD` | Hover de botón primario e info, foco de inputs |
| `--onest-blue-400` | `#3893D2` | Uso puntual en gráficas (series secundarias) |
| `--onest-blue-300` | `#4FA8E0` | Acentos sobre fondo oscuro (punto del eyebrow, borde activo del sidebar) |
| `--onest-blue-200` | `#A9D3EF` | Texto secundario sobre fondo oscuro (eyebrow del hero), hover de bordes de card |
| `--onest-blue-100` | `#EAF3FA` | Fondos de chip/icono suaves |
| `--onest-blue-50` | `#F5FAFD` | Tinte de fondo general (radial-gradient sutil del body) |
| `--onest-gray-950` | `#20252B` | Texto principal |
| `--onest-gray-700` | `#475467` | Texto secundario |
| `--onest-gray-500` | `#667085` | Texto muted, chips neutros (ej. "STAGING") — nunca azul, debe leerse neutral |
| `--onest-gray-300` | `#D0D5DD` | Bordes de inputs y botones secundarios |
| `--onest-gray-200` | `#E1E6EB` | Bordes de cards, headers, footer |
| `--onest-gray-100` | `#F2F4F7` | Fondos hover neutros |
| `--onest-gray-50` | `#F8FAFC` | Fondo general del body |

Rojo y ámbar de Bootstrap (`bg-danger`, `bg-warning`) se dejan sin tocar: son universales de error/advertencia, no colores de marca.

---

## 4. Tipografía, radios y sombras

### Tipografía
* **Montserrat (600/700):** Para títulos y `.main-title`.
* **Inter (400/500/600):** Para el resto del texto y tablas de datos.
* `h1` / `.page-title` se acota a `1.375rem`: el tamaño fluido grande que trae Bootstrap por defecto (~35px) está pensado para landing pages, no para un admin denso.

```html
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&display=swap">
```

### Radios
Escala de 4 pasos reutilizada por todos los componentes (nunca un valor suelto por componente):

| Token | Valor | Uso |
| :--- | :--- | :--- |
| `--onest-radius-sm` | `6px` | nav-links, inputs, chips pequeños |
| `--onest-radius-md` | `8px` | tarjetas de app, iconos |
| `--onest-radius-lg` | `12px` | cards, page-banner |
| `--onest-radius-xl` | `18px` | reservado para elementos grandes |

### Sombras
Escala de 3 pasos con tinte azul (`rgba(0, 62, 117, ...)`):

| Token | Valor |
| :--- | :--- |
| `--onest-shadow-sm` | `0 1px 2px rgba(16, 24, 40, .06)` |
| `--onest-shadow-md` | `0 6px 16px rgba(0, 62, 117, .10)` |
| `--onest-shadow-lg` | `0 16px 40px rgba(0, 62, 117, .18)` |

### Easing
Una sola curva de transición para todo el sistema:
```css
--onest-ease: cubic-bezier(.2, .7, .3, 1);
```

---

## 5. Arquitectura CSS de dos capas

1. **`onest-brand.css`:** Tema corporativo, siempre activo, incluido en el login. Sobrescribe la paleta base con azul usando selectores sin scope (`a`, `.btn-primary`, `:root`).
2. **`onest-skin.css`:** El Design System completo ("ONEST Digital Design System v1.0"). Aplica cuando `<html data-brand="onest">` está presente. Contiene tokens, sidebar oscuro, header translúcido, botones, cards, badges y banners fotográficos.

### Orden de carga exacto:
```html
<link rel="stylesheet" href="assets/css/style.min.css">
<link rel="stylesheet" href="assets/css/onest-brand.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="assets/css/onest-skin.css">
```

---

## 6. Componentes base

* **Sidebar:** Degradado oscuro `linear-gradient(180deg, var(--onest-blue-900) 0%, var(--onest-blue-950) 100%)`. Header del logo en blanco. Link activo con fondo `--onest-blue-700` y barra de acento izquierda de 3px en `--onest-blue-300` (`box-shadow: inset 3px 0 0 ...`).
* **Header:** Translúcido con blur: `background-color: rgba(255,255,255,.92)` + `backdrop-filter: saturate(180%) blur(8px)`.
* **Botones:**
  * `.btn-primary`: Fondo `--onest-blue-700`, hover `--onest-blue-500`, active `--onest-blue-900`.
  * `.btn-info`: Fondo `--onest-blue-600` (acento secundario en la misma escala).
  * `.btn-secondary`: Blanco con borde gris (`--onest-gray-300`) y texto `--onest-gray-700`.
* **Cards:** Radio `12px` (`--onest-radius-lg`), borde `--onest-gray-200`, `--onest-shadow-sm` en reposo. En hover suben a `--onest-shadow-md` y borde `--onest-blue-200`.
* **Tarjetas de aplicación ("Elija aplicación"):** Fondo en degradado azul (135deg, `--onest-blue-500` $\rightarrow$ `--onest-blue-900`).
* **Badges / estados:** `bg-success` y `.status-active` usan `--onest-blue-600` (**nunca verde**). `bg-info`/`bg-primary` usan `--onest-blue-700`. Rojo y ámbar quedan intactos.

---

## 7. Sistema de identidad fotográfica: `.page-banner` y `.hero-band`

Abre cada pantalla admin con fotografía real de la operación (escáner, racks, flota, nave) con degradado azul oscuro (scrim) para legibilidad:

* **`.page-banner`:** Banner bajo (168px, 136px en móvil) para pantallas secundarias con breadcrumb + título.
* **`.hero-band`:** Banner alto (300px, 260px en móvil) para página principal con eyebrow, título, descripción y chips `.hero-stats`.

### Implementación CSS:
```css
html[data-brand="onest"] .page-banner {
    position: relative;
    height: 168px;
    border-radius: var(--onest-radius-lg);
    overflow: hidden;
    margin-bottom: 1.5rem;
    background-size: cover;
    background-position: center;
    box-shadow: var(--onest-shadow-md);
}

html[data-brand="onest"] .page-banner::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(100deg,
        rgba(0, 20, 40, .93) 0%, rgba(0, 31, 61, .78) 34%,
        rgba(0, 31, 61, .30) 68%, rgba(0, 31, 61, .05) 100%);
}

html[data-brand="onest"] .page-banner-content {
    position: relative;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 0 1.75rem;
}

html[data-brand="onest"] .page-banner-title {
    color: #ffffff;
    margin: 0;
    text-shadow: 0 2px 12px rgba(0, 10, 20, .35);
}
```

### Uso en HTML:
```html
<div class="page-banner" style="background-image:url('assets/img/hero/nombre-pagina.jpg')">
  <div class="page-banner-content">
    <ol class="breadcrumb fs-sm mb-1">...</ol>
    <h4 class="main-title page-banner-title">Título de la página</h4>
  </div>
</div>
```

> **Nota crítica:** La imagen de fondo se fija siempre con `style=` inline sobre el elemento, nunca mediante variables CSS (`var(--page-banner-img)`), para evitar que las rutas relativas se resuelvan incorrectamente contra la carpeta CSS en vez del HTML.

---

## 8. Accesibilidad y Checklist de Homologación

1. Copiar `assets/css/onest-brand.css` y `assets/css/onest-skin.css`.
2. Incluir los `<link>` en el orden exacto.
3. Fijar `<html data-brand="onest">` en todas las páginas.
4. Auditar y eliminar cualquier verde o color hardcodeado, reemplazándolo por el token azul correspondiente.
5. Colocar imágenes reales de operación comprimidas (JPEG, calidad 76–78) en `assets/img/hero/`.
6. Envolver encabezados en `.page-banner` o `.hero-band` con `style=` inline.
7. Verificar que no existan textos azules sobre fondos azules ni errores en consola.

---

## 9. Errores comunes a evitar

1. **Texto azul invisible sobre fondo azul:** Proteger enlaces con selectores específicos (`a:not(.btn):not(.app-a)`).
2. **`url()` dentro de variables CSS:** Fijar `background-image` en `style=""` inline en el HTML.
3. **Colores nuevos "solo para este caso":** Usar exclusivamente los 11 tonos de la escala azul.
4. **Reinventar sombras, radios o easing:** Usar siempre los tokens `--onest-shadow-*`, `--onest-radius-*`, `--onest-ease`.
5. **Banner sin scrim:** El degradado `::before` es obligatorio para garantizar contraste WCAG.

# ONEST Digital Design System v1.0

## 1. Objetivo

Definir un estándar visual único para todos los desarrollos digitales de ONEST Logistics, incluyendo:

- Portales internos
- Dashboards
- Sistemas administrativos
- Formularios
- Aplicaciones operativas
- Chatbots
- Plataformas con IA
- Herramientas de seguimiento
- Sistemas de calidad
- Sistemas de RH
- Portales de clientes

El objetivo es que todos los sistemas compartan la misma identidad visual y no parezcan productos independientes.

La línea visual debe transmitir:

**ONEST Digital = Corporativo + Tecnológico + Limpio + Operacional**

---

# 2. Principios de diseño

Todo sistema digital ONEST debe cumplir con los siguientes principios:

1. Utilizar azul ONEST como color corporativo dominante.
2. Utilizar verde ONEST únicamente como color de acento.
3. Mantener fondos predominantemente blancos o grises claros.
4. Evitar interfaces saturadas de color.
5. Priorizar claridad sobre decoración.
6. Mantener consistencia entre todos los componentes.
7. Usar una sola librería de iconos.
8. Utilizar una escala única de espaciados.
9. Evitar estilos arbitrarios definidos directamente en componentes.
10. Mantener diseños modernos, empresariales y orientados a operación.

---

# 3. Distribución de color

Se establece una regla visual aproximada:

- **70 %** fondos blancos, grises claros y superficies neutras.
- **20 %** azul ONEST.
- **10 %** verde ONEST y colores semánticos.

El azul debe dominar visualmente.
El verde debe funcionar como color complementario.

---

# 4. Paleta corporativa

## Colores principales

| Token | Uso | Color |
|---|---|---|
| `onest-primary` | Navegación, botones principales, links | `#00549E` |
| `onest-primary-dark` | Sidebar, footer, hover | `#003E75` |
| `onest-primary-light` | Fondos seleccionados | `#EAF3FA` |
| `onest-green` | Acentos, estados positivos | `#39B54A` |
| `onest-green-dark` | Hover y contraste | `#2B9138` |
| `onest-white` | Fondos | `#FFFFFF` |
| `onest-background` | Fondo general | `#F5F7F9` |
| `onest-surface` | Cards | `#FFFFFF` |
| `onest-text` | Texto principal | `#20252B` |
| `onest-text-secondary` | Texto secundario | `#667085` |
| `onest-border` | Bordes | `#E1E6EB` |

---

# 5. Tokens CSS

```css
:root {

  /* =========================
     ONEST BRAND
  ========================== */

  --onest-blue-900: #003E75;
  --onest-blue-700: #00549E;
  --onest-blue-500: #1677BD;
  --onest-blue-100: #EAF3FA;

  --onest-green-700: #2B9138;
  --onest-green-500: #39B54A;
  --onest-green-100: #EAF7EC;

  /* =========================
     NEUTRAL
  ========================== */

  --gray-950: #20252B;
  --gray-700: #475467;
  --gray-500: #667085;
  --gray-300: #D0D5DD;
  --gray-200: #E1E6EB;
  --gray-100: #F2F4F7;
  --gray-50: #F8FAFC;

  --white: #FFFFFF;

  /* =========================
     SEMANTIC
  ========================== */

  --success: #22A447;
  --warning: #F59E0B;
  --danger: #D92D20;
  --info: #1677BD;

  /* =========================
     RADIUS
  ========================== */

  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
}
```

---

# 6. Uso del azul ONEST

El azul ONEST deberá utilizarse para:

- Navegación
- Sidebar
- Botones principales
- Links
- Indicadores activos
- Tabs seleccionados
- Elementos interactivos
- Iconografía principal
- Encabezados relevantes
- Estados informativos

Ejemplo:

```css
background: #00549E;
color: #FFFFFF;
```

Hover:

```css
background: #003E75;
```

---

# 7. Uso del verde ONEST

El verde deberá utilizarse únicamente como acento.

Puede utilizarse para:

- Estados satisfactorios
- Progreso
- Confirmaciones
- Indicadores positivos
- Innovación
- Elementos secundarios de marca
- Indicador activo dentro de navegación

No utilizar el verde como color dominante del sistema.
No construir sidebars completos en verde.
No utilizar verde únicamente como decoración.

---

# 8. Colores semánticos

Los estados funcionales deben conservar colores universales.

```css
--success: #22A447;
--warning: #F59E0B;
--danger: #D92D20;
--info: #1677BD;
--neutral: #667085;
```

---

# 9. Fondos

Para sistemas administrativos y operativos:

```text
Página: #F5F7F9
Cards: #FFFFFF
Sidebar: #003E75
Header: #FFFFFF
Footer: #003E75
```

Evitar utilizar fondos completamente azules en páginas completas.

---

# 10. Tipografía

### Branding y títulos
```css
font-family: "Montserrat", "Arial", sans-serif;
```

### Sistemas y dashboards
```css
font-family: "Inter", "Arial", sans-serif;
```

---

# 11. Jerarquía tipográfica

```text
H1: 32px | Font weight: 700
H2: 24px | Font weight: 700
H3: 20px | Font weight: 600
Título de Card: 16px | Font weight: 600
Body: 14px - 16px | Font weight: 400
Label: 13px - 14px | Font weight: 500
Caption: 12px | Font weight: 400
```

---

# 12. Botón principal y secundario

```css
.btn-primary {
  height: 44px;
  padding: 0 20px;
  background: #00549E;
  color: #FFFFFF;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.2s ease;
}
.btn-primary:hover {
  background: #003E75;
}

.btn-secondary {
  height: 44px;
  padding: 0 20px;
  background: #FFFFFF;
  color: #00549E;
  border: 1px solid #00549E;
  border-radius: 8px;
  font-weight: 600;
}
```

---

# 13. Cards

```css
.card {
  background: #FFFFFF;
  border: 1px solid #E1E6EB;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
```

---

# 14. Sidebar

```css
background: #003E75;
color: #FFFFFF;
```

Opción activa del Sidebar:
```css
.sidebar-item-active {
  background: rgba(255, 255, 255, 0.12);
  border-left: 3px solid #39B54A;
}
```

---

# 15. Header

```text
Altura: 64px - 72px
Fondo: blanco (#FFFFFF)
Border inferior: #E1E6EB
```

---

# 16. Iconografía

```text
Lucide Icons
Tipo: Outline
Tamaño: 18px - 22px
```

---

# 17. Configuración Tailwind CSS

```js
export default {
  theme: {
    extend: {
      colors: {
        onest: {
          blue: {
            900: "#003E75",
            700: "#00549E",
            500: "#1677BD",
            100: "#EAF3FA",
          },
          green: {
            700: "#2B9138",
            500: "#39B54A",
            100: "#EAF7EC",
          },
        },
      },
      borderRadius: {
        sm: "6px",
        md: "8px",
        lg: "12px",
      },
    },
  },
};
```

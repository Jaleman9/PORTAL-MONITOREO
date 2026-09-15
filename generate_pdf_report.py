import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

def build_pdf(filename="COMPARATIVA_COMPETENCIA.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#0f172a")
    accent_emerald = colors.HexColor("#059669")
    accent_dark_emerald = colors.HexColor("#064e3b")
    text_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    bg_light_gray = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#cbd5e1")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_muted,
        spaceAfter=15
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=accent_dark_emerald,
        spaceBefore=12,
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_dark
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    )
    
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=text_dark
    )
    
    td_bold = ParagraphStyle(
        'TableCellBold',
        parent=td_style,
        fontName='Helvetica-Bold'
    )
    
    td_highlight = ParagraphStyle(
        'TableCellHighlight',
        parent=td_style,
        fontName='Helvetica-Bold',
        textColor=accent_dark_emerald
    )

    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0369a1")
    )

    story = []

    # Header Badge & Title
    story.append(Paragraph("<b>ONEST WEB ANALYTICS PLATFORM</b> | DOCUMENTO EJECUTIVO", ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8, textColor=accent_emerald, spaceAfter=4)))
    story.append(Paragraph("Benchmark de Analítica Web vs. Competencia & Métodos de Medición", title_style))
    story.append(Paragraph("Respuesta técnica y comparativa: Cómo mide el tiempo, comportamiento y gobernanza nuestra plataforma frente a PostHog, OpenReplay, Umami, Plausible y Matomo.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_emerald, spaceBefore=0, spaceAfter=14))

    # SECTION 1: Matriz Comparativa
    story.append(Paragraph("1. Matriz Comparativa de Herramientas del Mercado", section_title_style))
    
    table_data = [
        [
            Paragraph("<b>Herramienta</b>", th_style),
            Paragraph("<b>Enfoque Principal</b>", th_style),
            Paragraph("<b>Cómo Mide el Tiempo / Métricas</b>", th_style),
            Paragraph("<b>Tipo de Hosting</b>", th_style)
        ],
        [
            Paragraph("<b>PostHog</b>", td_bold),
            Paragraph("Analítica de producto y comportamiento", td_style),
            Paragraph("Tiempo en pantalla, grabaciones de sesión y embudos por duración", td_style),
            Paragraph("Docker / Kubernetes / Cloud", td_style)
        ],
        [
            Paragraph("<b>OpenReplay</b>", td_bold),
            Paragraph("<i>Session replay</i> y observabilidad frontend", td_style),
            Paragraph("Tiempo activo/inactivo segundo a segundo y reproducción visual en video", td_style),
            Paragraph("Docker / Helm / Kubernetes", td_style)
        ],
        [
            Paragraph("<b>Umami</b>", td_bold),
            Paragraph("Analítica web minimalista y privada", td_style),
            Paragraph("Duración media de sesión y tiempo por URL sin <i>cookies</i>", td_style),
            Paragraph("Docker / Node.js / PostgreSQL", td_style)
        ],
        [
            Paragraph("<b>Plausible</b>", td_bold),
            Paragraph("Analítica web simple (alternativa a GA)", td_style),
            Paragraph("Tiempo promedio de permanencia por visita y página", td_style),
            Paragraph("Docker / ClickHouse", td_style)
        ],
        [
            Paragraph("<b>Matomo</b>", td_bold),
            Paragraph("Analítica integral tradicional", td_style),
            Paragraph("Duración de visita, tiempo por página y rebote histórico", td_style),
            Paragraph("PHP + MySQL / Cloud", td_style)
        ],
        [
            Paragraph("<b>ONEST Analytics</b><br/><font color='#059669'><b>(Nuestra Plataforma)</b></font>", td_highlight),
            Paragraph("<b>Gobernanza corporativa, adopción de portales B2B e internos, observabilidad y privacidad estricta (k &ge; 5)</b>", td_highlight),
            Paragraph("<b>Duración de sesión (session_start/end), tiempo de carga real (NavigationTiming API), permanencia en SPAs e inactividad</b>", td_highlight),
            Paragraph("<b>Docker Compose (ClickHouse + RabbitMQ + FastAPI)</b>", td_highlight)
        ]
    ]

    t = Table(table_data, colWidths=[105, 135, 185, 115])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        # Highlight our platform row
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 6), (-1, 6), 1.5, accent_emerald),
    ]))
    story.append(t)
    story.append(Spacer(1, 14))

    # SECTION 2: ¿Cómo lo mido?
    story.append(Paragraph("2. ¿Cómo lo Mido? (Métricas y Mecanismos de Captura)", section_title_style))
    story.append(Paragraph("El SDK Web (<font name='Courier'>telemetry.js</font>) y la API analítica operan con 4 mecanismos no invasivos:", body_style))
    story.append(Spacer(1, 6))

    how_data = [
        [
            Paragraph("<b>1. Tiempo de Rendimiento y Carga Real (load_time_ms)</b>", td_bold),
            Paragraph("Mide los milisegundos exactos de carga en el navegador real del usuario mediante la API nativa <font name='Courier'>PerformanceNavigationTiming</font> (<font name='Courier'>performance.getEntriesByType('navigation')[0].duration</font>).", td_style)
        ],
        [
            Paragraph("<b>2. Duración de Sesión e Inactividad</b>", td_bold),
            Paragraph("Mantiene una sesión activa en <font name='Courier'>sessionStorage</font> con caducidad tras <b>30 minutos de inactividad</b>. Captura automáticamente <font name='Courier'>session_start</font> al ingresar y <font name='Courier'>session_end</font> al cerrar pestaña vía <font name='Courier'>beforeunload</font> / <font name='Courier'>visibilitychange</font>.", td_style)
        ],
        [
            Paragraph("<b>3. Tiempo en SPAs (Single Page Applications)</b>", td_bold),
            Paragraph("Instrumenta el History API (<font name='Courier'>pushState</font>, <font name='Courier'>replaceState</font>, <font name='Courier'>popstate</font>) para medir tiempos entre rutas virtuales en frameworks como React, Angular o Vue sin requerir recarga.", td_style)
        ],
        [
            Paragraph("<b>4. Métricas de Negocio, Adopción y Cuentas Ociosas</b>", td_bold),
            Paragraph("ClickHouse computa <font name='Courier'>DAU</font> (usuarios diarios), <font name='Courier'>MAU</font> (mensuales), ratio de adopción (<font name='Courier'>DAU/MAU</font>) y alerta automáticamente cuentas con más de 30 días sin actividad corporativa.", td_style)
        ]
    ]

    t_how = Table(how_data, colWidths=[180, 360])
    t_how.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_how)
    story.append(Spacer(1, 14))

    # SECTION 3: ¿Con qué lo mido?
    story.append(Paragraph("3. ¿Con Qué lo Mido? (Arquitectura y Stack Tecnológico)", section_title_style))

    stack_data = [
        [
            Paragraph("<b>Capa</b>", th_style),
            Paragraph("<b>Componente</b>", th_style),
            Paragraph("<b>Función Técnica en la Medición</b>", th_style)
        ],
        [
            Paragraph("<b>1. Captura Cliente</b>", td_bold),
            Paragraph("<b>SDK Web TypeScript</b> (<font name='Courier'>telemetry.js</font>)", td_style),
            Paragraph("Librería ultra-ligera (<12 KB), no bloqueante, sin cookies de rastreo invasivas. Captura eventos y errores JS no controlados.", td_style)
        ],
        [
            Paragraph("<b>2. Borde / Ingesta</b>", td_bold),
            Paragraph("<b>Collector Service</b> (FastAPI)", td_style),
            Paragraph("Recepción asíncrona de alta velocidad. Valida contratos JSON Schema y genera <b>hash HMAC-SHA256</b> del usuario antes de encolar.", td_style)
        ],
        [
            Paragraph("<b>3. Mensajería</b>", td_bold),
            Paragraph("<b>RabbitMQ</b> (AMQP)", td_style),
            Paragraph("Amortiguador de eventos asíncronos para absorber picos masivos de telemetría sin pérdida de datos.", td_style)
        ],
        [
            Paragraph("<b>4. Procesamiento</b>", td_bold),
            Paragraph("<b>Consumer Worker</b> (Python)", td_style),
            Paragraph("Consume en micro-lotes (<i>micro-batching</i> de 100 eventos / 1.5s) e inserta masivamente en la base de datos.", td_style)
        ],
        [
            Paragraph("<b>5. Base de Datos</b>", td_bold),
            Paragraph("<b>ClickHouse OLAP</b> (MergeTree)", td_style),
            Paragraph("Motor columnar de ultra-alto rendimiento. Particionado mensual con <b>TTL de retención de 90 días</b> para minimización de datos.", td_style)
        ],
        [
            Paragraph("<b>6. Gobernanza & UI</b>", td_bold),
            Paragraph("<b>Aggregation API + Dashboard</b>", td_style),
            Paragraph("API con control de acceso por roles (<b>RBAC</b>), métricas de salud SLA y filtro de privacidad <b>k-anonymity (k &ge; 5)</b>.", td_style)
        ]
    ]

    t_stack = Table(stack_data, colWidths=[95, 145, 300])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 14))

    # SECTION 4: Ventajas y Diferenciadores
    story.append(Paragraph("4. Diferenciadores Clave frente al Mercado (Resumen Ejecutivo)", section_title_style))

    diff_data = [
        [
            Paragraph("<b>Frente a PostHog / OpenReplay:</b><br/>No realiza grabaciones en video de la pantalla. Esto elimina el riesgo de fuga de información confidencial o contraseñas en formularios corporativos y reduce el consumo de red y almacenamiento en un 95%.", td_style),
            Paragraph("<b>Frente a Matomo / Google Analytics:</b><br/>No sufre de cuellos de botella en bases de datos relacionales tradicionales (MySQL/PHP). ClickHouse permite consultar millones de eventos en milisegundos con costo mínimo.", td_style)
        ],
        [
            Paragraph("<b>Frente a Umami / Plausible:</b><br/>Diseñado para entornos corporativos y auditorías B2B: soporte multi-portal centralizado, matriz RBAC (Ejecutivo vs Analista), k-anonymity (k &ge; 5) y alertas de cuentas ociosas.", td_style),
            Paragraph("<b>100% Soberanía y On-Premise:</b><br/>Desplegable en cualquier servidor o nube privada mediante <font name='Courier'>docker compose up -d</font>, manteniendo los datos de la empresa bajo su exclusivo control.", td_style)
        ]
    ]

    t_diff = Table(diff_data, colWidths=[270, 270])
    t_diff.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_diff)

    doc.build(story)
    print(f"PDF generado exitosamente en: {filename}")

if __name__ == "__main__":
    build_pdf()

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def build_pdf(filename="COMPARATIVA_COMPETENCIA.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#0f172a")
    accent_emerald = colors.HexColor("#059669")
    accent_dark_emerald = colors.HexColor("#064e3b")
    text_dark = colors.HexColor("#1e293b")
    text_muted = colors.HexColor("#64748b")
    border_color = colors.HexColor("#cbd5e1")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceAfter=3
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=text_muted,
        spaceAfter=12
    )
    
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        textColor=accent_dark_emerald,
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11.5,
        textColor=text_dark
    )
    
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.white
    )
    
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
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

    story = []

    # Header Badge & Title
    story.append(Paragraph("<b>ONEST WEB ANALYTICS PLATFORM</b> | DOCUMENTO EJECUTIVO DE ARQUITECTURA", ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=8, textColor=accent_emerald, spaceAfter=2)))
    story.append(Paragraph("Benchmark de Analítica Web vs. Competencia & Métodos de Medición", title_style))
    story.append(Paragraph("Respuesta técnica comparativa: Cómo mide el tiempo, comportamiento y observabilidad nuestra plataforma frente a OpenReplay, PostHog, Umami, Plausible y Matomo.", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=accent_emerald, spaceBefore=0, spaceAfter=10))

    # SECTION 1: Matriz Comparativa (5 Columnas exactas)
    story.append(Paragraph("1. Matriz Comparativa de Enfoque, Captura y Medición", section_title_style))
    
    table_data = [
        [
            Paragraph("<b>Herramienta</b>", th_style),
            Paragraph("<b>Enfoque Principal</b>", th_style),
            Paragraph("<b>Tipo de Captura</b>", th_style),
            Paragraph("<b>Cómo Mide / Graba</b>", th_style),
            Paragraph("<b>Hosting</b>", th_style)
        ],
        [
            Paragraph("<b>OpenReplay</b><br/><font size=6 color='#64748b'>Session replay</font>", td_bold),
            Paragraph("Reproducción visual y observabilidad de frontend", td_style),
            Paragraph("<font color='#e11d48'><b>reproducción íntegra</b></font><br/>Captura 100% de actividad: vistas, clics, red, consola, CPU/memoria.", td_style),
            Paragraph("<b>Grabación DOM continua</b>: Registra mutaciones del DOM para reconstruir visualmente la sesión.", td_style),
            Paragraph("Docker / Helm / K8s", td_style)
        ],
        [
            Paragraph("<b>PostHog</b><br/><font size=6 color='#64748b'>Product analytics</font>", td_bold),
            Paragraph("Analítica de producto y comportamiento", td_style),
            Paragraph("Tiempo en pantalla, grabaciones de sesión y embudos por duración.", td_style),
            Paragraph("<b>Eventos + Replay opcional</b>: Telemetría de eventos con grabación visual de navegación.", td_style),
            Paragraph("Docker / K8s / Cloud", td_style)
        ],
        [
            Paragraph("<b>Umami</b><br/><font size=6 color='#64748b'>Web analytics</font>", td_bold),
            Paragraph("Analítica web minimalista y privada", td_style),
            Paragraph("Duración media de sesión y tiempo por URL sin <i>cookies</i>.", td_style),
            Paragraph("<b>Ping periódico</b>: Heartbeat mientras la pestaña está activa.", td_style),
            Paragraph("Docker / Node / Postgres", td_style)
        ],
        [
            Paragraph("<b>Plausible</b><br/><font size=6 color='#64748b'>Web analytics</font>", td_bold),
            Paragraph("Analítica web simple (alternativa a GA)", td_style),
            Paragraph("Tiempo promedio de permanencia por visita y página.", td_style),
            Paragraph("<b>Duración estimada</b>: Timestamps entre páginas sucesivas.", td_style),
            Paragraph("Docker / ClickHouse", td_style)
        ],
        [
            Paragraph("<b>Matomo</b><br/><font size=6 color='#64748b'>Full analytics</font>", td_bold),
            Paragraph("Analítica integral tradicional", td_style),
            Paragraph("Duración de visita, tiempo por página y rebote histórico.", td_style),
            Paragraph("<b>Heartbeat tracker</b>: Ping regular de presencia en MySQL.", td_style),
            Paragraph("PHP + MySQL / Cloud", td_style)
        ],
        [
            Paragraph("<b>ONEST Analytics</b><br/><font color='#059669'><b>(Nuestra Plataforma)</b></font>", td_highlight),
            Paragraph("<b>Gobernanza de adopción, salud técnica frontend y privacidad corporativa</b>", td_highlight),
            Paragraph("<font color='#059669'><b>telemetría canónica segura</b></font><br/><b>Captura semántica estructurada</b>: páginas, SPAs, clics en botones, errores JS y tiempos reales (Core Web Vitals).", td_highlight),
            Paragraph("<b>Instrumentación reactiva por eventos</b>: Sin mutaciones DOM ni video. Registra ciclo de vida con NavigationTiming y protege PII (ahorro 95% de red).", td_highlight),
            Paragraph("<b>Docker Compose (ClickHouse + RabbitMQ + FastAPI)</b>", td_highlight)
        ]
    ]

    t = Table(table_data, colWidths=[95, 120, 150, 135, 52])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 6), (-1, 6), colors.HexColor("#ecfdf5")),
        ('BOX', (0, 6), (-1, 6), 1.2, accent_emerald),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # SECTION 2: ¿Cómo lo mido?
    story.append(Paragraph("2. ¿Cómo lo Mido? (Métricas de Tiempo, Salud y Comportamiento)", section_title_style))

    how_data = [
        [
            Paragraph("<b>1. Carga Real (load_time_ms)</b>", td_bold),
            Paragraph("Mide milisegundos reales mediante la API nativa <font name='Courier'>PerformanceNavigationTiming</font> (<font name='Courier'>performance.getEntriesByType('navigation')</font>).", td_style),
            Paragraph("<b>3. SPAs (React/Vue/Angular)</b>", td_bold),
            Paragraph("Instrumenta <font name='Courier'>pushState</font> y <font name='Courier'>popstate</font> para medir navegación virtual sin recarga de página.", td_style)
        ],
        [
            Paragraph("<b>2. Sesión e Inactividad</b>", td_bold),
            Paragraph("Mantiene sesión en <font name='Courier'>sessionStorage</font> con caducidad a los <b>30 min de inactividad</b>. Captura <font name='Courier'>session_start</font> y <font name='Courier'>session_end</font>.", td_style),
            Paragraph("<b>4. Clics Semánticos (Custom)</b>", td_bold),
            Paragraph("Captura clics en <font name='Courier'>button</font> y <font name='Courier'>a</font> (tag, id, texto max 50 caracteres) sin leer inputs ni datos de formularios.", td_style)
        ]
    ]

    t_how = Table(how_data, colWidths=[120, 156, 120, 156])
    t_how.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_how)
    story.append(Spacer(1, 10))

    # SECTION 3: ¿Con qué lo mido?
    story.append(Paragraph("3. ¿Con Qué lo Mido? (Arquitectura y Stack Tecnológico)", section_title_style))

    stack_data = [
        [
            Paragraph("<b>1. SDK Web</b> (<font name='Courier'>telemetry.js</font>)", td_bold),
            Paragraph("Librería cliente en TypeScript (<12 KB), no bloqueante, sin cookies de rastreo invasivas.", td_style),
            Paragraph("<b>4. Consumer</b> (Worker)", td_bold),
            Paragraph("Micro-lotes (<i>micro-batching</i> de 100 ev / 1.5s) e inserción masiva.", td_style)
        ],
        [
            Paragraph("<b>2. Collector</b> (FastAPI)", td_bold),
            Paragraph("Ingesta asíncrona de alta concurrencia con <b>hash HMAC-SHA256</b> del usuario antes de encolar.", td_style),
            Paragraph("<b>5. ClickHouse</b> (OLAP)", td_bold),
            Paragraph("Base columnar. Particionado mensual con <b>TTL de retención de 90 días</b>.", td_style)
        ],
        [
            Paragraph("<b>3. RabbitMQ</b> (AMQP)", td_bold),
            Paragraph("Amortiguador de eventos asíncronos para tolerar picos masivos de telemetría sin pérdida.", td_style),
            Paragraph("<b>6. Aggregation & UI</b>", td_bold),
            Paragraph("API con <b>RBAC</b>, salud SLA y filtro de privacidad <b>k-anonymity (k &ge; 5)</b>.", td_style)
        ]
    ]

    t_stack = Table(stack_data, colWidths=[120, 156, 120, 156])
    t_stack.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#f8fafc")),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor("#f8fafc")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_stack)
    story.append(Spacer(1, 10))

    # SECTION 4: Diferenciadores Clave
    story.append(Paragraph("4. Comparativa Estratégica: ONEST vs. OpenReplay & Mercado", section_title_style))

    diff_data = [
        [
            Paragraph("<b>Frente a OpenReplay (DOM Replay vs. Telemetría Canónica):</b><br/>OpenReplay graba mutaciones continuas de DOM en video con riesgo de filtrar contraseñas o datos confidenciales en formularios y con alto costo de CPU y red. ONEST captura solo eventos semánticos (rutas, errores, tiempos, clics en botones) garantizando 100% de confidencialidad y 95% menos peso.", td_style),
            Paragraph("<b>Frente a Matomo / GA / Umami (Rendimiento & Gobernanza B2B):</b><br/>No sufre de cuellos de botella de bases relacionales tradicionales (MySQL/PHP); ClickHouse procesa millones de eventos en milisegundos. Añade soporte multi-portal centralizado, matriz RBAC (Ejecutivo vs Analista) y cumplimiento estricto k-anonymity (k &ge; 5).", td_style)
        ]
    ]

    t_diff = Table(diff_data, colWidths=[276, 276])
    t_diff.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ('GRID', (0, 0), (-1, -1), 0.5, border_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_diff)

    doc.build(story)
    print(f"PDF generado exitosamente en: {filename}")

if __name__ == "__main__":
    build_pdf()

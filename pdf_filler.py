"""
PDF filler for EMERGENCIAS Author Responsibilities Form.
Overlays text and checkbox marks on the visual PDF template.
"""

import io
import textwrap
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from pypdf import PdfReader, PdfWriter

PAGE_W = 595.276
PAGE_H = 793.701

# ── Fixed defaults ────────────────────────────────────────────────────────────
TITULO = (
    "ANONIM: desarrollo y validación de una herramienta de inteligencia "
    "artificial para la preanonimización automática de texto clínico en español"
)

DIRECCION_LINE1 = "Servicio de Urgencias, Hospital Universitario La Paz,"
DIRECCION_LINE2 = "Paseo de la Castellana 261, 28046 Madrid"

TITULO_LINE1 = "ANONIM: desarrollo y validación de una herramienta de"
TITULO_LINE2 = "inteligencia artificial para la preanonimización automática"
TITULO_LINE3 = "de texto clínico en español"


# ── Coordinate helpers ────────────────────────────────────────────────────────
def rl(y_pdf: float, font_size: float = 9) -> float:
    """Convert pdfplumber y (from top) to reportlab y (from bottom)."""
    return PAGE_H - y_pdf - font_size


def mark(c: canvas.Canvas, x: float, y_pdf: float, size: float = 7):
    """Draw a bold X inside a checkbox at pdfplumber coordinates."""
    c.setFont("Helvetica-Bold", size)
    c.drawString(x + 0.5, rl(y_pdf, size), "X")


def text(c: canvas.Canvas, x: float, y_pdf: float, value: str, size: float = 8.5):
    """Draw text at pdfplumber coordinates."""
    c.setFont("Helvetica", size)
    c.drawString(x, rl(y_pdf, size), value)


# ── Per-page overlay builders ─────────────────────────────────────────────────
def _page1(c: canvas.Canvas, nombre: str, email: str, telefono: str,
           correspondencia: bool):
    # Title (3 lines)
    text(c, 160, 321, TITULO_LINE1)
    text(c, 160, 330, TITULO_LINE2)
    text(c, 160, 339, TITULO_LINE3)

    # Author name
    text(c, 90, 357, nombre)

    # Profession: Médico checkbox (□ is at x=96.8)
    mark(c, 96.8, 384.6)

    # Correspondencia
    if correspondencia:
        mark(c, 184.9, 420.8)   # Sí (ES)
        mark(c, 347.5, 420.8)   # YES (EN)
    else:
        mark(c, 210.9, 420.8)   # NO (ES)
        mark(c, 373.5, 420.8)   # NO (EN)

    # Único autor: NO
    mark(c, 201.4, 429.9)       # NO (ES)
    mark(c, 387.8, 429.9)       # NO (EN)

    # Email
    text(c, 185, 448, email)

    # Teléfono
    text(c, 140, 457, telefono)

    # Dirección postal (2 lines)
    text(c, 175, 475, DIRECCION_LINE1)
    text(c, 42,  484, DIRECCION_LINE2)

    # Autoría declaration: SÍ
    mark(c, 227.8, 683.4)       # SÍ (ES)
    mark(c, 443.5, 683.4)       # YES (EN)


def _page2(c: canvas.Canvas):
    # ¿Reproduce material de otras publicaciones? → NO
    mark(c, 338.5, 106.2)       # NO (ES)
    mark(c, 352.9, 115.4)       # NO (EN)

    # ¿Publicación redundante o duplicada? → SÍ (no es duplicada)
    mark(c, 279.2, 262.3)       # Sí (ES)
    mark(c, 322.4, 271.5)       # YES (EN)

    # Cesión de derechos → SÍ
    mark(c, 246.3, 638.9)       # Sí (ES)
    mark(c, 229.1, 648.1)       # YES (EN)

    # Gobierno extranjero → NO
    mark(c, 73.2,  721.5)       # NO (ES)
    mark(c, 135.6, 721.5)       # NO (EN)


def _page3(c: canvas.Canvas):
    # Financiación → NO
    mark(c, 235.8, 159.3)       # NO (ES)
    mark(c, 374.8, 159.3)       # NO (EN)

    # Conflicto de intereses general → NO
    mark(c, 301.2, 293.1)       # NO (ES)
    mark(c, 534.3, 293.1)       # NO (EN)

    # Sub-pregunta 1 → NO
    mark(c, 473.8, 342.0)       # NO (ES)
    mark(c, 460.9, 351.2)       # NO (EN)

    # Sub-pregunta 2 → NO
    mark(c, 548.5, 387.9)       # NO (ES)
    mark(c, 548.5, 397.1)       # NO (EN)

    # Sub-pregunta 3 → NO
    mark(c, 548.5, 433.8)       # NO (ES)
    mark(c, 548.5, 443.0)       # NO (EN)

    # Sub-pregunta 4 → NO
    mark(c, 144.1, 488.9)       # NO (ES)
    mark(c, 128.4, 507.3)       # NO (EN)

    # Sub-pregunta 5 → NO
    mark(c, 126.2, 562.4)       # NO (ES)
    mark(c, 160.3, 590.0)       # NO (EN)

    # Sub-pregunta 6 → NO
    mark(c, 548.5, 635.9)       # NO (ES)
    mark(c, 548.5, 645.1)       # NO (EN)


def _page4(c: canvas.Canvas):
    # Datos de pacientes: "No, en el artículo no aparecen datos de pacientes"
    mark(c, 39.7, 243.2)        # ES
    mark(c, 39.7, 251.8)        # EN

    # Protección de personas → No patient data
    mark(c, 39.7, 388.8)        # ES
    mark(c, 39.7, 397.4)        # EN

    # Protección de personas y animales → no experiments in humans/animals
    mark(c, 39.7, 614.7)        # ES
    mark(c, 39.7, 623.3)        # EN

    # CEIC: estudio eximido de evaluación
    mark(c, 39.7, 674.7)        # ES
    mark(c, 39.7, 683.3)        # EN

    # Date
    today = date.today().strftime("%d/%m/%Y")
    text(c, 170, 706, today, size=9)


# ── Main function ─────────────────────────────────────────────────────────────
def fill_pdf(template_path: str, nombre: str, email: str,
             telefono: str, correspondencia: bool = False) -> bytes:
    """
    Fill the EMERGENCIAS author form for one author.
    Returns the filled PDF as bytes.
    """
    reader = PdfReader(template_path)
    writer = PdfWriter()

    for page_num in range(len(reader.pages)):
        # Create overlay for this page
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))

        if page_num == 0:
            _page1(c, nombre, email, telefono, correspondencia)
        elif page_num == 1:
            _page2(c)
        elif page_num == 2:
            _page3(c)
        elif page_num == 3:
            _page4(c)

        c.save()
        buf.seek(0)

        # Merge overlay onto original page
        overlay_reader = PdfReader(buf)
        base_page = reader.pages[page_num]
        base_page.merge_page(overlay_reader.pages[0])
        writer.add_page(base_page)

    # Write to bytes
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()

"""
PDF filler for EMERGENCIAS Author Responsibilities Form.
Overlays text and checkbox marks on the visual PDF template.
"""

import io
import textwrap
from datetime import date
from pathlib import Path
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter

PAGE_W = 595.276
PAGE_H = 793.701

# ── Fixed defaults ────────────────────────────────────────────────────────────
DIRECCION_LINE1 = "Servicio de Urgencias, Hospital Universitario La Paz,"
DIRECCION_LINE2 = "Paseo de la Castellana 261, 28046 Madrid"

# Characters per line in the title box (Helvetica 8.5pt, width ~394pt)
TITLE_LINE_WIDTH = 78


def _split_title(titulo: str) -> list[str]:
    """Split title into max 3 lines of ~78 chars each."""
    lines = textwrap.wrap(titulo, width=TITLE_LINE_WIDTH)
    return lines[:3]   # form has 3 title rows


# ── Coordinate helpers ────────────────────────────────────────────────────────
def rl(y_pdf: float, font_size: float = 9) -> float:
    """Convert pdfplumber y (from top) to reportlab y (from bottom)."""
    return PAGE_H - y_pdf - font_size


def mark(c: canvas.Canvas, x: float, y_pdf: float, size: float = 7):
    """Draw a bold X inside a checkbox at pdfplumber coordinates."""
    c.setFont("Helvetica-Bold", size)
    c.drawString(x + 0.5, rl(y_pdf, size), "X")


def txt(c: canvas.Canvas, x: float, y_pdf: float, value: str, size: float = 8.5):
    """Draw text at pdfplumber coordinates."""
    c.setFont("Helvetica", size)
    c.drawString(x, rl(y_pdf, size), value)


# ── Per-page overlay builders ─────────────────────────────────────────────────
def _page1(c: canvas.Canvas, nombre: str, email: str, telefono: str,
           correspondencia: bool, titulo: str):
    title_lines = _split_title(titulo)
    y_rows = [321, 330, 339]
    for i, line in enumerate(title_lines):
        txt(c, 160, y_rows[i], line)

    # Author name
    txt(c, 90, 357, nombre)

    # Profession: Médico
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
    txt(c, 185, 448, email)

    # Teléfono
    txt(c, 140, 457, telefono)

    # Dirección postal (2 lines)
    txt(c, 175, 475, DIRECCION_LINE1)
    txt(c, 42,  484, DIRECCION_LINE2)

    # Autoría declaration: SÍ
    mark(c, 227.8, 683.4)
    mark(c, 443.5, 683.4)


def _page2(c: canvas.Canvas):
    # Reproduce material → NO
    mark(c, 338.5, 106.2)
    mark(c, 352.9, 115.4)

    # Publicación redundante → SÍ (no es duplicada)
    mark(c, 279.2, 262.3)
    mark(c, 322.4, 271.5)

    # Cesión de derechos → SÍ
    mark(c, 246.3, 638.9)
    mark(c, 229.1, 648.1)

    # Gobierno extranjero → NO
    mark(c, 73.2,  721.5)
    mark(c, 135.6, 721.5)


def _page3(c: canvas.Canvas):
    # Financiación → NO
    mark(c, 235.8, 159.3)
    mark(c, 374.8, 159.3)

    # Conflicto de intereses general → NO
    mark(c, 301.2, 293.1)
    mark(c, 534.3, 293.1)

    # 6 sub-preguntas → todas NO
    mark(c, 473.8, 342.0);  mark(c, 460.9, 351.2)
    mark(c, 548.5, 387.9);  mark(c, 548.5, 397.1)
    mark(c, 548.5, 433.8);  mark(c, 548.5, 443.0)
    mark(c, 144.1, 488.9);  mark(c, 128.4, 507.3)
    mark(c, 126.2, 562.4);  mark(c, 160.3, 590.0)
    mark(c, 548.5, 635.9);  mark(c, 548.5, 645.1)


def _page4(c: canvas.Canvas):
    # Datos de pacientes: no aparecen datos
    mark(c, 39.7, 243.2)
    mark(c, 39.7, 251.8)

    # Protección personas → no patient data
    mark(c, 39.7, 388.8)
    mark(c, 39.7, 397.4)

    # Protección personas y animales → no experiments
    mark(c, 39.7, 614.7)
    mark(c, 39.7, 623.3)

    # CEIC: estudio eximido
    mark(c, 39.7, 674.7)
    mark(c, 39.7, 683.3)

    # Fecha
    today = date.today().strftime("%d/%m/%Y")
    txt(c, 170, 706, today, size=9)


# ── Main function ─────────────────────────────────────────────────────────────
def fill_pdf(template_path: str, nombre: str, email: str,
             telefono: str, correspondencia: bool = False,
             titulo: str = "") -> bytes:
    """
    Fill the EMERGENCIAS author form for one author.
    Returns the filled PDF as bytes.
    """
    reader = PdfReader(template_path)
    writer = PdfWriter()

    for page_num in range(len(reader.pages)):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))

        if page_num == 0:
            _page1(c, nombre, email, telefono, correspondencia, titulo)
        elif page_num == 1:
            _page2(c)
        elif page_num == 2:
            _page3(c)
        elif page_num == 3:
            _page4(c)

        c.save()
        buf.seek(0)

        overlay_reader = PdfReader(buf)
        base_page = reader.pages[page_num]
        base_page.merge_page(overlay_reader.pages[0])
        writer.add_page(base_page)

    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()

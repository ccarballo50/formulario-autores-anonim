"""
Formulario de Responsabilidades del Autor — Revista EMERGENCIAS
================================================================
Formulario público para coautores del artículo ANONIM.
El PDF generado se envía automáticamente al IP por email.
"""

import streamlit as st
from pathlib import Path
from pdf_filler import fill_pdf
from email_sender import send_pdf_to_admin

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Formulario de Autor · EMERGENCIAS",
    page_icon="📋",
    layout="centered",
)

PDF_TEMPLATE = Path(__file__).parent / "formulario_emergencias.pdf"

DEFAULT_TITULO = (
    "ANONIM: desarrollo y validación de una herramienta de inteligencia "
    "artificial para la preanonimización automática de texto clínico en español"
)


def get_titulo() -> str:
    try:
        return st.secrets["article"]["titulo"]
    except Exception:
        return DEFAULT_TITULO


TITULO = get_titulo()

# ── Cabecera ──────────────────────────────────────────────────────────────────
st.title("Formulario de Responsabilidades del Autor")
st.markdown("**Revista** · EMERGENCIAS · SEMES")
st.divider()

st.markdown(
    f"""
    ### Artículo
    > *{TITULO}*

    Como coautor/a de este artículo necesitas completar el
    **Documento de Responsabilidades del Autor, Acuerdo de Publicación y
    Cesión de Derechos** exigido por la revista EMERGENCIAS.

    Rellena tus datos. El formulario PDF se generará automáticamente y
    recibirás un enlace de descarga. **Imprímelo, fírmalo a mano** y
    envíalo a [carmen.ibanez@semes.org](mailto:carmen.ibanez@semes.org).
    """
)
st.divider()

# ── Formulario ────────────────────────────────────────────────────────────────
with st.form("autor_form"):
    st.subheader("Tus datos")

    nombre = st.text_input(
        "Nombre completo *",
        placeholder="Ej.: María García López",
    )
    email = st.text_input(
        "Correo electrónico institucional *",
        placeholder="nombre@hospital.es",
    )
    telefono = st.text_input(
        "Teléfono de contacto *",
        placeholder="+34 600 000 000",
    )
    correspondencia = st.checkbox(
        "Soy el **autor/a de correspondencia** de este artículo",
        value=False,
    )

    submit = st.form_submit_button("Generar y enviar formulario PDF", type="primary")

# ── Procesamiento ─────────────────────────────────────────────────────────────
if submit:
    errors = []
    if not nombre.strip():
        errors.append("El nombre completo es obligatorio.")
    if not email.strip() or "@" not in email:
        errors.append("Introduce un correo electrónico válido.")
    if not telefono.strip():
        errors.append("El teléfono es obligatorio.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Generando formulario PDF…"):
            try:
                pdf_bytes = fill_pdf(
                    template_path=str(PDF_TEMPLATE),
                    nombre=nombre.strip(),
                    email=email.strip(),
                    telefono=telefono.strip(),
                    correspondencia=correspondencia,
                    titulo=TITULO,
                )

                # Guardar localmente si el directorio es accesible (entorno local)
                try:
                    local_dir = Path(
                        r"C:\Users\CESAR CC\Desktop\claude-prueba"
                        r"\Documentos autores\ANONIM_preanonimizacion"
                    )
                    if local_dir.parent.parent.exists():
                        local_dir.mkdir(parents=True, exist_ok=True)
                        safe = "".join(
                            c if c.isalnum() or c in " _-" else "_"
                            for c in nombre.strip()
                        )
                        (local_dir / f"{safe}.pdf").write_bytes(pdf_bytes)
                except Exception:
                    pass

                # Enviar PDF al IP por email
                email_sent = False
                try:
                    send_pdf_to_admin(pdf_bytes, nombre.strip(), TITULO)
                    email_sent = True
                except Exception as mail_err:
                    st.warning(
                        f"PDF generado correctamente, pero no se pudo enviar "
                        f"por email: {mail_err}. Descárgalo manualmente."
                    )

                if email_sent:
                    st.success(
                        f"Formulario generado y enviado al investigador principal."
                    )
                else:
                    st.success("Formulario generado correctamente.")

                st.info(
                    "Descarga el PDF, **imprímelo y fírmalo a mano** "
                    "en el campo FIRMA (última página)."
                )

                safe = "".join(
                    c if c.isalnum() or c in " _-" else "_"
                    for c in nombre.strip()
                ).replace(" ", "_")

                st.download_button(
                    label="Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"Formulario_Autor_EMERGENCIAS_{safe}.pdf",
                    mime="application/pdf",
                )

            except Exception as exc:
                st.error(f"Error al generar el PDF: {exc}")
                st.exception(exc)

# ── Pie ───────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Servicio de Urgencias · Hospital Universitario La Paz · Madrid  \n"
    "Investigador principal: Dr. César Carballo  \n"
    "Proyecto ANONIM — Anonimización automática de texto clínico en español"
)

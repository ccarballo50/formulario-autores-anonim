"""
Formulario de Responsabilidades del Autor — Revista EMERGENCIAS
================================================================
Aplicación web para que los coautores del artículo ANONIM
rellenen sus datos y generen el formulario PDF de la revista.

Despliegue: Streamlit Cloud — https://github.com/ccarballo50
"""

import os
import streamlit as st
from pathlib import Path
from pdf_filler import fill_pdf

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Formulario de Autor · EMERGENCIAS",
    page_icon="📋",
    layout="centered",
)

# ── Constantes ────────────────────────────────────────────────────────────────
PDF_TEMPLATE = Path(__file__).parent / "formulario_emergencias.pdf"
OUTPUT_FOLDER = Path(
    r"C:\Users\CESAR CC\Desktop\claude-prueba\Documentos autores\ANONIM_preanonimizacion"
)
ARTICULO_TITULO = (
    "ANONIM: desarrollo y validación de una herramienta de inteligencia "
    "artificial para la preanonimización automática de texto clínico en español"
)

# ── Cabecera ──────────────────────────────────────────────────────────────────
st.title("Formulario de Responsabilidades del Autor")
st.markdown("**Revista** · EMERGENCIAS · SEMES")

st.divider()

st.markdown(
    """
    ### Artículo al que se adhiere
    > *{}*

    Como coautor/a de este artículo, debes completar el **Documento de
    Responsabilidades del Autor, Acuerdo de Publicación y Cesión de Derechos**
    exigido por la revista EMERGENCIAS.

    Rellena los tres campos a continuación. El formulario PDF se generará
    automáticamente con todos tus datos y los valores predefinidos del artículo.
    Descárgalo, **imprímelo, fírmalo** y envíalo a:
    [carmen.ibanez@semes.org](mailto:carmen.ibanez@semes.org)
    """.format(ARTICULO_TITULO)
)

st.divider()

# ── Formulario ────────────────────────────────────────────────────────────────
with st.form("autor_form"):
    st.subheader("Tus datos")

    nombre = st.text_input(
        "Nombre completo *",
        placeholder="Ej.: María García López",
        help="Nombre y apellidos tal y como aparecerán en el formulario.",
    )

    email = st.text_input(
        "Correo electrónico institucional *",
        placeholder="nombre@hospital.es",
        help="Email de contacto profesional.",
    )

    telefono = st.text_input(
        "Teléfono de contacto *",
        placeholder="+34 600 000 000",
        help="Teléfono (con prefijo internacional si procede).",
    )

    correspondencia = st.checkbox(
        "Soy el **autor/a de correspondencia** de este artículo",
        value=False,
        help="Marca esta casilla únicamente si eres el autor responsable de la correspondencia con la revista.",
    )

    submit = st.form_submit_button("Generar formulario PDF", type="primary")

# ── Procesamiento ─────────────────────────────────────────────────────────────
if submit:
    # Validación
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
        with st.spinner("Generando tu formulario PDF…"):
            try:
                pdf_bytes = fill_pdf(
                    template_path=str(PDF_TEMPLATE),
                    nombre=nombre.strip(),
                    email=email.strip(),
                    telefono=telefono.strip(),
                    correspondencia=correspondencia,
                )

                # Guardar localmente si el directorio existe (entorno local)
                try:
                    if OUTPUT_FOLDER.parent.parent.exists():
                        OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
                        safe_name = "".join(
                            c if c.isalnum() or c in (" ", "_", "-") else "_"
                            for c in nombre.strip()
                        )
                        local_path = OUTPUT_FOLDER / f"{safe_name}.pdf"
                        local_path.write_bytes(pdf_bytes)
                        st.caption(f"Guardado localmente: `{local_path}`")
                except Exception:
                    pass  # En Streamlit Cloud el directorio no existe, OK

                st.success("Formulario generado correctamente.")
                st.info(
                    "Descarga el PDF, **imprímelo y fírmalo a mano** en el campo "
                    "FIRMA / SIGNATURE (última página), y envíalo a la revista."
                )

                # Botón de descarga
                filename = "".join(
                    c if c.isalnum() or c in (" ", "_", "-") else "_"
                    for c in nombre.strip()
                ).replace(" ", "_")

                st.download_button(
                    label="Descargar PDF",
                    data=pdf_bytes,
                    file_name=f"Formulario_Autor_EMERGENCIAS_{filename}.pdf",
                    mime="application/pdf",
                )

            except Exception as exc:
                st.error(f"Error al generar el PDF: {exc}")
                st.exception(exc)

# ── Pie de página ─────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Servicio de Urgencias · Hospital Universitario La Paz · Madrid  \n"
    "Investigador principal: Dr. César Carballo  \n"
    "Proyecto ANONIM — Anonimización automática de texto clínico en español"
)

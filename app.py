"""
Formulario de Responsabilidades del Autor — Revista EMERGENCIAS
================================================================
- Página pública: formulario para coautores (genera y envía PDF)
- Panel Admin (barra lateral, contraseña): gestión del título y envío de invitaciones
"""

import streamlit as st
from pathlib import Path
from pdf_filler import fill_pdf
from email_sender import send_pdf_to_admin, send_invitation

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

# ── Selector de modo en la barra lateral ─────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/"
        "Emergencias_logo.png/320px-Emergencias_logo.png",
        use_container_width=True,
    ) if False else None   # logo opcional; descomenta si tienes imagen local

    st.markdown("## Navegación")
    modo = st.radio(
        "Selecciona vista",
        ["📋 Formulario de autor", "🔐 Administrador"],
        index=0,
    )

# ══════════════════════════════════════════════════════════════════════════════
# VISTA: FORMULARIO PÚBLICO
# ══════════════════════════════════════════════════════════════════════════════
if modo == "📋 Formulario de autor":

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

        submit = st.form_submit_button(
            "Generar y enviar formulario PDF", type="primary"
        )

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

                    # Guardar localmente si el directorio es accesible
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
                            f"PDF generado, pero no se pudo enviar por email: "
                            f"{mail_err}. Descárgalo manualmente."
                        )

                    if email_sent:
                        st.success(
                            "Formulario generado y enviado al investigador principal."
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

    st.divider()
    st.caption(
        "Servicio de Urgencias · Hospital Universitario La Paz · Madrid  \n"
        "Investigador principal: Dr. César Carballo  \n"
        "Proyecto ANONIM — Anonimización automática de texto clínico en español"
    )


# ══════════════════════════════════════════════════════════════════════════════
# VISTA: PANEL DE ADMINISTRADOR
# ══════════════════════════════════════════════════════════════════════════════
else:
    st.title("Panel de Administrador")
    st.caption("Acceso restringido al investigador principal.")

    # ── Autenticación ─────────────────────────────────────────────────────────
    def check_password() -> bool:
        try:
            admin_pwd = st.secrets["email"]["admin_password"]
        except Exception:
            st.error(
                "No se encontró `admin_password` en los secrets de Streamlit. "
                "Configúralo en el panel de Streamlit Cloud."
            )
            return False

        if st.session_state.get("admin_auth"):
            return True

        with st.form("login_form"):
            pwd = st.text_input("Contraseña", type="password")
            login = st.form_submit_button("Entrar")

        if login:
            if pwd == admin_pwd:
                st.session_state["admin_auth"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        return False

    if not check_password():
        st.stop()

    st.success("Sesión iniciada.")

    if st.button("Cerrar sesión"):
        st.session_state["admin_auth"] = False
        st.rerun()

    st.divider()

    # ── Título activo ─────────────────────────────────────────────────────────
    st.subheader("Título del artículo activo")
    st.info(
        "Para cambiar el título edita el secret `[article] titulo` "
        "en el panel de Streamlit Cloud (sin necesidad de tocar el código)."
    )
    st.text_area("Título actual", value=TITULO, height=80, disabled=True)
    st.divider()

    # ── URL del formulario ────────────────────────────────────────────────────
    st.subheader("Enviar invitaciones a coautores")

    form_url = st.text_input(
        "URL pública de esta app",
        placeholder="https://ccarballo50-formulario-autores-anonim-app-XXXX.streamlit.app",
        help="Se incluye en el email de invitación.",
    )

    st.markdown(
        "Introduce un coautor por línea: `Nombre Completo, email@dominio.com`"
    )
    coautores_raw = st.text_area(
        "Lista de coautores",
        placeholder=(
            "María García López, mgarcia@hulp.es\n"
            "Juan Pérez Martín, jperez@uc3m.es\n"
            "Ana Rodríguez Sánchez, arodriguez@upm.es"
        ),
        height=160,
    )

    if st.button("Enviar invitaciones", type="primary"):
        if not form_url.strip():
            st.error("Introduce la URL pública de la app.")
        elif not coautores_raw.strip():
            st.error("Introduce al menos un coautor.")
        else:
            lines = [
                l.strip()
                for l in coautores_raw.strip().splitlines()
                if l.strip()
            ]
            enviados, errores = [], []

            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 2 or "@" not in parts[-1]:
                    errores.append(f"Formato incorrecto: `{line}`")
                    continue
                n_autor = ", ".join(parts[:-1])
                e_autor = parts[-1]
                try:
                    send_invitation(n_autor, e_autor, TITULO, form_url.strip())
                    enviados.append(f"{n_autor} <{e_autor}>")
                except Exception as e:
                    errores.append(f"{n_autor} ({e_autor}): {e}")

            if enviados:
                st.success(f"Invitaciones enviadas ({len(enviados)}):")
                for e in enviados:
                    st.markdown(f"- {e}")
            if errores:
                st.error("Errores:")
                for e in errores:
                    st.markdown(f"- {e}")

    st.divider()
    st.caption("Panel de administración · Proyecto ANONIM · Dr. César Carballo · HULP")

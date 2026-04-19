"""
Panel de Administrador — acceso restringido con contraseña.
Permite a César configurar el título del artículo y enviar
invitaciones por email a los coautores.
"""

import streamlit as st
from email_sender import send_invitation

st.set_page_config(
    page_title="Admin · Formulario EMERGENCIAS",
    page_icon="🔐",
    layout="centered",
)

st.title("Panel de Administrador")
st.caption("Acceso restringido al investigador principal.")

# ── Autenticación ─────────────────────────────────────────────────────────────
def check_password() -> bool:
    try:
        admin_pwd = st.secrets["email"]["admin_password"]
    except Exception:
        st.error("No se encontró `admin_password` en los secrets de Streamlit.")
        return False

    if "admin_auth" not in st.session_state:
        st.session_state["admin_auth"] = False

    if not st.session_state["admin_auth"]:
        pwd = st.text_input("Contraseña de administrador", type="password")
        if st.button("Entrar"):
            if pwd == admin_pwd:
                st.session_state["admin_auth"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
        return False
    return True


if not check_password():
    st.stop()

st.success("Sesión iniciada.")
st.divider()

# ── Obtener título actual ─────────────────────────────────────────────────────
DEFAULT_TITULO = (
    "ANONIM: desarrollo y validación de una herramienta de inteligencia "
    "artificial para la preanonimización automática de texto clínico en español"
)
try:
    titulo_actual = st.secrets["article"]["titulo"]
except Exception:
    titulo_actual = DEFAULT_TITULO

# ── URL pública del formulario ────────────────────────────────────────────────
st.subheader("URL del formulario público")
form_url = st.text_input(
    "Pega aquí la URL pública de esta app en Streamlit Cloud",
    placeholder="https://ccarballo50-formulario-autores-anonim-app-XXXX.streamlit.app",
    help="Esta URL se incluirá en el email de invitación a los coautores.",
)
st.divider()

# ── Título del artículo ───────────────────────────────────────────────────────
st.subheader("Título del artículo")
st.info(
    "El título activo se configura en los **Secrets** de Streamlit Cloud "
    "(`[article] titulo = \"...\"`). El campo de abajo es solo informativo."
)
st.text_area("Título actual (solo lectura)", value=titulo_actual,
             height=80, disabled=True)
st.divider()

# ── Enviar invitaciones ───────────────────────────────────────────────────────
st.subheader("Enviar invitaciones a coautores")
st.markdown(
    "Introduce un coautor por línea con el formato: `Nombre Completo, email@dominio.com`"
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

enviar = st.button("Enviar invitaciones", type="primary")

if enviar:
    if not form_url.strip():
        st.error("Introduce primero la URL pública de la app.")
    elif not coautores_raw.strip():
        st.error("Introduce al menos un coautor.")
    else:
        lines = [l.strip() for l in coautores_raw.strip().splitlines() if l.strip()]
        errores = []
        enviados = []

        for line in lines:
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 2 or "@" not in parts[-1]:
                errores.append(f"Formato incorrecto: `{line}`")
                continue
            nombre = ", ".join(parts[:-1])
            email  = parts[-1]
            try:
                send_invitation(nombre, email, titulo_actual, form_url.strip())
                enviados.append(f"{nombre} <{email}>")
            except Exception as e:
                errores.append(f"{nombre} ({email}): {e}")

        if enviados:
            st.success(f"Invitaciones enviadas a {len(enviados)} coautor/es:")
            for e in enviados:
                st.markdown(f"- {e}")

        if errores:
            st.error("Errores en los siguientes casos:")
            for e in errores:
                st.markdown(f"- {e}")

st.divider()
st.caption("Panel de administración · Proyecto ANONIM · Dr. César Carballo · HULP")

"""
Utilidades de correo electrónico para el formulario de autor.
Usa Gmail SMTP con contraseña de aplicación almacenada en Streamlit secrets.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.utils import formatdate
import streamlit as st


def _get_smtp_cfg():
    """Lee la configuración SMTP de Streamlit secrets."""
    try:
        cfg = st.secrets["email"]
        return {
            "server":   cfg.get("smtp_server", "smtp.gmail.com"),
            "port":     int(cfg.get("smtp_port", 587)),
            "user":     cfg["smtp_user"],
            "password": cfg["smtp_password"],
            "recipient": cfg.get("recipient", cfg["smtp_user"]),
        }
    except Exception as e:
        raise RuntimeError(
            f"Faltan credenciales de email en los secrets de Streamlit. "
            f"Configura [email] smtp_user y smtp_password. ({e})"
        )


def send_pdf_to_admin(pdf_bytes: bytes, author_name: str, article_title: str):
    """
    Envía el formulario PDF relleno al administrador (César).
    """
    cfg = _get_smtp_cfg()

    msg = MIMEMultipart()
    msg["From"]    = cfg["user"]
    msg["To"]      = cfg["recipient"]
    msg["Date"]    = formatdate(localtime=True)
    msg["Subject"] = f"Formulario EMERGENCIAS - {author_name}"

    body = (
        f"Formulario de responsabilidades del autor recibido.\n\n"
        f"Autor:    {author_name}\n"
        f"Artículo: {article_title}\n\n"
        f"Se adjunta el PDF relleno listo para imprimir y firmar."
    )
    msg.attach(MIMEText(body, "plain", "utf-8"))

    safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in author_name)
    attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
    attachment.add_header(
        "Content-Disposition",
        "attachment",
        filename=f"Formulario_Autor_EMERGENCIAS_{safe}.pdf",
    )
    msg.attach(attachment)

    _smtp_send(cfg, msg)


def send_invitation(to_name: str, to_email: str,
                    article_title: str, form_url: str):
    """
    Envía un email de invitación a un coautor para que rellene el formulario.
    """
    cfg = _get_smtp_cfg()

    msg = MIMEMultipart()
    msg["From"]    = cfg["user"]
    msg["To"]      = to_email
    msg["Date"]    = formatdate(localtime=True)
    msg["Subject"] = "Solicitud de firma – Responsabilidades del Autor – EMERGENCIAS"

    body = f"""Estimado/a {to_name},

Como coautor/a del siguiente artículo enviado a la revista EMERGENCIAS:

  "{article_title}"

te pedimos que rellenes el Documento de Responsabilidades del Autor mediante el
formulario web que encontrarás en el siguiente enlace:

  {form_url}

Solo necesitas introducir tu nombre, email y teléfono. El resto del formulario
se completa automáticamente. Descarga el PDF resultante, imprímelo, fírmalo a
mano y envíalo a: carmen.ibanez@semes.org

Gracias por tu colaboración.

Un saludo,
Dr. César Carballo
Servicio de Urgencias – Hospital Universitario La Paz
"""
    msg.attach(MIMEText(body, "plain", "utf-8"))
    _smtp_send(cfg, msg)


def _smtp_send(cfg: dict, msg: MIMEMultipart):
    context = ssl.create_default_context()
    with smtplib.SMTP(cfg["server"], cfg["port"]) as server:
        server.ehlo()
        server.starttls(context=context)
        server.login(cfg["user"], cfg["password"])
        server.sendmail(msg["From"], msg["To"], msg.as_string())

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

# =============================================================
# Carregar variáveis de ambiente no padrão EMAIL_*
# =============================================================
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", EMAIL_USER)

# =============================================================
# Validação automática (antes de enviar)
# =============================================================
def validar_config_email():
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.error("❌ EMAIL_USER ou EMAIL_PASSWORD não configurados no .env")
        return False

    if not EMAIL_HOST:
        logger.error("❌ EMAIL_HOST não configurado no .env")
        return False

    if not EMAIL_PORT:
        logger.error("❌ EMAIL_PORT não configurado no .env")
        return False

    return True

# =============================================================
# Template de envio de e-mail de reset de senha
# =============================================================
def enviar_email_reset_senha(email_destino, nome, token):
    """
    Envia email de redefinição de senha.
    """

    if not validar_config_email():
        return False

    reset_link = f"{os.getenv('APP_BASE_URL')}/reset_password?token={token}"

    assunto = "Redefinição de senha - PETDOR"
    html = f"""
    <html>
    <body>
        <p>Olá <strong>{nome}</strong>,</p>
        <p>Você solicitou uma redefinição de senha para sua conta no <strong>PETDOR</strong>.</p>

        <p>Clique no link abaixo para redefinir sua senha:</p>

        <p><a href="{reset_link}">{reset_link}</a></p>

        <p>Este link expira em <strong>1 hora</strong>.</p>
        <br/>
        <p>Se você não fez esta solicitação, ignore esta mensagem.</p>
        <br/>
        <p>Atenciosamente,<br/>Equipe PETDOR</p>
    </body>
    </html>
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = email_destino
        msg["Subject"] = assunto

        msg.attach(MIMEText(html, "html"))

        contexto = ssl.create_default_context()

        with smtplib.SMTP(EMAIL_HOST, int(EMAIL_PORT)) as servidor:
            servidor.starttls(context=contexto)
            servidor.login(EMAIL_USER, EMAIL_PASSWORD)
            servidor.sendmail(SENDER_EMAIL, email_destino, msg.as_string())

        logger.info(f"Email de reset enviado para: {email_destino}")
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email para {email_destino}: {e}", exc_info=True)
        return False

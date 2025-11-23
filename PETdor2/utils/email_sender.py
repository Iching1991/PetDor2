import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logger = logging.getLogger(__name__)

# =============================================================
# CARREGAMENTO DE VARIÁVEIS DE AMBIENTE
# =============================================================
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", EMAIL_USER)

# URL base do app (Ex: https://petdor.streamlit.app )
APP_BASE_URL = os.getenv("APP_BASE_URL", "").rstrip("/")


# =============================================================
# VALIDAÇÃO DAS CONFIGURAÇÕES DE EMAIL
# =============================================================
def validar_config_email():
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.error("❌ EMAIL_USER ou EMAIL_PASSWORD não configurados")
        return False

    if not EMAIL_HOST:
        logger.error("❌ EMAIL_HOST não configurado")
        return False

    if not EMAIL_PORT:
        logger.error("❌ EMAIL_PORT não configurado")
        return False

    return True


# =============================================================
# ENVIO GENÉRICO
# =============================================================
def enviar_email(destino, assunto, html):
    """
    Envia email em HTML com SMTP autenticado.
    """

    if not validar_config_email():
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SENDER_EMAIL
        msg["To"] = destino
        msg["Subject"] = assunto

        msg.attach(MIMEText(html, "html"))

        contexto = ssl.create_default_context()

        with smtplib.SMTP(EMAIL_HOST, int(EMAIL_PORT)) as servidor:
            servidor.starttls(context=contexto)
            servidor.login(EMAIL_USER, EMAIL_PASSWORD)
            servidor.sendmail(SENDER_EMAIL, destino, msg.as_string())

        logger.info(f"📨 Email enviado para {destino}")
        return True

    except Exception as e:
        logger.error(f"❌ Falha ao enviar email para {destino}: {e}", exc_info=True)
        return False


# =============================================================
# 1) CONFIRMAÇÃO DE EMAIL (JWT)
# =============================================================
def enviar_email_confirmacao(email_destino, nome, token):
    link = f"{APP_BASE_URL}/confirm_email?token={token}"

    assunto = "Confirme seu cadastro - PETDOR"

    html = f"""
    <html>
    <body>
        <p>Olá, <strong>{nome}</strong>! 👋</p>

        <p>Obrigado por criar sua conta no <strong>PETDOR</strong>.</p>

        <p>Clique abaixo para confirmar seu e-mail:</p>

        <p><a href="{link}">{link}</a></p>

        <p>Se você não fez este cadastro, apenas ignore.</p>

        <br/>
        <p>Atenciosamente,<br/>Equipe PETDOR 🐾</p>
    </body>
    </html>
    """

    return enviar_email(email_destino, assunto, html)


# =============================================================
# 2) RESET DE SENHA (JWT)
# =============================================================
def enviar_email_reset_senha(email_destino, nome, token):
    link = f"{APP_BASE_URL}/reset_password?token={token}"

    assunto = "Redefinição de senha - PETDOR"

    html = f"""
    <html>
    <body>
        <p>Olá <strong>{nome}</strong>,</p>

        <p>Você solicitou a redefinição da sua senha no PETDOR.</p>

        <p>Clique no link abaixo para definir uma nova senha:</p>

        <p><a href="{link}">{link}</a></p>

        <p><b>O link expira em 1 hora.</b></p>

        <p>Se não foi você, ignore esta mensagem.</p>

        <br/>
        <p>Equipe PETDOR 🐾</p>
    </body>
    </html>
    """

    return enviar_email(email_destino, assunto, html)


# =============================================================
# 3) EMAIL DE BOAS-VINDAS
# =============================================================
def enviar_email_boas_vindas(email_destino, nome):
    assunto = "Bem-vindo ao PETDOR! 🐾"

    html = f"""
    <html>
    <body>
        <p>Olá <strong>{nome}</strong>! 😊</p>

        <p>Seja bem-vindo ao <strong>PETDOR</strong>, o sistema mais moderno de avaliação e monitoramento da dor veterinária.</p>

        <p>Agora você tem acesso a:</p>

        <ul>
            <li>✔ Avaliações completas</li>
            <li>✔ Relatórios em PDF</li>
            <li>✔ Histórico do paciente</li>
            <li>✔ Escalas validadas internacionalmente</li>
        </ul>

        <br/>
        <p>Estamos felizes em ter você com a gente!</p>

        <p>Equipe PETDOR 🐾</p>
    </body>
    </html>
    """

    return enviar_email(email_destino, assunto, html)

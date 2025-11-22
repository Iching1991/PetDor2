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
APP_BASE_URL = os.getenv("APP_BASE_URL", "")

# =============================================================
# Validação automática (antes de enviar)
# =============================================================
def validar_config_email():
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logger.error("❌ EMAIL_USER ou EMAIL_PASSWORD não configurados no ambiente")
        return False

    if not EMAIL_HOST:
        logger.error("❌ EMAIL_HOST não configurado")
        return False

    if not EMAIL_PORT:
        logger.error("❌ EMAIL_PORT não configurado")
        return False

    return True


# =============================================================
# Função genérica de envio
# =============================================================
def enviar_email(destino, assunto, html):
    """
    Envia um email genérico em HTML.
    """
    if not validar_config_email():
        return False

    try:
        msg = MIMEMultipart()
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
        logger.error(f"❌ Erro ao enviar email para {destino}: {e}", exc_info=True)
        return False


# =============================================================
# 1) Email de CONFIRMAÇÃO DE CADASTRO
# =============================================================
def enviar_email_confirmacao(email_destino, nome, token):
    link = f"{APP_BASE_URL}/confirm_email?token={token}"

    assunto = "Confirme seu cadastro - PETDOR"

    html = f"""
    <html>
    <body>
        <p>Olá, <strong>{nome}</strong>! 👋</p>

        <p>Obrigado por criar sua conta no <strong>PETDOR</strong>.</p>

        <p>Para ativar sua conta, clique no link abaixo:</p>

        <p><a href="{link}">{link}</a></p>

        <p>Se você não solicitou este cadastro, ignore este email.</p>

        <br/>
        <p>Atenciosamente,<br/>Equipe PETDOR 🐾</p>
    </body>
    </html>
    """

    return enviar_email(email_destino, assunto, html)


# =============================================================
# 2) Email de RESET DE SENHA
# =============================================================
def enviar_email_reset_senha(email_destino, nome, token):
    link = f"{APP_BASE_URL}/reset_password?token={token}"

    assunto = "Redefinição de senha - PETDOR"

    html = f"""
    <html>
    <body>
        <p>Olá <strong>{nome}</strong>,</p>

        <p>Parece que você solicitou a redefinição de senha do PETDOR.</p>

        <p>Clique no link abaixo para definir uma nova senha:</p>

        <p><a href="{link}">{link}</a></p>

        <p>O link expira em <strong>1 hora</strong>.</p>

        <br/>
        <p>Se você não fez esta solicitação, apenas ignore.</p>

        <br/>
        <p>Equipe PETDOR 🐾</p>
    </body>
    </html>
    """

    return enviar_email(email_destino, assunto, html)


# =============================================================
# 3) Email de BOAS-VINDAS
# =============================================================
def enviar_email_boas_vindas(email_destino, nome):
    assunto = "Bem-vindo ao PETDOR! 🐾"

    html = f"""
    <html>
    <body>
        <p>Olá <strong>{nome}</strong>! 😊</p>

        <p>Seja bem-vindo ao <strong>PETDOR</strong>, o sistema mais moderno para avaliação e monitoramento da dor veterinária.</p>

        <p>Agora você tem acesso a:</p>

        <ul>
            <li>✔ Avaliações profissionais completas</li>
            <li>✔ Relatórios em PDF</li>
            <li>✔ Histórico do paciente</li>
            <li>✔ Escalas validadas internacionalmente</li>
        </ul>

        <br/>
        <p>Estamos felizes em ter você conosco!</p>

        <p>Equipe PETDOR 🐾</p>
    </body>
    </html>
    """

    return enviar_email(email_destino, assunto, html)


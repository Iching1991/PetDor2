# PETdor2/utils/email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging
import streamlit as st # Para exibir mensagens de erro

logger = logging.getLogger(__name__)

def _get_email_config():
    """Retorna as configurações de e-mail do ambiente."""
    return {
        "EMAIL_HOST": os.getenv("EMAIL_HOST"),
        "EMAIL_PORT": int(os.getenv("EMAIL_PORT", 587)),
        "EMAIL_USER": os.getenv("EMAIL_USER"),
        "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD"),
        "EMAIL_SENDER": os.getenv("EMAIL_SENDER")
    }

def enviar_email(destinatario: str, assunto: str, corpo_html: str) -> tuple[bool, str]:
    """
    Envia um e-mail HTML usando as configurações do ambiente.
    Retorna (True, "Sucesso") ou (False, "Mensagem de erro").
    """
    config = _get_email_config()

    if not all([config["EMAIL_HOST"], config["EMAIL_USER"], config["EMAIL_PASSWORD"], config["EMAIL_SENDER"]]):
        msg = "Configurações de e-mail incompletas. Verifique as variáveis de ambiente (EMAIL_HOST, EMAIL_USER, EMAIL_PASSWORD, EMAIL_SENDER)."
        logger.error(msg)
        return False, msg

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = config["EMAIL_SENDER"]
        msg["To"] = destinatario
        msg["Subject"] = assunto

        part1 = MIMEText(corpo_html, "html")
        msg.attach(part1)

        with smtplib.SMTP(config["EMAIL_HOST"], config["EMAIL_PORT"]) as server:
            server.starttls()
            server.login(config["EMAIL_USER"], config["EMAIL_PASSWORD"])
            server.sendmail(config["EMAIL_SENDER"], destinatario, msg.as_string())

        logger.info(f"E-mail enviado com sucesso para {destinatario} (Assunto: {assunto})")
        return True, "E-mail enviado com sucesso."
    except smtplib.SMTPAuthenticationError as e:
        msg = f"Erro de autenticação SMTP. Verifique EMAIL_USER e EMAIL_PASSWORD. Detalhes: {e}"
        logger.error(msg, exc_info=True)
        return False, msg
    except smtplib.SMTPConnectError as e:
        msg = f"Erro de conexão SMTP. Verifique EMAIL_HOST e EMAIL_PORT. Detalhes: {e}"
        logger.error(msg, exc_info=True)
        return False, msg
    except Exception as e:
        msg = f"Erro inesperado ao enviar e-mail para {destinatario}. Detalhes: {e}"
        logger.error(msg, exc_info=True)
        return False, msg

def enviar_email_confirmacao(destinatario: str, token: str) -> tuple[bool, str]:
    """Envia um e-mail de confirmação de conta."""
    # URL base do seu aplicativo Streamlit
    # No Streamlit Cloud, a URL é gerada automaticamente.
    # Para desenvolvimento local, pode ser "http://localhost:8501"
    # Para deploy, use a URL do seu app Streamlit Cloud
    app_url = os.getenv("STREAMLIT_APP_URL", "http://localhost:8501") # Adicione STREAMLIT_APP_URL nas suas variáveis de ambiente
    confirm_link = f"{app_url}?token={token}&action=confirm_email"

    assunto = "Confirme sua conta PETDOR"
    corpo_html = f"""
    <html>
        <body>
            <p>Olá,</p>
            <p>Obrigado por se registrar no PETDOR! Por favor, clique no link abaixo para confirmar seu e-mail:</p>
            <p><a href="{confirm_link}">Confirmar E-mail</a></p>
            <p>Se você não solicitou este e-mail, por favor, ignore-o.</p>
            <p>Atenciosamente,</p>
            <p>Equipe PETDOR</p>
        </body>
    </html>
    """
    return enviar_email(destinatario, assunto, corpo_html)

def enviar_email_recuperacao_senha(destinatario: str, token: str) -> tuple[bool, str]:
    """Envia um e-mail para recuperação de senha."""
    app_url = os.getenv("STREAMLIT_APP_URL", "http://localhost:8501")
    reset_link = f"{app_url}?token={token}&action=reset_password"

    assunto = "Redefinição de Senha PETDOR"
    corpo_html = f"""
    <html>
        <body>
            <p>Olá,</p>
            <p>Você solicitou a redefinição de sua senha no PETDOR. Por favor, clique no link abaixo para redefinir sua senha:</p>
            <p><a href="{reset_link}">Redefinir Senha</a></p>
            <p>Este link é válido por 30 minutos.</p>
            <p>Se você não solicitou a redefinição de senha, por favor, ignore este e-mail.</p>
            <p>Atenciosamente,</p>
            <p>Equipe PETDOR</p>
        </body>
    </html>
    """
    return enviar_email(destinatario, assunto, corpo_html)

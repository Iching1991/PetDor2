# PETdor2/backend/utils/email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import logging

# Importa as variáveis diretamente do módulo config
from backend.utils.config import (
    SMTP_SERVIDOR,
    SMTP_PORTA,
    SMTP_REMETENTE,
    SMTP_EMAIL,
    SMTP_SENHA,
    SMTP_USAR_SSL,
    STREAMLIT_APP_URL # Se precisar da URL do app para montar links
)

logger = logging.getLogger(__name__)

def enviar_email(destinatario, assunto, corpo_html):
    """
    Envia um e-mail HTML usando as configurações SMTP.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_REMETENTE
        msg["To"] = destinatario
        msg["Subject"] = assunto

        # Anexa a versão HTML do corpo
        msg.attach(MIMEText(corpo_html, "html"))

        with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA) as server:
            if SMTP_USAR_SSL:
                server.starttls()  # Inicia TLS para conexão segura
            server.login(SMTP_EMAIL, SMTP_SENHA)
            server.sendmail(SMTP_REMETENTE, destinatario, msg.as_string())
        logger.info(f"E-mail enviado para {destinatario} com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro ao enviar e-mail para {destinatario}: {e}")
        return False

def enviar_email_confirmacao(destinatario, token_confirmacao):
    """
    Envia um e-mail para confirmação de conta.
    """
    link_confirmacao = f"{STREAMLIT_APP_URL}?action=confirm_email&token={token_confirmacao}"
    assunto = "Confirmação de Cadastro PETDOR"
    corpo_html = f"""
    <html>
        <body>
            <p>Olá,</p>
            <p>Obrigado por se cadastrar no PETDOR!</p>
            <p>Por favor, clique no link abaixo para confirmar seu e-mail:</p>
            <p><a href="{link_confirmacao}">Confirmar E-mail</a></p>
            <p>Se você não se cadastrou no PETDOR, por favor, ignore este e-mail.</p>
            <p>Atenciosamente,</p>
            <p>Equipe PETDOR</p>
        </body>
    </html>
    """
    return enviar_email(destinatario, assunto, corpo_html)

def enviar_email_recuperacao_senha(destinatario, token_reset):
    """
    Envia um e-mail para recuperação de senha.
    """
    link_reset = f"{STREAMLIT_APP_URL}?action=reset_password&token={token_reset}"
    assunto = "Recuperação de Senha PETDOR"
    corpo_html = f"""
    <html>
        <body>
            <p>Olá,</p>
            <p>Você solicitou a recuperação de senha para sua conta PETDOR.</p>
            <p>Por favor, clique no link abaixo para redefinir sua senha:</p>
            <p><a href="{link_reset}">Redefinir Senha</a></p>
            <p>Este link é válido por um tempo limitado. Se você não solicitou a recuperação de senha, por favor, ignore este e-mail.</p>
            <p>Atenciosamente,</p>
            <p>Equipe PETDOR</p>
        </body>
    </html>
    """
    return enviar_email(destinatario, assunto, corpo_html)

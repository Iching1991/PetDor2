# PETdor2/backend/utils/email_sender.py
"""
Módulo para envio de e-mails - confirmação de conta e recuperação de senha.
Compatível com SMTP (SSL/STARTTLS).
"""

import sys
import os
import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Corrige importações absolutas para Streamlit Cloud ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim correção ---

from utils.config import SMTP_SERVIDOR, SMTP_PORTA, SMTP_EMAIL, SMTP_SENHA, SMTP_USAR_SSL

logger = logging.getLogger(__name__)

# ============================================================
# Função genérica de envio de e-mail
# ============================================================
def enviar_email(destinatario: str, assunto: str, corpo_html: str) -> tuple[bool, str]:
    """Envia um e-mail HTML usando configurações do config.py."""
    if not all([SMTP_SERVIDOR, SMTP_EMAIL, SMTP_SENHA, SMTP_PORTA]):
        logger.error("Configurações SMTP ausentes. Não é possível enviar e-mail.")
        return False, "Erro: configuração SMTP ausente no sistema."

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_EMAIL
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo_html, "html"))

    try:
        context = ssl.create_default_context()

        if SMTP_USAR_SSL:
            with smtplib.SMTP_SSL(SMTP_SERVIDOR, SMTP_PORTA, context=context) as server:
                server.login(SMTP_EMAIL, SMTP_SENHA)
                server.sendmail(SMTP_EMAIL, destinatario, msg.as_string())
        else:
            with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA) as server:
                server.starttls(context=context)
                server.login(SMTP_EMAIL, SMTP_SENHA)
                server.sendmail(SMTP_EMAIL, destinatario, msg.as_string())

        logger.info(f"E-mail enviado com sucesso para {destinatario}. Assunto: {assunto}")
        return True, "E-mail enviado com sucesso."

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Erro de autenticação SMTP: {e}")
        return False, "Falha na autenticação SMTP. Verifique usuário e senha."
    except smtplib.SMTPConnectError as e:
        logger.error(f"Erro de conexão com o servidor SMTP: {e}")
        return False, "Não foi possível conectar ao servidor SMTP."
    except Exception as e:
        logger.error(f"Erro inesperado ao enviar e-mail: {e}")
        return False, f"Erro ao enviar e-mail: {e}"

# ============================================================
# E-mail de confirmação de conta
# ============================================================
def enviar_email_confirmacao(destinatario_email: str, nome_usuario: str, link_confirmacao: str):
    """Envia e-mail de confirmação de cadastro."""
    assunto = "Confirme seu E-mail - PETDOR"
    corpo_html = f"""
    <html>
        <body>
            <h3>Olá, {nome_usuario}!</h3>
            <p>Obrigado por criar sua conta no <strong>PETDOR</strong>.</p>
            <p>Clique no botão abaixo para confirmar seu e-mail:</p>
            <a href="{link_confirmacao}"
               style="padding: 12px 20px; background-color: #1a7a6e; 
                      color: white; text-decoration: none; border-radius: 6px;">
               Confirmar E-mail
            </a>
            <p>Se você não solicitou este cadastro, ignore este e-mail.</p>
            <br>
            <p>🐾 Equipe PETDOR</p>
        </body>
    </html>
    """
    return enviar_email(destinatario_email, assunto, corpo_html)

# ============================================================
# E-mail de recuperação de senha
# ============================================================
def enviar_email_recuperacao_senha(destinatario_email: str, nome_usuario: str, link_reset: str):
    """Envia e-mail com link para redefinir a senha."""
    assunto = "Redefinição de Senha - PETDOR"
    corpo_html = f"""
    <html>
        <body>
            <h3>Olá, {nome_usuario}!</h3>
            <p>Recebemos um pedido para redefinir sua senha.</p>
            <p>Clique no link abaixo para criar uma nova senha:</p>
            <a href="{link_reset}"
               style="padding: 12px 20px; background-color: #1a7a6e; 
                      color: white; text-decoration: none; border-radius: 6px;">
               Redefinir Senha
            </a>
            <p>O link expira em <b>1 hora</b>.</p>
            <p>Se você não solicitou isso, ignore este e-mail.</p>
            <br>
            <p>🐾 Equipe PETDOR</p>
        </body>
    </html>
    """
    return enviar_email(destinatario_email, assunto, corpo_html)

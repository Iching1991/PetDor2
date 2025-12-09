# PetDor2/backend/utils/email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Importa variáveis SMTP do config
from backend.utils.config import (
    SMTP_SERVIDOR,
    SMTP_PORTA,
    SMTP_EMAIL,
    SMTP_SENHA,
    SMTP_USAR_SSL,
)


def _enviar_email(destinatario: str, assunto: str, texto: str, html: str) -> Tuple[bool, str]:
    """
    Função interna responsável por montar e enviar qualquer e-mail.
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_EMAIL
        msg["To"] = destinatario
        msg["Subject"] = assunto

        msg.attach(MIMEText(texto, "plain"))
        msg.attach(MIMEText(html, "html"))

        # Conexão com SMTP
        if SMTP_USAR_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVIDOR, SMTP_PORTA)
        else:
            server = smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA)
            server.starttls()

        with server:
            server.login(SMTP_EMAIL, SMTP_SENHA)
            server.sendmail(SMTP_EMAIL, destinatario, msg.as_string())

        logger.info(f"[EMAIL OK] Enviado para {destinatario} | Assunto: {assunto}")
        return True, "E-mail enviado com sucesso."

    except Exception as e:
        logger.error(f"[EMAIL ERRO] Falha ao enviar para {destinatario}: {e}", exc_info=True)
        return False, f"Erro ao enviar e-mail: {e}"


# ================================
#  FUNÇÕES PÚBLICAS
# ================================

def enviar_email_confirmacao_generico(destinatario_email: str, assunto: str, corpo_html: str, corpo_texto: str):
    return _enviar_email(destinatario_email, assunto, corpo_texto, corpo_html)


def enviar_email_recuperacao_senha(destinatario_email: str, link_recuperacao: str):
    """
    Implementação REAL que estava faltando!
    """

    assunto = "Recuperação de Senha - PetDor"

    corpo_texto = f"""
Olá! Você solicitou a recuperação da sua senha.

Para redefinir, clique no link abaixo:
{link_recuperacao}

Se não foi você, apenas ignore este e-mail.
    """

    corpo_html = f"""
<p>Olá! Você solicitou a recuperação de senha.</p>
<p>Clique no botão abaixo para redefinir:</p>
<p><a href="{link_recuperacao}" style="padding:10px 20px;background:#4CAF50;color:white;text-decoration:none;border-radius:6px;">Redefinir Senha</a></p>
<p>Se não foi você, ignore este e-mail.</p>
"""

    return _enviar_email(destinatario_email, assunto, corpo_texto, corpo_html)

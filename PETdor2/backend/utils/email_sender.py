# PETdor2/backend/utils/email_sender.py

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Tuple

from backend.utils.config import (
    SMTP_SERVIDOR,
    SMTP_PORTA,
    SMTP_EMAIL,
    SMTP_SENHA,
    SMTP_USAR_SSL,
)

logger = logging.getLogger(__name__)


# ============================================================
#   FUNÇÃO INTERNA DE ENVIO
# ============================================================

def _enviar_email(destinatario: str, assunto: str, texto: str, html: str) -> Tuple[bool, str]:
    """Função interna para envio de e-mails (HTML + texto)."""

    if not destinatario:
        return False, "Endereço de e-mail do destinatário está vazio."

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = SMTP_EMAIL
        msg["To"] = destinatario
        msg["Subject"] = assunto

        msg.attach(MIMEText(texto, "plain"))
        msg.attach(MIMEText(html, "html"))

        # Definição do servidor
        if SMTP_USAR_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVIDOR, SMTP_PORTA)
        else:
            server = smtplib.SMTP(SMTP_SERVIDOR, SMTP_PORTA)
            server.starttls()

        with server:
            server.login(SMTP_EMAIL, SMTP_SENHA)
            server.sendmail(SMTP_EMAIL, destinatario, msg.as_string())

        logger.info(f"📧 Email enviado com sucesso → {destinatario}")
        return True, "E-mail enviado com sucesso."

    except Exception as e:
        logger.error(f"❌ Erro ao enviar e-mail para {destinatario}: {e}", exc_info=True)
        return False, f"Erro ao enviar e-mail: {e}"


# ============================================================
#   FUNÇÕES PÚBLICAS
# ============================================================

def enviar_email_confirmacao_generico(destinatario_email: str, assunto: str, corpo_html: str, corpo_texto: str):
    """E-mail genérico usado pelo sistema."""
    return _enviar_email(destinatario_email, assunto, corpo_texto, corpo_html)


def enviar_email_recuperacao_senha(destinatario_email: str, link_recuperacao: str):
    """Envia o link de recuperação de senha."""

    assunto = "Recuperação de Senha - PetDor"

    corpo_texto = (
        "Olá! Você solicitou a recuperação da sua senha.\n\n"
        f"Acesse o link abaixo:\n{link_recuperacao}\n\n"
        "Se não foi você, ignore esta mensagem."
    )

    corpo_html = f"""
    <p>Olá! Você solicitou a recuperação da sua senha.</p>
    <p>Clique abaixo para redefinir:</p>
    <p>
        <a href="{link_recuperacao}" 
           style="padding:10px 20px;background:#4CAF50;color:white;text-decoration:none;
                  border-radius:6px;font-weight:bold;">
           Redefinir Senha
        </a>
    </p>
    """

    return _enviar_email(destinatario_email, assunto, corpo_texto, corpo_html)


__all__ = [
    "enviar_email_confirmacao_generico",
    "enviar_email_recuperacao_senha",
]

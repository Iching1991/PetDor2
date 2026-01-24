"""
Confirmação de e-mail de usuários - PETDor
Fluxo simples, seguro e compatível com Supabase REST + RLS
"""

import logging
import uuid
from datetime import datetime
from typing import Tuple, Optional

from backend.database import (
    supabase_table_select,
    supabase_table_update,
)
from backend.utils.email_sender import enviar_email_confirmacao_generico
from backend.utils.config import STREAMLIT_APP_URL

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"

# ==========================================================
# 1️⃣ Gerar token e enviar e-mail
# ==========================================================

def enviar_email_confirmacao(email: str, nome: str, usuario_id: str) -> Tuple[bool, str]:
    """
    Gera token UUID, salva no banco e envia e-mail de confirmação.
    """
    try:
        token = str(uuid.uuid4())

        # Salva token no banco
        atualizado = supabase_table_update(
            table=TABELA_USUARIOS,
            filters={"id": usuario_id},
            data={
                "email_confirm_token": token,
                "atualizado_em": datetime.utcnow().isoformat(),
            },
        )

        if atualizado is None:
            return False, "Erro ao gerar token de confirmação."

        link = f"{STREAMLIT_APP_URL}?action=confirm_email&token={token}"

        assunto = "Confirme seu e-mail - PETDor"

        corpo_html = f"""
        <html>
          <body>
            <p>Olá, <strong>{nome}</strong>!</p>
            <p>Para ativar sua conta no PETDor, clique no link abaixo:</p>
            <p><a href="{link}">🔗 Confirmar meu e-mail</a></p>
            <br>
            <p>Se você não criou esta conta, ignore este e-mail.</p>
          </body>
        </html>
        """

        corpo_texto = f"""
Olá, {nome}!

Para ativar sua conta no PETDor, acesse o link abaixo:

{link}

Se você não criou esta conta, ignore este e-mail.
"""

        ok_email, msg_email = enviar_email_confirmacao_generico(
            destinatario_email=email,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=corpo_texto,
        )

        if not ok_email:
            logger.error(f"Erro ao enviar e-mail: {msg_email}")
            return False, "Erro ao enviar e-mail de confirmação."

        logger.info(f"E-mail de confirmação enviado para {email}")
        return True, "E-mail de confirmação enviado."

    except Exception as e:
        logger.exception("Erro ao enviar e-mail de confirmação")
        return False, "Erro interno ao enviar e-mail."


# ==========================================================
# 2️⃣ Validar token
# ==========================================================

def validar_token_confirmacao(token: str) -> Tuple[bool, Optional[str]]:
    """
    Valida token de confirmação.
    """
    try:
        resultado = supabase_table_select(
            table=TABELA_USUARIOS,
            filters={
                "email_confirm_token": token,
                "ativo": True,
            },
            limit=1,
        )

        if not resultado:
            return False, None

        return True, resultado[0]["id"]

    except Exception as e:
        logger.error("Erro ao validar token", exc_info=True)
        return False, None


# ==========================================================
# 3️⃣ Confirmar e-mail
# ==========================================================

def confirmar_email(usuario_id: str) -> Tuple[bool, str]:
    """
    Confirma o e-mail do usuário e invalida o token.
    """
    try:
        atualizado = supabase_table_update(
            table=TABELA_USUARIOS,
            filters={"id": usuario_id},
            data={
                "email_confirmado": True,
                "email_confirm_token": None,
            },
        )

        if atualizado is None:
            return False, "Erro ao confirmar e-mail."

        return True, "E-mail confirmado com sucesso."

    except Exception as e:
        logger.error("Erro ao confirmar e-mail", exc_info=True)
        return False, "Erro interno ao confirmar e-mail."

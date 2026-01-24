# PETdor2/pages/recuperar_senha.py
"""
Reset e recuperação de senha
Compatível com Supabase REST + RLS
"""

import logging
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Tuple, Dict, Any

from backend.database import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

logger = logging.getLogger(__name__)


# ==========================================================
# Utils
# ==========================================================

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


# ==========================================================
# Solicitar reset de senha (ENVIA E-MAIL)
# ==========================================================

def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Cria token de reset de senha e envia link por e-mail.
    """
    try:
        # Busca usuário
        usuarios = supabase_table_select(
            table="usuarios",
            filters={"email": email.lower(), "ativo": True},
            limit=1,
        )

        if not usuarios:
            # Não revela se o e-mail existe (segurança)
            return True, "Se o e-mail existir, enviaremos um link de recuperação."

        usuario = usuarios[0]
        usuario_id = usuario["id"]

        # Gera token
        token = str(uuid.uuid4())

        # Salva token
        supabase_table_insert(
            table="tokens_reset_senha",
            data={
                "usuario_id": usuario_id,
                "email": email.lower(),
                "token": token,
                "criado_em": datetime.now(timezone.utc).isoformat(),
            },
        )

        # Envia e-mail
        from backend.utils.email_sender import enviar_email_generico
        from backend.utils.config import STREAMLIT_APP_URL

        link = f"{STREAMLIT_APP_URL}?pagina=password_reset&token={token}"

        assunto = "🔐 Redefinição de senha - PETDor"
        corpo = f"""
Olá!

Recebemos uma solicitação para redefinir sua senha no PETDor.

Clique no link abaixo para criar uma nova senha:
{link}

Se você não solicitou isso, ignore este e-mail.
"""

        enviar_email_generico(
            destinatario=email,
            assunto=assunto,
            corpo_texto=corpo,
        )

        logger.info(f"Token de reset enviado para {email}")
        return True, "Se o e-mail existir, enviaremos um link de recuperação."

    except Exception as e:
        logger.error(f"Erro ao solicitar reset de senha: {e}", exc_info=True)
        return False, "Erro interno ao processar solicitação."


# ==========================================================
# Validar token de reset
# ==========================================================

def validar_token_reset(token: str) -> Tuple[bool, Dict[str, Any]]:
    try:
        resultado = supabase_table_select(
            table="tokens_reset_senha",
            filters={"token": token},
            limit=1,
        )

        if not resultado:
            return False, {"erro": "Token inválido ou expirado."}

        registro = resultado[0]

        return True, {
            "email": registro["email"],
            "usuario_id": registro["usuario_id"],
        }

    except Exception as e:
        logger.error(f"Erro ao validar token reset: {e}", exc_info=True)
        return False, {"erro": "Erro interno."}


# ==========================================================
# Redefinir senha com token
# ==========================================================

def redefinir_senha_com_token(token: str, nova_senha: str) -> Tuple[bool, str]:
    try:
        valido, dados = validar_token_reset(token)

        if not valido:
            return False, dados.get("erro", "Token inválido.")

        senha_hash = hash_senha(nova_senha)

        atualizado = supabase_table_update(
            table="usuarios",
            filters={"id": dados["usuario_id"]},
            data={"senha_hash": senha_hash},
        )

        if atualizado is None:
            return False, "Erro ao atualizar senha."

        # Invalida token
        supabase_table_delete(
            table="tokens_reset_senha",
            filters={"token": token},
        )

        return True, "Senha redefinida com sucesso."

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}", exc_info=True)
        return False, "Erro interno ao redefinir senha."

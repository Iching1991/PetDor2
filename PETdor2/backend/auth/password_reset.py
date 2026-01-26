# PETdor2/backend/auth/password_reset.py
"""
Módulo de recuperação de senha.
Compatível com Supabase REST + RLS
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any

from backend.database import (
    supabase_table_select,
    supabase_table_update,
)
from backend.auth.security import gerar_hash_senha
from backend.utils.email_sender import enviar_email_recuperacao_senha

logger = logging.getLogger(__name__)


# ==========================================================
# Solicitar redefinição de senha
# ==========================================================

def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Gera token, salva no usuário e envia e-mail.
    Nunca revela se o e-mail existe.
    """
    try:
        usuarios = supabase_table_select(
            table="usuarios",
            filters={"email": email.lower()},
            limit=1
        )

        # Segurança: resposta sempre genérica
        if not usuarios:
            return True, "Se o e-mail estiver cadastrado, você receberá o link."

        usuario = usuarios[0]
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)

        supabase_table_update(
            table="usuarios",
            filters={"id": usuario["id"]},
            data={
                "reset_password_token": token,
                "reset_password_expires": expires.isoformat(),
            }
        )

        link = f"https://petdor.streamlit.app/resetar_senha?token={token}"

        enviar_email_recuperacao_senha(
            destinatario_email=email,
            link_recuperacao=link
        )

        return True, "Se o e-mail estiver cadastrado, você receberá o link."

    except Exception:
        logger.error("Erro ao solicitar reset de senha", exc_info=True)
        return False, "Erro interno ao solicitar recuperação."


# ==========================================================
# Validar token
# ==========================================================

def validar_token_reset(token: str) -> Tuple[bool, Dict[str, Any]]:
    try:
        usuarios = supabase_table_select(
            table="usuarios",
            filters={"reset_password_token": token},
            limit=1
        )

        if not usuarios:
            return False, {"erro": "Token inválido ou expirado."}

        usuario = usuarios[0]
        expires = datetime.fromisoformat(
            usuario["reset_password_expires"]
        ).replace(tzinfo=timezone.utc)

        if expires < datetime.now(timezone.utc):
            return False, {"erro": "Token expirado."}

        return True, {
            "usuario_id": usuario["id"],
            "email": usuario["email"]
        }

    except Exception:
        logger.error("Erro ao validar token", exc_info=True)
        return False, {"erro": "Erro interno."}


# ==========================================================
# Redefinir senha
# ==========================================================

def redefinir_senha_com_token(token: str, nova_senha: str) -> Tuple[bool, str]:
    try:
        valido, dados = validar_token_reset(token)
        if not valido:
            return False, dados["erro"]

        if len(nova_senha) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres."

        supabase_table_update(
            table="usuarios",
            filters={"id": dados["usuario_id"]},
            data={
                "senha_hash": gerar_hash_senha(nova_senha),
                "reset_password_token": None,
                "reset_password_expires": None,
            }
        )

        return True, "Senha redefinida com sucesso."

    except Exception:
        logger.error("Erro ao redefinir senha", exc_info=True)
        return False, "Erro interno ao redefinir senha."

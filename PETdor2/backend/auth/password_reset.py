# PETdor2/backend/auth/password_reset.py
"""
Módulo de recuperação de senha.
Gerencia tokens JWT e redefinição de senha.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any

# Importações absolutas (evitam import circular)
from backend.auth.security import (
    gerar_token_reset_senha,
    validar_token_reset_senha,
    hash_password,
)
from backend.utils.email_sender import enviar_email_recuperacao_senha
from backend.database.supabase_client import get_supabase

logger = logging.getLogger(__name__)


def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """Gera token, salva no banco e envia o e-mail."""
    try:
        supabase = get_supabase()

        response = (
            supabase.from_("usuarios")
            .select("id, nome, email")
            .eq("email", email.lower())
            .single()
            .execute()
        )

        usuario = response.data

        # Por segurança, nunca dizer se existe ou não
        if not usuario:
            return True, "Se o e-mail estiver cadastrado, você receberá o link."

        usuario_id = usuario["id"]
        nome_usuario = usuario["nome"]

        # Token JWT
        token = gerar_token_reset_senha(usuario_id, email)

        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        supabase.from_("usuarios").update({
            "reset_password_token": token,
            "reset_password_expires": expires_at.isoformat()
        }).eq("id", usuario_id).execute()

        # Enviar e-mail
        ok_email, msg_email = enviar_email_recuperacao_senha(
            destinatario_email=email,
            destinatario_nome=nome_usuario,
            token=token
        )

        if not ok_email:
            return False, "Erro ao enviar e-mail de recuperação."

        return True, "Se o e-mail estiver cadastrado, você receberá o link."

    except Exception as e:
        logger.error(f"Erro em solicitar_reset_senha: {e}", exc_info=True)
        return False, "Erro interno ao solicitar recuperação."


def validar_token_reset(token: str) -> Tuple[bool, Dict[str, Any]]:
    """Valida estrutura do JWT e consistência com o banco."""
    try:
        payload = validar_token_reset_senha(token)
        if not payload:
            return False, {"erro": "Token inválido ou expirado."}

        usuario_id = payload.get("usuario_id")
        email_jwt = payload.get("email")

        supabase = get_supabase()
        resp = (
            supabase.from_("usuarios")
            .select("id, email, reset_password_token, reset_password_expires")
            .eq("id", usuario_id)
            .single()
            .execute()
        )

        usuario = resp.data
        if not usuario:
            return False, {"erro": "Token inválido."}

        # Token no banco deve ser igual
        if usuario["reset_password_token"] != token:
            return False, {"erro": "Token inválido ou já utilizado."}

        # Expiração
        expires = datetime.fromisoformat(usuario["reset_password_expires"]).replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            return False, {"erro": "Token expirado."}

        return True, {"email": usuario["email"], "usuario_id": usuario["id"]}

    except Exception as e:
        logger.error(f"Erro em validar_token_reset: {e}", exc_info=True)
        return False, {"erro": "Erro interno ao validar token."}


def redefinir_senha_com_token(token: str, nova_senha: str) -> Tuple[bool, str]:
    """Redefine a senha se o token for válido."""
    try:
        valido, dados = validar_token_reset(token)
        if not valido:
            return False, dados["erro"]

        usuario_id = dados["usuario_id"]
        email = dados["email"]

        if len(nova_senha) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres."

        hashed = hash_password(nova_senha)

        supabase = get_supabase()
        supabase.from_("usuarios").update({
            "senha_hash": hashed,
            "reset_password_token": None,
            "reset_password_expires": None
        }).eq("id", usuario_id).execute()

        return True, "Senha redefinida com sucesso."

    except Exception as e:
        logger.error(f"Erro em redefinir_senha_com_token: {e}", exc_info=True)
        return False, "Erro interno ao redefinir senha."


__all__ = [
    "solicitar_reset_senha",
    "validar_token_reset",
    "redefinir_senha_com_token",
]

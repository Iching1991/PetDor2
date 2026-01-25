# PETdor2/backend/auth/password_reset.py
"""
Módulo de recuperação de senha.
Gerencia geração, validação e utilização de tokens de reset.
"""

import logging
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict, Any

from backend.auth.security import gerar_token_reset_senha
from backend.utils.email_sender import enviar_email_recuperacao_senha
from backend.database.supabase_client import get_supabase

logger = logging.getLogger(__name__)


# ==========================================================
# Utils
# ==========================================================

def hash_senha(senha: str) -> str:
    """Gera hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


# ==========================================================
# Solicitar redefinição de senha
# ==========================================================

def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Gera token de recuperação, salva no banco e envia o e-mail.
    Nunca revela se o e-mail existe ou não.
    """
    try:
        supabase = get_supabase()

        response = (
            supabase
            .from_("usuarios")
            .select("id, email")
            .eq("email", email.lower())
            .single()
            .execute()
        )

        usuario = response.data

        # Segurança: nunca revelar existência do e-mail
        if not usuario:
            return True, "Se o e-mail estiver cadastrado, você receberá o link."

        token = gerar_token_reset_senha()
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        supabase.from_("usuarios").update({
            "reset_password_token": token,
            "reset_password_expires": expires_at.isoformat()
        }).eq("id", usuario["id"]).execute()

        link = f"https://petdor.streamlit.app/resetar_senha?token={token}"

        ok, msg = enviar_email_recuperacao_senha(
            destinatario_email=email,
            link_recuperacao=link
        )

        if not ok:
            logger.error(msg)
            return False, "Erro ao enviar e-mail de recuperação."

        return True, "Se o e-mail estiver cadastrado, você receberá o link."

    except Exception as e:
        logger.error("Erro ao solicitar reset de senha", exc_info=True)
        return False, "Erro interno ao solicitar recuperação."


# ==========================================================
# Validar token de redefinição
# ==========================================================

def validar_token_reset(token: str) -> Tuple[bool, Dict[str, Any]]:
    try:
        supabase = get_supabase()

        response = (
            supabase
            .from_("usuarios")
            .select("id, email, reset_password_token, reset_password_expires")
            .eq("reset_password_token", token)
            .single()
            .execute()
        )

        usuario = response.data
        if not usuario:
            return False, {"erro": "Token inválido ou expirado."}

        expires = datetime.fromisoformat(
            usuario["reset_password_expires"]
        ).replace(tzinfo=timezone.utc)

        if expires < datetime.now(timezone.utc):
            return False, {"erro": "Token expirado."}

        return True, {
            "usuario_id": usuario["id"],
            "email": usuario["email"]
        }

    except Exception as e:
        logger.error("Erro ao validar token de reset", exc_info=True)
        return False, {"erro": "Erro interno ao validar token."}


# ==========================================================
# Redefinir senha com token
# ==========================================================

def redefinir_senha_com_token(token: str, nova_senha: str) -> Tuple[bool, str]:
    try:
        valido, dados = validar_token_reset(token)

        if not valido:
            return False, dados.get("erro", "Token inválido.")

        if len(nova_senha) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres."

        senha_hash = hash_senha(nova_senha)

        supabase = get_supabase()
        supabase.from_("usuarios").update({
            "senha_hash": senha_hash,
            "reset_password_token": None,
            "reset_password_expires": None
        }).eq("id", dados["usuario_id"]).execute()

        return True, "Senha redefinida com sucesso."

    except Exception as e:
        logger.error("Erro ao redefinir senha", exc_info=True)
        return False, "Erro interno ao redefinir senha."


__all__ = [
    "solicitar_reset_senha",
    "validar_token_reset",
    "redefinir_senha_com_token",
]

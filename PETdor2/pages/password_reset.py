# PETdor2/pages/password_reset.py
"""
Reset de senha de usuários
Compatível com Supabase REST + RLS
"""

import logging
import hashlib
from typing import Tuple, Dict, Any

from backend.database import (
    supabase_table_select,
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
# Validar token de reset
# ==========================================================

def validar_token_reset(token: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Valida token de redefinição de senha.

    Retorna:
        (True, {email, usuario_id}) se válido
        (False, {erro}) se inválido
    """
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
            "email": registro.get("email"),
            "usuario_id": registro.get("usuario_id"),
        }

    except Exception as e:
        logger.error(f"Erro ao validar token de reset: {e}", exc_info=True)
        return False, {"erro": "Erro interno ao validar token."}


# ==========================================================
# Redefinir senha com token
# ==========================================================

def redefinir_senha_com_token(token: str, nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine a senha do usuário usando token válido.
    """
    try:
        valido, dados = validar_token_reset(token)

        if not valido:
            return False, dados.get("erro", "Token inválido.")

        usuario_id = dados["usuario_id"]
        senha_hash = hash_senha(nova_senha)

        # Atualiza senha
        atualizado = supabase_table_update(
            table="usuarios",
            filters={"id": usuario_id},
            data={"senha_hash": senha_hash},
        )

        if atualizado is None:
            return False, "Erro ao atualizar senha."

        # Remove token (invalida)
        supabase_table_delete(
            table="tokens_reset_senha",
            filters={"token": token},
        )

        logger.info(f"Senha redefinida com sucesso para usuario_id={usuario_id}")
        return True, "Senha redefinida com sucesso."

    except Exception as e:
        logger.error(f"Erro ao redefinir senha: {e}", exc_info=True)
        return False, "Erro interno ao redefinir senha."

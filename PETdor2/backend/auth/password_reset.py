"""
Reset de senha via Supabase Auth
"""

import streamlit as st
import logging
from backend.database.supabase_client import supabase

logger = logging.getLogger(__name__)


# ==========================================================
# Solicitar reset
# ==========================================================
def solicitar_reset_senha(email: str):

    try:
        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": st.secrets["app"]["STREAMLIT_APP_URL"]
                + "/redefinir_senha"
            },
        )

        return True, "Link enviado para seu e-mail."

    except Exception as e:
        logger.exception("Erro reset senha")
        return False, str(e)


# ==========================================================
# Redefinir senha
# ==========================================================
def redefinir_senha(nova_senha: str):

    try:
        supabase.auth.update_user(
            {
                "password": nova_senha
            }
        )

        return True, "Senha redefinida com sucesso."

    except Exception as e:
        logger.exception("Erro redefinir senha")
        return False, str(e)

"""
Reset de senha via Supabase Auth — PETDor2
Responsável por:

• Solicitar envio de e-mail de recuperação
• Redefinir senha do usuário autenticado via token
"""

import streamlit as st
import logging
from typing import Tuple

from backend.database.supabase_client import supabase

logger = logging.getLogger(__name__)


# ==========================================================
# 📧 SOLICITAR RESET DE SENHA
# ==========================================================
def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Envia e-mail de redefinição de senha via Supabase Auth.

    O Supabase envia automaticamente um link contendo o token
    para o e-mail informado.

    Returns:
        (sucesso: bool, mensagem: str)
    """
    try:
        email = email.strip().lower()

        if not email:
            return False, "Informe um e-mail válido."

        redirect_url = (
            st.secrets["app"]["STREAMLIT_APP_URL"]
            + "/redefinir_senha"
        )

        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": redirect_url
            },
        )

        logger.info(f"📧 Reset de senha solicitado para: {email}")

        return True, (
            "Se o e-mail estiver cadastrado, você receberá "
            "um link para redefinir sua senha."
        )

    except Exception as e:
        logger.exception("❌ Erro ao solicitar reset de senha")
        return False, f"Erro ao solicitar recuperação: {e}"


# ==========================================================
# 🔐 REDEFINIR SENHA
# ==========================================================
def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine a senha do usuário autenticado via token do Supabase.

    IMPORTANTE:
    • O token já vem autenticado quando o usuário abre o link do e-mail.
    • Não é necessário receber token como parâmetro.

    Args:
        nova_senha: Nova senha do usuário

    Returns:
        (sucesso: bool, mensagem: str)
    """

    try:
        # --------------------------------------------------
        # Validações
        # --------------------------------------------------
        if not nova_senha:
            return False, "Informe a nova senha."

        if len(nova_senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        # (Opcional — fortalecer segurança)
        if len(nova_senha) < 8:
            logger.warning("⚠️ Senha redefinida com menos de 8 caracteres")

        # --------------------------------------------------
        # Verificar sessão ativa
        # --------------------------------------------------
        session = supabase.auth.get_session()

        if not session or not session.user:
            return False, (
                "Sessão inválida ou expirada. "
                "Solicite um novo link de redefinição."
            )

        user_id = session.user.id
        logger.info(f"🔐 Redefinindo senha para user_id: {user_id}")

        # --------------------------------------------------
        # Atualizar senha
        # --------------------------------------------------
        supabase.auth.update_user({
            "password": nova_senha
        })

        logger.info("✅ Senha redefinida com sucesso")

        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.exception("❌ Erro ao redefinir senha")

        error_msg = str(e).lower()

        # Tratamentos amigáveis
        if "session" in error_msg:
            return False, "Sessão inválida. Solicite novo link."
        elif "password" in error_msg:
            return False, "Senha não atende aos requisitos."
        else:
            return False, f"Erro ao redefinir senha: {e}"


# ==========================================================
# EXPORTS
# ==========================================================
__all__ = [
    "solicitar_reset_senha",
    "redefinir_senha",
]

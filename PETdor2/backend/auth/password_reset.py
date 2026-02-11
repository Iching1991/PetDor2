"""
Reset de senha - PETDor2
Compatível com Supabase Auth
SEM import circular
"""

from typing import Tuple
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# 🔐 Solicitar reset
# ==========================================================
def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Envia e-mail de redefinição via Supabase Auth
    """

    from backend.database.supabase_client import supabase

    try:
        email = email.lower().strip()

        if not email:
            return False, "Informe um e-mail válido."

        logger.info(f"🔄 Reset solicitado: {email}")

        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": (
                    st.secrets["app"]["STREAMLIT_APP_URL"]
                    + "/redefinir_senha"
                )
            }
        )

        return True, (
            "Se o e-mail estiver cadastrado, "
            "você receberá instruções."
        )

    except Exception as e:
        logger.exception("Erro ao solicitar reset")
        return False, f"Erro: {e}"


# ==========================================================
# 🔑 Redefinir senha (token ativo)
# ==========================================================
def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine senha do usuário autenticado pelo token
    """

    from backend.database.supabase_client import supabase

    try:
        if len(nova_senha) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres."

        supabase.auth.update_user({
            "password": nova_senha
        })

        logger.info("✅ Senha redefinida")

        return True, "Senha redefinida com sucesso."

    except Exception as e:
        logger.exception("Erro redefinir senha")
        return False, f"Erro: {e}"

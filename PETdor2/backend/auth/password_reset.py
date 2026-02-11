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

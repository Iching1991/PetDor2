# PetDor2/backend/auth/security.py
"""
Controle de sessão e segurança do PETDor2
Compatível com Streamlit + Supabase REST
"""

import streamlit as st
from typing import Dict, Any


# ==========================================================
# Sessão
# ==========================================================

def usuario_logado(session_state: Dict[str, Any]) -> bool:
    """
    Verifica se o usuário está logado.
    """
    return bool(session_state.get("logged_in") and session_state.get("user_data"))


def logout(session_state: Dict[str, Any]) -> None:
    """
    Encerra a sessão do usuário.
    """
    keys = [
        "logged_in",
        "user_id",
        "user_data",
        "user_email",
        "user_name",
        "is_admin",
    ]
    for key in keys:
        session_state.pop(key, None)


# ==========================================================
# Helpers
# ==========================================================

def exigir_login():
    """
    Bloqueia acesso se o usuário não estiver logado.
    """
    if not usuario_logado(st.session_state):
        st.warning("⚠️ Você precisa estar logado.")
        st.stop()

# PetDor2/backend/auth/security.py
"""
Controle de sessão e segurança do PETDor2
Compatível com Streamlit + Supabase REST
"""

import streamlit as st
import secrets
import hashlib
from typing import Dict, Any


# ==========================================================
# Sessão
# ==========================================================

def usuario_logado(session_state: Dict[str, Any]) -> bool:
    return bool(session_state.get("user_data"))


def logout(session_state: Dict[str, Any]) -> None:
    keys = [
        "user_data",
        "pagina",
    ]
    for key in keys:
        session_state.pop(key, None)


def exigir_login():
    if not usuario_logado(st.session_state):
        st.warning("⚠️ Você precisa estar logado.")
        st.stop()


# ==========================================================
# Segurança
# ==========================================================

def gerar_token_reset_senha() -> str:
    """
    Gera token seguro para redefinição de senha.
    """
    return secrets.token_urlsafe(32)


def gerar_hash_senha(senha: str) -> str:
    """
    Gera hash SHA-256 da senha.
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

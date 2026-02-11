"""
Página de Login - PETDor2
Com recuperação de senha integrada
"""

import streamlit as st
import logging

from backend.auth.user import fazer_login
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)


# ==========================================================
# Render
# ==========================================================

def render():

    st.title("🔐 Login")

    # ------------------------------------------------------
    # Já logado
    # ------------------------------------------------------
    if st.session_state.get("user_data"):
        st.success("✅ Você já está logado.")

        if st.button("🏠 Ir para Página Inicial"):
            st.session_state.pagina = "home"
            st.rerun()

        return

    # ------------------------------------------------------
    # Formulário
    # ------------------------------------------------------
    with st.form("form_login"):

        email = st.text_input("📧 E-mail").strip().lower()
        senha = st.text_input("🔑 Senha", type="password")

        entrar = st.form_submit_button("Entrar")

    # ------------------------------------------------------
    # Login
    # ------------------------------------------------------
    if entrar:

        if not email or not senha:
            st.error("❌ Preencha e-mail e senha.")
            return

        if not validar_email(email):
            st.error("❌ E-mail inválido.")
            return

        sucesso, msg, usuario = fazer_login(email, senha)

        if not sucesso:
            st.error(msg)
            return

        # Sessão
        st.session_state["user_data"] = usuario
        st.session_state["pagina"] = "home"

        st.success("✅ Login realizado com sucesso!")
        st.rerun()

    # ------------------------------------------------------
    # Recuperação de senha
    # ------------------------------------------------------
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔑 Esqueci minha senha"):
            st.session_state.pagina = "recuperar_senha"
            st.rerun()

    with col2:
        if st.button("📝 Criar conta"):
            st.session_state.pagina = "cadastro"
            st.rerun()


__all__ = ["render"]

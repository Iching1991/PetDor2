# PETdor2/backend/pages/login.py

import streamlit as st
import logging
from auth.login_handler import autenticar_usuario
from utils.session import iniciar_sessao

logger = logging.getLogger(__name__)

def get_query_params():
    """Compatível com qualquer versão do Streamlit."""
    try:
        return st.query_params  # Streamlit 1.30+
    except Exception:
        return st.experimental_get_query_params()  # versões antigas


def render():
    """Página de Login"""
    st.title("🔐 Login")

    # Lê query params
    query_params = get_query_params()

    st.subheader("Acesse sua conta")

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if not email or not senha:
            st.warning("⚠️ Preencha todos os campos.")
            return

        sucesso, dados = autenticar_usuario(email, senha)

        if not sucesso:
            st.error("❌ E-mail ou senha incorretos.")
            return

        iniciar_sessao(dados)

        st.success("✅ Login realizado com sucesso!")
        st.rerun()

    st.markdown("---")

    st.info("Ainda não tem conta?")
    if st.button("Criar conta"):
        st.session_state.pagina = "registrar"
        st.rerun()

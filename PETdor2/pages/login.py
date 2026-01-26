"""
Página de login do PETDor2.
Autenticação de usuários e inicialização da sessão.
"""

import streamlit as st
import logging

from backend.auth import verificar_credenciais
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)


def render():
    st.header("🔐 Login")
    st.write("Acesse sua conta para continuar no **PETDor**.")

    # ------------------------------------------------------
    # Já logado
    # ------------------------------------------------------
    if st.session_state.get("user_data"):
        st.info("✅ Você já está logado.")
        if st.button("Ir para Página Inicial"):
            st.session_state.pagina = "home"
            st.rerun()
        return

    # ------------------------------------------------------
    # Formulário
    # ------------------------------------------------------
    with st.form("login_form"):
        email = st.text_input("📧 E-mail").strip().lower()
        senha = st.text_input("🔑 Senha", type="password")
        submitted = st.form_submit_button("Entrar")

    if not submitted:
        return

    # ------------------------------------------------------
    # Validações
    # ------------------------------------------------------
    if not email or not senha:
        st.error("❌ Preencha e-mail e senha.")
        return

    if not validar_email(email):
        st.error("❌ E-mail inválido.")
        return

    # ------------------------------------------------------
    # Autenticação (backend faz o hash)
    # ------------------------------------------------------
    sucesso, resultado = verificar_credenciais(email, senha)

    if not sucesso:
        st.error(resultado)
        logger.warning(f"Falha no login para {email}: {resultado}")
        return

    usuario = resultado

    if not usuario.get("email_confirmado"):
        st.warning("⚠️ Seu e-mail ainda não foi confirmado.")
        st.info("Verifique sua caixa de entrada ou spam.")
        return

    # ------------------------------------------------------
    # Sessão
    # ------------------------------------------------------
    st.session_state["user_data"] = usuario
    st.session_state["pagina"] = "home"

    logger.info(f"Usuário {email} logado com sucesso.")
    st.success("✅ Login realizado com sucesso!")
    st.rerun()


__all__ = ["render"]

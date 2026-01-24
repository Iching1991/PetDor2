# PetDor2/pages/login.py
"""
Página de login do PETDor2.
Autenticação de usuários e inicialização da sessão.
"""

import streamlit as st
import logging
import hashlib

from backend.auth.user import autenticar_usuario
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)


def hash_senha(senha: str) -> str:
    """Gera hash da senha (mesmo padrão do cadastro)."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def render():
    st.header("🔐 Login")
    st.write("Acesse sua conta para continuar.")

    # ------------------------------------------------------
    # Se já estiver logado
    # ------------------------------------------------------
    if st.session_state.get("user_data"):
        st.info("Você já está logado.")
        return

    with st.form("login_form"):
        email = st.text_input("E-mail").strip().lower()
        senha = st.text_input("Senha", type="password")
        submitted = st.form_submit_button("Entrar")

        if not submitted:
            return

        # --------------------------------------------------
        # Validações
        # --------------------------------------------------
        if not email or not senha:
            st.error("❌ Preencha e-mail e senha.")
            return

        if not validar_email(email):
            st.error("❌ E-mail inválido.")
            return

        # --------------------------------------------------
        # Autenticação
        # --------------------------------------------------
        senha_hash = hash_senha(senha)
        sucesso, resultado = autenticar_usuario(email, senha_hash)

        if not sucesso:
            st.error(resultado)
            logger.warning(f"Falha no login para {email}: {resultado}")
            return

        user_data = resultado

        if not user_data.get("email_confirmado"):
            st.warning("⚠️ Seu e-mail ainda não foi confirmado.")
            return

        # --------------------------------------------------
        # Inicializa sessão
        # --------------------------------------------------
        st.session_state["user_data"] = user_data

        st.success("✅ Login realizado com sucesso!")
        logger.info(f"Usuário {email} logado com sucesso.")

        st.session_state.pagina = "home"
        st.rerun()

    st.markdown("---")
    st.markdown("Esqueceu sua senha? Recuperação estará disponível em breve.")


__all__ = ["render"]

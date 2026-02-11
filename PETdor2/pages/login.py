"""
🔐 Página de Login — PETDor2
Autenticação via Supabase Auth + Perfil na tabela usuarios
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
        st.success("Você já está logado.")
        st.page_link("pages/home.py", label="Ir para Home")
        return

    # ------------------------------------------------------
    # Formulário
    # ------------------------------------------------------
    with st.form("form_login", clear_on_submit=False):

        email = st.text_input(
            "E-mail",
            placeholder="seu@email.com",
        ).strip().lower()

        senha = st.text_input(
            "Senha",
            type="password",
            placeholder="Digite sua senha",
        )

        entrar = st.form_submit_button(
            "Entrar",
            use_container_width=True
        )

    if not entrar:
        return

    # ------------------------------------------------------
    # Validações
    # ------------------------------------------------------
    if not validar_email(email):
        st.error("❌ E-mail inválido.")
        return

    if not senha:
        st.error("❌ Digite sua senha.")
        return

    # ------------------------------------------------------
    # Login
    # ------------------------------------------------------
    with st.spinner("Autenticando..."):

        sucesso, msg, usuario = fazer_login(email, senha)

    if not sucesso:

        if "confirmar" in msg.lower():
            st.warning(msg)
            st.page_link(
                "pages/confirmar_email.py",
                label="📧 Confirmar e-mail",
            )
        else:
            st.error(msg)

        return

    # ------------------------------------------------------
    # Sessão
    # ------------------------------------------------------
    st.session_state["user_data"] = usuario
    st.session_state["usuario_id"] = usuario["id"]
    st.session_state["is_admin"] = usuario.get("is_admin", False)

    logger.info(f"✅ Login efetuado: {email}")

    st.success("Login realizado com sucesso!")

    st.rerun()


# ==========================================================
# Execução obrigatória
# ==========================================================
try:
    render()
except Exception as e:
    st.error("Erro ao carregar página de login.")
    st.exception(e)

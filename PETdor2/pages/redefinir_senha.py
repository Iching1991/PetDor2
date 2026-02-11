"""
🔐 Página — Redefinir Senha
Fluxo via Supabase Auth (sessão do link de e-mail)
"""

import streamlit as st
import logging

from backend.auth.password_reset import redefinir_senha

logger = logging.getLogger(__name__)


# ==========================================================
# Render
# ==========================================================
def render():

    st.title("🔐 Redefinir Senha")

    st.info(
        "Digite sua nova senha para concluir a recuperação."
    )

    # ------------------------------------------------------
    # Formulário
    # ------------------------------------------------------
    with st.form("form_reset"):

        nova = st.text_input(
            "Nova senha",
            type="password",
        )

        confirmar = st.text_input(
            "Confirmar senha",
            type="password",
        )

        alterar = st.form_submit_button(
            "Alterar senha",
            use_container_width=True
        )

    if not alterar:
        return

    # ------------------------------------------------------
    # Validações
    # ------------------------------------------------------
    if not nova or not confirmar:
        st.warning("Preencha todos os campos.")
        return

    if len(nova) < 6:
        st.error("A senha deve ter pelo menos 6 caracteres.")
        return

    if nova != confirmar:
        st.error("As senhas não coincidem.")
        return

    # ------------------------------------------------------
    # Reset
    # ------------------------------------------------------
    with st.spinner("Redefinindo senha..."):

        sucesso, msg = redefinir_senha(nova)

    if sucesso:

        st.success("✅ Senha redefinida com sucesso!")

        if st.button("Ir para login"):
            st.switch_page("pages/login.py")

    else:
        st.error(msg)


# ==========================================================
# Execução
# ==========================================================
try:
    render()
except Exception as e:
    st.error("Erro ao carregar página.")
    st.exception(e)

"""
Página de confirmação de e-mail — PETDor2
Fluxo compatível com Supabase Auth automático
"""

import streamlit as st
from backend.auth.user import obter_usuario_atual


# ==========================================================
# 🖥️ Página
# ==========================================================

def render():

    st.title("📧 Confirmação de E-mail")

    usuario = obter_usuario_atual()

    # ------------------------------------------------------
    # Link inválido ou sessão não criada
    # ------------------------------------------------------
    if not usuario:
        st.error("❌ Link inválido ou expirado.")
        st.info("Solicite um novo link de confirmação.")

        if st.button("🔐 Ir para Login"):
            st.session_state.pagina = "login"
            st.rerun()

        return

    # ------------------------------------------------------
    # Confirmação bem sucedida
    # ------------------------------------------------------
    st.success("🎉 E-mail confirmado com sucesso!")
    st.info("Sua conta já está ativa.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🏠 Ir para Home", use_container_width=True):
            st.session_state.pagina = "home"
            st.rerun()

    with col2:
        if st.button("🔐 Ir para Login", use_container_width=True):
            st.session_state.pagina = "login"
            st.rerun()


# ==========================================================
# 🚀 Execução segura
# ==========================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro ao carregar página.")
    st.exception(e)


__all__ = ["render"]
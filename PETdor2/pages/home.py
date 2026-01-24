# PetDor2/pages/home.py
"""
Página inicial (dashboard) do PETDor2.
Exibe informações básicas do usuário e atalhos principais.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def render():
    """
    Renderiza a página inicial após o login.
    """
    st.title("🏠 Página Inicial")

    # ------------------------------------------------------
    # Verificação de login
    # ------------------------------------------------------
    user_data = st.session_state.get("user_data")

    if not user_data:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        st.stop()

    # ------------------------------------------------------
    # Boas-vindas
    # ------------------------------------------------------
    st.success(f"Bem-vindo(a), {user_data.get('nome', 'usuário')}!")
    st.write(
        "Aqui ficará o dashboard do PETDor, com estatísticas, atalhos "
        "e informações relevantes."
    )

    st.divider()

    # ------------------------------------------------------
    # Informações do usuário
    # ------------------------------------------------------
    st.subheader("👤 Suas informações")
    st.write(f"**E-mail:** {user_data.get('email', 'Não informado')}")
    st.write(f"**Tipo de usuário:** {user_data.get('tipo_usuario', 'Não informado')}")
    st.write(f"**País:** {user_data.get('pais', 'Não informado')}")
    st.write(
        f"**E-mail confirmado:** {'✅' if user_data.get('email_confirmado') else '❌'}"
    )

    st.divider()

    # ------------------------------------------------------
    # Ações rápidas
    # ------------------------------------------------------
    st.subheader("⚡ Ações rápidas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 Nova Avaliação"):
            st.session_state.pagina = "avaliacao"
            st.rerun()

    with col2:
        if st.button("📊 Histórico"):
            st.session_state.pagina = "historico"
            st.rerun()

    with col3:
        if st.button("👤 Minha Conta"):
            st.session_state.pagina = "conta"
            st.rerun()

    st.divider()

    # ------------------------------------------------------
    # Logout
    # ------------------------------------------------------
    if st.button("🚪 Sair da Conta", key="btn_logout_home"):
        st.session_state.clear()
        st.success("✅ Você saiu da conta com sucesso.")
        st.rerun()


__all__ = ["render"]

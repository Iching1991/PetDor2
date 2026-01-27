"""
Página inicial (dashboard) do PETDor2.
Exibe informações básicas do usuário e atalhos principais.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# 🖥️ Render
# ==========================================================

def render():
    st.title("🏠 Página Inicial")

    # ------------------------------------------------------
    # 🔐 Verificação de login
    # ------------------------------------------------------
    user_data = st.session_state.get("user_data")

    if not user_data:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        st.session_state.pagina = "login"
        st.stop()

    nome = user_data.get("nome", "Usuário")

    # ------------------------------------------------------
    # 👋 Boas-vindas
    # ------------------------------------------------------
    st.success(f"Bem-vindo(a), **{nome}**!")
    st.write(
        """
        Este é o painel principal do **PETDor**.

        Aqui você pode:
        - Avaliar a dor dos seus pets
        - Consultar avaliações anteriores
        - Gerenciar sua conta
        """
    )

    st.divider()

    # ------------------------------------------------------
    # 👤 Informações do usuário
    # ------------------------------------------------------
    st.subheader("👤 Suas informações")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"📧 **E-mail:** {user_data.get('email', '—')}")
        st.write(f"🌍 **País:** {user_data.get('pais', '—')}")

    with col2:
        st.write(
            f"👥 **Tipo de usuário:** "
            f"{user_data.get('tipo_usuario', '-').title()}"
        )
        st.write(
            f"📨 **E-mail confirmado:** "
            f"{'✅ Sim' if user_data.get('email_confirmado') else '❌ Não'}"
        )

    st.divider()

    # ------------------------------------------------------
    # ⚡ Ações rápidas
    # ------------------------------------------------------
    st.subheader("⚡ Ações rápidas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📋 Nova Avaliação", use_container_width=True):
            st.session_state.pagina = "avaliacao"
            st.rerun()

    with col2:
        if st.button("📊 Histórico", use_container_width=True):
            st.session_state.pagina = "historico"
            st.rerun()

    with col3:
        if st.button("👤 Minha Conta", use_container_width=True):
            st.session_state.pagina = "conta"
            st.rerun()

    st.divider()

    # ------------------------------------------------------
    # 🚪 Logout
    # ------------------------------------------------------
    if st.button("🚪 Sair da Conta", key="logout_home"):
        st.session_state.clear()
        st.success("✅ Você saiu da conta com sucesso.")
        st.rerun()


# ==========================================================
# 🚀 Execução protegida (evita tela branca)
# ==========================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro inesperado ao carregar a página inicial.")
    st.exception(e)


__all__ = ["render"]

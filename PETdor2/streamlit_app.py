import streamlit as st
import time
import logging

# ============================================
#  CONFIGURAÇÃO INICIAL
# ============================================
st.set_page_config(
    page_title="PETDor - Avaliação de Dor Animal",
    layout="wide",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# IMPORTS DO PROJETO
# ============================================
try:
    # Banco de dados
    from database.migration import criar_tabelas
    
    # Autenticação
    from auth.user import (
        cadastrar_usuario,
        autenticar_usuario,
        buscar_usuario_por_id
    )

    # Utils
    from utils.email_sender import enviar_email_confirmacao
    from utils.pdf_generator import gerar_pdf_relatorio

    # Páginas internas
    import pages.login as login_page
    import pages.cadastro as cadastro_page
    import pages.cadastro_pet as cadastro_pet_page
    import pages.avaliacao as avaliacao_page
    import pages.historico as historico_page
    import pages.conta as conta_page
    import pages.confirmar_email as confirmar_email_page
    import pages.recuperar_senha as recuperar_senha_page
    import pages.reset_senha as reset_senha_page

except Exception as e:
    st.error(f"Erro ao importar módulos internos do projeto. Verifique a estrutura das pastas.\n\n{e}")
    raise e


# ============================================
# INICIALIZAR BANCO DE DADOS
# ============================================
criar_tabelas()


# ============================================
# SISTEMA DE SESSÃO
# ============================================
if "usuario" not in st.session_state:
    st.session_state.usuario = None      # dados do usuário logado
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"    # página inicial padrão


# ============================================
# MENUS E PROTEÇÃO DE ROTAS
# ============================================
def require_login():
    if st.session_state.usuario is None:
        st.session_state.pagina = "login"
        st.warning("Faça login para acessar esta página.")
        st.stop()


# ============================================
# MENU LATERAL
# ============================================
def menu_lateral():
    if st.session_state.usuario:
        with st.sidebar:
            st.markdown(f"### 👤 {st.session_state.usuario['nome']}")
            st.markdown("---")

            if st.button("🏠 Início"):
                st.session_state.pagina = "inicio"

            if st.button("🐾 Cadastrar Pet"):
                st.session_state.pagina = "cadastro_pet"

            if st.button("📊 Avaliação"):
                st.session_state.pagina = "avaliacao"

            if st.button("📝 Histórico"):
                st.session_state.pagina = "historico"

            if st.button("⚙ Minha Conta"):
                st.session_state.pagina = "conta"

            st.markdown("---")
            if st.button("🚪 Sair"):
                st.session_state.usuario = None
                st.session_state.pagina = "login"
                st.experimental_rerun()


# ============================================
# ROTEAMENTO DE PÁGINAS
# ============================================
def carregar_pagina():
    page = st.session_state.pagina

    if page == "login":
        login_page.render()
        return

    if page == "cadastro":
        cadastro_page.render()
        return

    if page == "confirmar_email":
        confirmar_email_page.render()
        return

    if page == "recuperar_senha":
        recuperar_senha_page.render()
        return

    if page == "reset_senha":
        reset_senha_page.render()
        return

    # ==== ROTAS QUE EXIGEM LOGIN ====
    require_login()

    if page == "inicio":
        st.title("Bem-vindo ao PETDor 🐾")
        st.write("Selecione uma opção no menu ao lado.")
        return

    if page == "cadastro_pet":
        cadastro_pet_page.render()
        return

    if page == "avaliacao":
        avaliacao_page.render()
        return

    if page == "historico":
        historico_page.render()
        return

    if page == "conta":
        conta_page.render()
        return

    st.error(f"Página não encontrada: {page}")


# ============================================
# INTERFACE PRINCIPAL
# ============================================
def main():
    st.markdown("<h1 style='text-align:center;'>🐾 PETDor - Sistema de Avaliação de Dor Animal</h1>", unsafe_allow_html=True)
    st.write("")

    if st.session_state.usuario:
        menu_lateral()

    carregar_pagina()


# ============================================
# RODAR A INTERFACE
# ============================================
if __name__ == "__main__":
    main()

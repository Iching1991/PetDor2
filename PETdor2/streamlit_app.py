# ==========================================================
# 🚀 APP PRINCIPAL — PETDor2
# Arquitetura SaaS Veterinária
# ==========================================================

import streamlit as st

# ==========================================================
# ⚙️ CONFIG GLOBAL (SEMPRE PRIMEIRO)
# ==========================================================

st.set_page_config(
    page_title="PETdor",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# 🎨 CSS GLOBAL
# ==========================================================

from frontend.components.css import load_css
load_css()

# ==========================================================
# 🧭 SIDEBAR
# ==========================================================

from frontend.components.sidebar import render_sidebar
render_sidebar()

# ==========================================================
# 🔌 BACKEND STATUS
# ==========================================================

from backend.database import testar_conexao

with st.sidebar:
    st.divider()

    if testar_conexao():
        st.success("🟢 Backend online")
    else:
        st.error("🔴 Backend offline")

# ==========================================================
# 🧠 SESSION CONTROL
# ==========================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

pagina = st.session_state.pagina

# ==========================================================
# 📦 IMPORT PÁGINAS
# Lazy import evita circular import
# ==========================================================

def load_page(page_name):

    if page_name == "login":
        from pages import login
        login.render()

    elif page_name == "cadastro":
        from pages import cadastro
        cadastro.render()

    elif page_name == "home":
        from pages import home
        home.render()

    elif page_name == "avaliacao":
        from pages import avaliacao
        avaliacao.render()

    elif page_name == "historico":
        from pages import historico
        historico.render()

    elif page_name == "conta":
        from pages import conta
        conta.render()

    elif page_name == "confirmar_email":
        from pages import confirmar_email
        confirmar_email.render()

    elif page_name == "redefinir_senha":
        from pages import redefinir_senha
        redefinir_senha.render()

    elif page_name == "recuperar_senha":
        from pages import recuperar_senha
        recuperar_senha.render()

    else:
        st.error(f"❌ Página '{page_name}' não encontrada.")


# ==========================================================
# 🔐 AUTH GUARD (Proteção básica)
# ==========================================================

PAGINAS_PUBLICAS = [
    "login",
    "cadastro",
    "confirmar_email",
    "redefinir_senha",
    "recuperar_senha",
]

usuario_logado = st.session_state.get("user_data")

if not usuario_logado and pagina not in PAGINAS_PUBLICAS:
    st.warning("🔐 Faça login para acessar o sistema.")
    st.session_state.pagina = "login"
    st.rerun()

# ==========================================================
# 🖥️ RENDERIZAÇÃO DA PÁGINA
# ==========================================================

try:
    load_page(pagina)

except Exception as e:
    st.error("❌ Erro ao carregar página.")
    st.exception(e)

# ==========================================================
# 📌 FOOTER
# ==========================================================

st.divider()

st.caption(
    "© 2026 PETdor • Sistema Inteligente de Avaliação de Dor Animal 🐾"
)

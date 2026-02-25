# ==========================================================
# 🚀 APP PRINCIPAL PETDor2 — UI REFATORADA
# ==========================================================

import streamlit as st

# ==========================================================
# ⚠️ CONFIGURAÇÃO GLOBAL (SEMPRE PRIMEIRO)
# ==========================================================

st.set_page_config(
    page_title="PETDor",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================
# IMPORTS CORE
# ==========================================================

from backend.database import testar_conexao
from frontend.components.sidebar import render_sidebar

# Páginas
from pages import (
    login,
    cadastro,
    home,
    avaliacao,
    historico,
    conta,
    confirmar_email,
    redefinir_senha,
    recuperar_senha,
)

# ==========================================================
# 🎨 ESTILO GLOBAL (opcional mas melhora UI)
# ==========================================================

st.markdown(
    """
    <style>

    /* Remove padding topo */
    .block-container {
        padding-top: 1.5rem;
    }

    /* Sidebar largura */
    section[data-testid="stSidebar"] {
        width: 260px;
    }

    /* Botões largura total */
    .stButton button {
        width: 100%;
        border-radius: 10px;
        height: 45px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# 🔌 TESTE BACKEND (modo silencioso)
# ==========================================================

with st.spinner("Conectando backend..."):

    if testar_conexao():
        backend_ok = True
    else:
        backend_ok = False

# Banner discreto no topo
if backend_ok:
    st.toast("Backend conectado ✅")
else:
    st.error("❌ Falha na conexão com backend")

# ==========================================================
# 🧭 SIDEBAR GLOBAL
# ==========================================================

render_sidebar()

# ==========================================================
# 🧠 SESSION STATE DEFAULTS
# ==========================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

pagina = st.session_state.pagina

# ==========================================================
# 🧱 CONTAINER PRINCIPAL
# ==========================================================

main_container = st.container()

# ==========================================================
# 🚦 ROUTER DE PÁGINAS
# ==========================================================

try:

    with main_container:

        # -------------------------
        # AUTH
        # -------------------------
        if pagina == "login":
            login.render()

        elif pagina == "cadastro":
            cadastro.render()

        elif pagina == "confirmar_email":
            confirmar_email.render()

        elif pagina == "redefinir_senha":
            redefinir_senha.render()

        elif pagina == "recuperar_senha":
            recuperar_senha.render()

        # -------------------------
        # APP
        # -------------------------
        elif pagina == "home":
            home.render()

        elif pagina == "avaliacao":
            avaliacao.render()

        elif pagina == "historico":
            historico.render()

        elif pagina == "conta":
            conta.render()

        # -------------------------
        # FALLBACK
        # -------------------------
        else:
            st.error(f"Página '{pagina}' não encontrada.")

# ==========================================================
# 🚨 ERRO GLOBAL
# ==========================================================

except Exception as e:

    st.error("❌ Erro ao carregar a aplicação.")
    st.exception(e)

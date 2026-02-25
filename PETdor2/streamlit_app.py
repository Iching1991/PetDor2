# ==========================================================
# 🚀 APP PRINCIPAL — PETDor2
# Arquitetura SaaS Veterinária
# ==========================================================

import streamlit as st
import sys
import os

# 🔧 Garantir que o root do projeto esteja no path (evita erro frontend import)
sys.path.append(os.path.dirname(__file__))

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

try:
    from frontend.components.css import load_css
    load_css()
except Exception:
    pass  # Se CSS falhar, app continua

# ==========================================================
# 🧭 SIDEBAR
# ==========================================================

try:
    from frontend.components.sidebar import render_sidebar
    render_sidebar()
except Exception:
    pass

# ==========================================================
# 🔌 BACKEND STATUS
# ==========================================================

try:
    from backend.database import testar_conexao

    with st.sidebar:
        st.divider()

        if testar_conexao():
            st.success("🟢 Backend online")
        else:
            st.error("🔴 Backend offline")

except Exception:
    pass

# ==========================================================
# 🧠 SESSION CONTROL
# ==========================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

pagina = st.session_state.pagina

# ==========================================================
# 🔐 AUTH GUARD
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
    st.session_state.pagina = "login"
    st.rerun()

# ==========================================================
# 📦 ROUTER DE PÁGINAS (Lazy Import)
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
# 🖥️ RENDERIZAÇÃO
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
st.caption("© 2026 PETdor • Sistema Inteligente de Avaliação de Dor Animal 🐾")

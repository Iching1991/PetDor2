# streamlit_app.py

# streamlit_app.py

import streamlit as st
from backend.database import testar_conexao

# ==========================================================
# Configuração da página
# ==========================================================
st.set_page_config(
    page_title="PETdor",
    page_icon="🐾",
    layout="wide"
)

# ==========================================================
# Teste backend (opcional)
# ==========================================================
try:
    if testar_conexao():
        st.sidebar.success("🟢 Backend conectado")
    else:
        st.sidebar.error("🔴 Falha na conexão")
except Exception:
    st.sidebar.warning("⚠️ Não foi possível testar conexão")

# ==========================================================
# Controle de navegação
# ==========================================================
if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

pagina = st.session_state.pagina

# ==========================================================
# Router de páginas
# ==========================================================
if pagina == "login":
    from pages.login import render
    render()

elif pagina == "cadastro":
    from pages.cadastro import render
    render()

elif pagina == "recuperar_senha":
    from pages.recuperar_senha import render
    render()

elif pagina == "redefinir_senha":
    from pages.redefinir_senha import render
    render()

elif pagina == "home":
    from pages.home import render
    render()

elif pagina == "avaliacao":
    from pages.avaliacao import render
    render()

elif pagina == "historico":
    from pages.historico import render
    render()

elif pagina == "conta":
    from pages.conta import render
    render()

elif pagina == "admin":
    from pages.admin import render
    render()

else:
    st.error("Página não encontrada.")

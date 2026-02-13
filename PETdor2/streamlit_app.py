# ==========================================================
# 🚀 APP PRINCIPAL PETDor2
# ==========================================================

import streamlit as st

# ⚠️ TEM QUE SER A PRIMEIRA COISA STREAMLIT
st.set_page_config(
    page_title="PETdor",
    page_icon="🐾",
    layout="wide"
)

# Só depois dos configs
from backend.database import testar_conexao

# ==========================================================
# Teste backend
# ==========================================================

if testar_conexao():
    st.success("✅ Backend conectado com sucesso!")
else:
    st.error("❌ Falha na conexão com o backend.")

st.divider()

# ==========================================================
# Router de páginas
# ==========================================================

if "pagina" not in st.session_state:
    st.session_state.pagina = "login"

pagina = st.session_state.pagina

# ==========================================================
# Imports das páginas
# ==========================================================

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
# Renderização
# ==========================================================

try:

    if pagina == "login":
        login.render()

    elif pagina == "cadastro":
        cadastro.render()

    elif pagina == "home":
        home.render()

    elif pagina == "avaliacao":
        avaliacao.render()

    elif pagina == "historico":
        historico.render()

    elif pagina == "conta":
        conta.render()

    elif pagina == "confirmar_email":
        confirmar_email.render()

    elif pagina == "redefinir_senha":
        redefinir_senha.render()

    elif pagina == "recuperar_senha":
        recuperar_senha.render()

    else:
        st.error(f"Página '{pagina}' não encontrada.")

except Exception as e:
    st.error("❌ Erro ao carregar página.")
    st.exception(e)

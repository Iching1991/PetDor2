# PETdor2/streamlit_app.py

import streamlit as st

# Importa backend
from backend.database import testar_conexao
from backend.auth.user import (
    criar_usuario,
    autenticar_usuario,
    buscar_usuario_por_email
)

# Carrega páginas
import pages.home as home
import pages.login as login
import pages.cadastro as cadastro


# ----------------------------
# Inicialização
# ----------------------------
st.set_page_config(
    page_title="PETdor",
    page_icon="🐾",
    layout="wide"
)

# Teste manual de conexão (aparece na UI)
import streamlit as st
from backend.database import testar_conexao

st.sidebar.write("🔧 Testes do sistema")
if st.sidebar.button("Testar conexão com Supabase"):
    testar_conexao()



# ----------------------------
# Router simples
# ----------------------------
pagina = st.sidebar.selectbox(
    "Navegar",
    ["Home", "Login", "Cadastro"]
)

if pagina == "Home":
    home.render()

elif pagina == "Login":
    login.render()

elif pagina == "Cadastro":
    cadastro.render()

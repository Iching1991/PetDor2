# PETdor2/streamlit_app.py

import streamlit as st

# ------------------------ Backend ------------------------
from backend.database.supabase_client import testar_conexao, supabase_table_select
from backend.especies.index import carregar_especies
from backend.pages.home import render_home
from backend.pages.avaliacao import render_avaliacao
from backend.pages.sobre import render_sobre

# ------------------------ Configuração da página ------------------------
st.set_page_config(
    page_title="PetDor",
    page_icon="🐾",
    layout="wide"
)

# ------------------------ MENU LATERAL ------------------------
menu = st.sidebar.selectbox(
    "Menu",
    ["🏡 Início", "📋 Avaliação", "🐾 Espécies", "ℹ️ Sobre"]
)

# ------------------------ STATUS DA CONEXÃO ------------------------
with st.sidebar:
    st.write("### 🔌 Status da Conexão")
    status = testar_conexao()
    if status:
        st.success("✅ Conectado ao Supabase!")
    else:
        st.error("❌ Falha ao conectar ao Supabase")

# ------------------------ ROTAS ------------------------
if menu == "🏡 Início":
    render_home()

elif menu == "📋 Avaliação":
    render_avaliacao()

elif menu == "🐾 Espécies":
    especies = carregar_especies()
    st.write("### 🐾 Lista de Espécies Cadastradas")
    if especies:
        st.table(especies)
    else:
        st.info("Nenhuma espécie cadastrada.")

elif menu == "ℹ️ Sobre":
    render_sobre()

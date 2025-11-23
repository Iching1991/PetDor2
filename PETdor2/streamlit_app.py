# PETdor2/streamlit_app.py
import sys
import os
import streamlit as st

# --- Corrige importações para Streamlit Cloud ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim correção ---

# ===========================
# Imports locais das páginas
# ===========================
from pages.cadastro_pet import render as cadastro_pet_app
from pages.avaliacao import render as avaliacao_app
from pages.home import render as home_app
from pages.perfil import render as perfil_app

# ===========================
# Menu lateral
# ===========================
st.sidebar.title("PETdor2")
pagina = st.sidebar.selectbox(
    "Navegar",
    ["Home", "Cadastro de Pet", "Avaliação de Dor", "Perfil"]
)

# ===========================
# Renderiza páginas
# ===========================
if pagina == "Home":
    home_app()
elif pagina == "Cadastro de Pet":
    cadastro_pet_app()
elif pagina == "Avaliação de Dor":
    avaliacao_app()
elif pagina == "Perfil":
    perfil_app()


# PETdor2/streamlit_app.py
import streamlit as st
import sys
import os

# --- Corrige importações para Streamlit Cloud ---
current_script_dir = os.path.dirname(os.path.abspath(__file__))
if current_script_dir not in sys.path:
    sys.path.insert(0, current_script_dir)
# --- Fim correção ---

# ------------------------------
# Importações de banco e auth
# ------------------------------
from database.migration import migrar_banco_completo
from auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
    confirmar_email,
)
from auth.password_reset import (
    solicitar_reset_senha,
    validar_token_reset,
    redefinir_senha_com_token,
)

# ------------------------------
# Importações das páginas
# ------------------------------
from pages.cadastro_pet import app as cadastro_pet_app
from pages.avaliacao import app as avaliacao_app

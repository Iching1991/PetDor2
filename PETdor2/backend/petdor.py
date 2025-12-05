# ============================================================
# PETDOR – Backend Principal
# ============================================================

import os
import sys
import logging
import streamlit as st

# ============================================================
# 🔧 LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================
# 🔧 AJUSTE DO PATH PARA IMPORTS ABSOLUTOS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ============================================================
# 🔧 IMPORTS INTERNOS
# ============================================================
from database.supabase_client import get_supabase, testar_conexao
from auth.user import (
    cadastrar_usuario, verificar_credenciais,
    buscar_usuario_por_id
)
from auth.password_reset import (
    solicitar_reset_senha, validar_token_reset, redefinir_senha_com_token
)
from auth.email_confirmation import confirmar_email_com_token
from auth.security import usuario_logado, logout

from pages.cadastro_pet import app as cadastro_pet_page
from pages.avaliacao import app as avaliacao_page
from pages.admin import app as admin_page

# ============================================================
# 🔧 INICIALIZAÇÃO DO SUPABASE
# ============================================================
try:
    get_supabase()
    if not testar_conexao():
        st.error("❌ Falha ao conectar ao Supabase. Verifique variáveis de ambiente.")
        st.stop()
except Exception as e:
    st.error(f"❌ Erro ao iniciar o Supabase: {e}")
    st.stop()

logger.info("✅ Supabase inicializado com sucesso.")

# ============================================================
# 🎨 Streamlit – Configuração inicial
# ============================================================
st.set_page_config(page_title="PETDOR", layout="wide")
st.title("🐾 PETDOR – Avaliação de Dor Animal")

# ============================================================
# 🔐 Inicialização do session_state
# ============================================================
defaults = {
    "user_id": None,
    "user_data": None,
    "user_email": None,
    "user_name": None,
    "is_admin": False,
    "page": "login",
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)

# ============================================================
# 🔗 PARÂMETROS DE URL
# ============================================================
params = st.query_params

# --- Confirmação de e-mail ---
if params.get("confirm_token"):
    st.session_state.page = "confirmar_email"

# --- Reset de senha via link ---
elif params.get("reset_token"):
    st.session_state.page = "reset_url"

# ============================================================
# 🔀 ROTEAMENTO PRINCIPAL
# ============================================================
def route(page: str):

    # ========================================================
    # 📌 CONFIRMAR E-MAIL
    # ========================================================
    if page == "confirmar_email":
        token = params.get("confirm_token")
        st.subheader("Confirmação de E-mail")

        ok, msg = confirmar_email_com_token(token)
        st.success(msg) if ok else st.error(msg)

        st.info("Agora você pode fazer login.")
        st.query_params.clear()
        return

    # ========================================================
    # 📌 RESET DE SENHA PELO LINK
    # ========================================================
    if page == "reset_url":
        token = params.get("reset_token")
        st.subheader("Redefinir Senha")

        valido, email, msg = validar_token_reset(token)
        if not valido:
            st.error(msg)
            st.info("Solicite um novo link.")
            st.query_params.clear()
            return

        st.write(f"Redefinindo senha de: **{email}**")

        nova = st.text_input("Nova senha", type="password")
        nova2 = st.text_input("Confirmar nova senha", type="password")

        if st.button("Alterar senha"):
            if nova != nova2:
                st.error("As senhas não coincidem.")
            elif len(nova) < 8:
                st.error("Senha deve ter pelo menos 8 caracteres.")
            else:
                ok, msg = redefinir_senha_com_token(token, nova)
                st.success(msg) if ok else st.error(msg)
                if ok:
                    st.query_params.clear()
        return

    # ========================================================
    # 📌 USUÁRIO LOGADO – DASHBOARD
    # ========================================================
    if usuario_logado(st.session_state):

        # Carregar dados se ainda não estão no session
        if st.session_state.user_data is None:
            ok, data = buscar_usuario_por_id(st.session_state.user_id)
            if not ok:
                st.error("Erro ao carregar dados do usuário.")
                logout(st.session_state)
                st.rerun()
            st.session_state.user_data = data
            st.session_state.user_email = data['email']
            st.session_state.user_name = data['nome']
            st.session_state.is_admin = data.get('is_admin', False)

        # Sidebar
        st.sidebar.write(f"Bem-vindo(a), **{st.session_state.user_name}**!")

        options = ["Meus Pets e Avaliações"]
        if st.session_state.is_admin:
            options.append("Administração")
        options.append("Sair")

        choice = st.sidebar.selectbox("Menu", options)

        if choice == "Sair":
            logout(st.session_state)
            st.session_state.page = "login"
            st.rerun()

        if choice == "Meus Pets e Avaliações":
            st.subheader("Meus Pets e Avaliações")
            cadastro_pet_page(st.session_state.user_id)
            avaliacao_page(st.session_state.user_id)
            return

        if choice == "Administração":
            st.subheader("Painel Administrador")
            admin_page()
            return

    # ========================================================
    # 📌 LOGIN / CRIAR CONTA / RESET SENHA
    # ========================================================

    menu = st.sidebar.selectbox(
        "Menu",
        ["Login", "Criar Conta", "Redefinir Senha"]
    )
    st.session_state.page = menu.lower().replace(" ", "_")

    # ---- LOGIN ----
    if st.session_state.page == "login":
        st.subheader("Login")
        email = st.text_input("E-mail").lower()
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            ok, user = verificar_credenciais(email, senha)
            if ok:
                st.success("Login bem-sucedido!")
                st.session_state.user_id = user["id"]
                st.session_state.user_data = user
                st.session_state.user_email = user["email"]
                st.session_state.user_name = user["nome"]
                st.session_state.is_admin = user.get("is_admin", False)
                st.session_state.page = "avaliacao"
                st.rerun()
            else:
                st.error(user)
        return

    # ---- CRIAR CONTA ----
    if st.session_state.page == "criar_conta":
        st.subheader("Criar Conta")

        with st.form("cadastro"):
            nome = st.text_input("Nome Completo").title()
            email = st.text_input("E-mail").lower()
            senha = st.text_input("Senha", type="password")
            senha2 = st.text_input("Confirmar senha", type="password")
            tipo = st.selectbox("Tipo de Usuário", ["Tutor", "Veterinário", "Clínica"])
            pais = st.text_input("País", "Brasil")

            if st.form_submit_button("Cadastrar"):

                if not nome or not email or not senha:
                    st.error("Preencha todos os campos.")
                elif senha != senha2:
                    st.error("As senhas não coincidem.")
                elif len(senha) < 8:
                    st.error("Senha deve ter pelo menos 8 caracteres.")
                else:
                    ok, msg = cadastrar_usuario(nome, email, senha, tipo, pais)
                    st.success(msg) if ok else st.error(msg)
        return

    # ---- RESET SENHA ----
    if st.session_state.page == "redefinir_senha":
        st.subheader("Redefinir Senha")

        email = st.text_input("Seu e-mail").lower()
        if st.button("Enviar link de redefinição"):
            ok, msg = solicitar_reset_senha(email)
            st.info(msg) if ok else st.error(msg)

        st.markdown("---")
        st.write("Reset manual (modo desenvolvedor)")

        token = st.text_input("Token")
        nova = st.text_input("Nova senha", type="password")
        nova2 = st.text_input("Confirmar senha", type="password")

        if st.button("Alterar manualmente"):
            if nova != nova2:
                st.error("Senhas não coincidem.")
            elif len(nova) < 8:
                st.error("Senha muito curta.")
            else:
                ok, msg = redefinir_senha_com_token(token, nova)
                st.success(msg) if ok else st.error(msg)
        return


# ============================================================
# ✔️ EXECUÇÃO DO ROTEAMENTO
# ============================================================
route(st.session_state.page)

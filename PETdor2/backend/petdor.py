# PetDor2/petdor.py
import streamlit as st
import sys
import os
import logging

# ============================================================
# 🔧 Configuração de Logging
# ============================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================================
# 🔧 CORREÇÃO DOS IMPORTS (ABSOLUTOS)
# ============================================================
# Adiciona o diretório raiz do projeto ao sys.path para imports absolutos
# Isso permite importar módulos como 'auth.user' ou 'database.supabase_client'
# sem problemas de "top-level package".
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Agora todos os imports são feitos a partir da raiz do projeto (ex: auth.user)
from database.supabase_client import testar_conexao, get_supabase
from auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
    buscar_usuario_por_id, # Adicionado para buscar dados do usuário logado
)
from auth.password_reset import (
    solicitar_reset_senha,
    validar_token_reset,
    redefinir_senha_com_token,
)
from auth.email_confirmation import confirmar_email_com_token # Novo import para confirmação de e-mail
from auth.security import usuario_logado, logout # Funções de sessão
from pages.cadastro_pet import app as cadastro_pet_app
from pages.avaliacao import app as avaliacao_app
from pages.admin import app as admin_app # Importar a página de administração

# ============================================================
# 🔧 Inicializa Supabase e verifica conexão
# ============================================================
try:
    # Apenas tenta obter o cliente para inicializar e testar a conexão
    # A inicialização real ocorre dentro de get_supabase()
    get_supabase()
    if not testar_conexao():
        st.error("❌ Falha ao conectar com o Supabase. Verifique as variáveis de ambiente.")
        st.stop() # Para a execução do app se não houver conexão
    logger.info("✅ Conexão com Supabase estabelecida.")
except RuntimeError as e:
    st.error(f"❌ Erro de configuração do Supabase: {e}")
    st.stop()
except Exception as e:
    st.error(f"❌ Erro inesperado na inicialização do Supabase: {e}")
    st.stop()

# ============================================================
# 🎨 Configuração da página Streamlit
# ============================================================
st.set_page_config(page_title="PETDOR – Avaliação de Dor Animal", layout="wide")
st.title("🐾 PETDOR – Sistema de Avaliação de Dor Animal")

# ============================================================
# 🔐 GESTÃO DE SESSÃO E ROTAS
# ============================================================

# Inicializa st.session_state se necessário
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "page" not in st.session_state:
    st.session_state.page = "login" # Página inicial padrão

# -----------------------------------------
# 📧 Rota para Confirmação de E-mail
# -----------------------------------------
query_params = st.query_params
confirm_token = query_params.get("confirm_token")

if confirm_token:
    st.session_state.page = "confirmar_email"
    st.subheader("Confirmação de E-mail")
    ok, msg = confirmar_email_com_token(confirm_token)
    if ok:
        st.success(msg)
        st.info("Você pode fazer login agora.")
    else:
        st.error(msg)
    # Limpa o token da URL para evitar reprocessamento
    st.query_params.clear()
    st.stop() # Para a execução após a confirmação

# -----------------------------------------
# 🔄 Rota para Redefinição de Senha via URL
# -----------------------------------------
reset_token_url = query_params.get("reset_token") # Usar 'reset_token' para clareza

if reset_token_url and st.session_state.page != "redefinir_senha_url":
    st.session_state.page = "redefinir_senha_url"
    st.query_params.clear() # Limpa para evitar loop de reruns
    st.rerun() # Redireciona para a página de redefinição com o token

# ============================================================
# 🗺️ NAVEGAÇÃO PRINCIPAL
# ============================================================

# Se o usuário está logado, mostra o menu de opções
if usuario_logado(st.session_state):
    # Carrega os dados completos do usuário se ainda não estiverem na sessão
    if st.session_state.user_data is None:
        ok, user_data = buscar_usuario_por_id(st.session_state.user_id)
        if ok and user_data:
            st.session_state.user_data = user_data
            st.session_state.user_email = user_data.get('email')
            st.session_state.user_name = user_data.get('nome')
            st.session_state.is_admin = user_data.get('is_admin', False)
        else:
            st.error("Erro ao carregar dados do usuário. Por favor, faça login novamente.")
            logout(st.session_state)
            st.rerun()

    st.sidebar.write(f"Bem-vindo(a), **{st.session_state.user_name}**!")

    menu_options = ["Meus Pets e Avaliações"]
    if st.session_state.is_admin:
        menu_options.append("Administração")
    menu_options.append("Sair")

    selected_option = st.sidebar.selectbox("Opções", menu_options, key="main_menu_logged_in")

    if selected_option == "Meus Pets e Avaliações":
        st.session_state.page = "avaliacao"
    elif selected_option == "Administração":
        st.session_state.page = "admin"
    elif selected_option == "Sair":
        logout(st.session_state)
        st.session_state.page = "login" # Volta para a página de login
        st.rerun()

    # Renderiza a página selecionada
    if st.session_state.page == "avaliacao":
        st.subheader("Meus Pets e Avaliações")
        cadastro_pet_app(st.session_state.user_id) # Passa o user_id para a página de cadastro de pet
        avaliacao_app(st.session_state.user_id) # Passa o user_id para a página de avaliação
    elif st.session_state.page == "admin":
        st.subheader("Painel de Administração")
        admin_app() # Chama a página de administração

# Se o usuário NÃO está logado, mostra o menu de autenticação
else:
    menu = st.sidebar.selectbox("Menu", ["Login", "Criar Conta", "Redefinir Senha"], key="main_menu_not_logged_in")
    st.session_state.page = menu.lower().replace(" ", "_") # Atualiza a página com base na seleção do menu

    if st.session_state.page == "login":
        st.subheader("Login")
        email = st.text_input("E-mail", key="login_email").lower()
        senha = st.text_input("Senha", type="password", key="login_senha")
        if st.button("Entrar", key="btn_login"):
            ok, msg_ou_usuario = verificar_credenciais(email, senha)
            if ok:
                st.success("Login bem-sucedido!")
                st.session_state.user_id = msg_ou_usuario['id']
                st.session_state.user_data = msg_ou_usuario # Armazena todos os dados do usuário
                st.session_state.user_email = msg_ou_usuario['email']
                st.session_state.user_name = msg_ou_usuario['nome']
                st.session_state.is_admin = msg_ou_usuario.get('is_admin', False)
                st.session_state.page = "avaliacao" # Redireciona para a página de avaliação após login
                st.rerun()
            else:
                st.error(msg_ou_usuario)

    elif st.session_state.page == "criar_conta":
        st.subheader("Criar Nova Conta")
        with st.form("form_cadastro"):
            nome = st.text_input("Nome Completo").title()
            email = st.text_input("E-mail").lower()
            senha = st.text_input("Senha", type="password")
            senha2 = st.text_input("Confirmar Senha", type="password")
            tipo_usuario = st.selectbox("Tipo de Usuário", ["Tutor", "Veterinário", "Clínica"])
            pais = st.text_input("País", value="Brasil")
            enviar = st.form_submit_button("Cadastrar")
            if enviar:
                if not nome or not email or not senha or not senha2:
                    st.error("Por favor, preencha todos os campos.")
                elif senha != senha2:
                    st.error("As senhas não coincidem.")
                elif len(senha) < 8: # Aumentei para 8 caracteres para melhor segurança
                    st.error("A senha deve ter pelo menos 8 caracteres.")
                else:
                    ok, msg = cadastrar_usuario(nome, email, senha, tipo_usuario, pais)
                    if ok:
                        st.success(msg)
                        st.info("Verifique seu e-mail para confirmar sua conta e depois faça login.")
                    else:
                        st.error(msg)

    elif st.session_state.page == "redefinir_senha" or st.session_state.page == "redefinir_senha_url":
        st.subheader("Redefinir Senha")

        # Verifica se chegou um token na URL (para o fluxo de link de e-mail)
        token_url = query_params.get("reset_token") # Re-verifica aqui para o caso de reruns

        if st.session_state.page == "redefinir_senha_url" and token_url:
            st.info("Você está redefinindo sua senha através de um link enviado por e-mail.")
            token_valido, email_do_usuario, msg_validacao = validar_token_reset(token_url) # Ajuste na ordem dos retornos

            if token_valido and email_do_usuario:
                st.success(msg_validacao)
                st.write(f"Redefinindo senha para: **{email_do_usuario}**")
                nova = st.text_input("Nova senha", type="password", key="nova_senha_url")
                nova2 = st.text_input("Confirmar nova senha", type="password", key="nova_senha2_url")
                if st.button("Alterar senha", key="btn_alterar_senha_url"):
                    if not nova or not nova2:
                        st.error("Preencha a nova senha e a confirmação.")
                    elif nova != nova2:
                        st.error("As senhas não coincidem.")
                    elif len(nova) < 8: # Aumentei para 8 caracteres
                        st.error("A senha deve ter pelo menos 8 caracteres.")
                    else:
                        ok, msg = redefinir_senha_com_token(token_url, nova)
                        if ok:
                            st.success(msg)
                            st.info("Você pode fazer login agora.")
                            st.session_state.page = "login" # Volta para login
                            st.query_params.clear()
                            st.rerun()
                        else:
                            st.error(msg)
            else:
                st.error(msg_validacao)
                st.info("Solicite um novo link de redefinição.")
                st.query_params.clear()
                st.session_state.page = "redefinir_senha" # Volta para o fluxo normal
                st.rerun()
        else:
            # Fluxo normal de solicitação de link de reset
            email_reset = st.text_input("Seu e-mail para redefinição", key="email_reset").lower()
            if st.button("Enviar link de redefinição", key="btn_enviar_reset"):
                ok, msg = solicitar_reset_senha(email_reset)
                if ok:
                    st.info(msg)
                else:
                    st.error(msg)

            st.markdown("---")
            st.write("Ou redefina manualmente com um token (apenas para testes/desenvolvimento):")
            token_manual = st.text_input("Token", key="token_manual")
            nova_manual = st.text_input("Nova senha", type="password", key="nova_manual")
            nova2_manual = st.text_input("Confirmar nova senha", type="password", key="nova2_manual")
            if st.button("Alterar senha manualmente", key="btn_alterar_manual"):
                if not token_manual or not nova_manual or not nova2_manual:
                    st.error("Preencha todos os campos.")
                elif nova_manual != nova2_manual:
                    st.error("As senhas não coincidem.")
                elif len(nova_manual) < 8: # Aumentei para 8 caracteres
                    st.error("A senha deve ter pelo menos 8 caracteres.")
                else:
                    valido, email_usuario, msg_validacao = validar_token_reset(token_manual) # Ajuste na ordem dos retornos
                    if valido and email_usuario:
                        ok, msg = redefinir_senha_com_token(token_manual, nova_manual)
                        if ok:
                            st.success(msg)
                            st.info("Você pode fazer login agora.")
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error(msg_validacao)


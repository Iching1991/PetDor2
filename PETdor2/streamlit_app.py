# PETdor2/streamlit_app.py
import streamlit as st
import sys
import os

# --- INÍCIO DA CORREÇÃO DE IMPORTAÇÃO ---
# Adiciona o diretório atual (PETdor2) ao sys.path para resolver importações absolutas
# Isso permite que módulos como 'auth', 'utils' e 'database' sejam importados diretamente
# como 'auth.user' ou 'utils.email_sender' ou 'database.connection' de qualquer lugar dentro do projeto.
current_script_dir = os.path.dirname(os.path.abspath(__file__))
# current_script_dir agora é '/mount/src/petdor2/PETdor2'
if current_script_dir not in sys.path:
    sys.path.insert(0, current_script_dir)
# --- FIM DA CORREÇÃO DE IMPORTAÇÃO ---

# Agora as importações devem funcionar
from database.migration import migrar_banco_completo 
# Importações corrigidas para corresponder aos nomes das funções em auth/user.py
from auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
    confirmar_email, # Adicionado para lidar com a confirmação de e-mail
)
# Importações corrigidas para corresponder aos nomes das funções em auth/password_reset.py
from auth.password_reset import solicitar_reset_senha, validar_token_reset, redefinir_senha_com_token

from pages.cadastro_pet import app as cadastro_pet_app
from pages.avaliacao import app as avaliacao_app

# 🔧 Inicializa banco
migrar_banco_completo() 

# Configuração da página
st.set_page_config(page_title="PETDOR – Avaliação de Dor", layout="centered")
st.title("🐾 PETDOR – Sistema PETDOR")

# --- Lógica para lidar com parâmetros de URL (confirmação de e-mail e reset de senha) ---
query_params = st.query_params
if "token" in query_params and "action" in query_params:
    token = query_params["token"]
    action = query_params["action"]

    if action == "confirm_email":
        st.subheader("Confirmação de E-mail")
        ok, msg = confirmar_email(token)
        if ok:
            st.success(msg + " Você já pode fazer login.")
        else:
            st.error(msg)
        # Limpa os parâmetros da URL para evitar reprocessamento
        st.query_params.clear()
        st.stop() # Interrompe a execução para mostrar a mensagem e não carregar o resto do app

    elif action == "reset_password":
        st.subheader("Redefinir Senha")
        st.info("Por favor, insira sua nova senha.")

        nova_senha = st.text_input("Nova Senha", type="password", key="reset_nova_senha_url")
        confirmar_nova_senha = st.text_input("Confirmar Nova Senha", type="password", key="reset_confirmar_nova_senha_url")

        if st.button("Redefinir Senha", key="btn_redefinir_url"):
            if not nova_senha or not confirmar_nova_senha:
                st.error("Por favor, preencha ambos os campos de senha.")
            elif nova_senha != confirmar_nova_senha:
                st.error("As senhas não coincidem.")
            else:
                ok, msg = redefinir_senha_com_token(token, nova_senha)
                if ok:
                    st.success(msg + " Você já pode fazer login.")
                else:
                    st.error(msg)
                # Limpa os parâmetros da URL para evitar reprocessamento
                st.query_params.clear()
                st.stop() # Interrompe a execução para mostrar a mensagem e não carregar o resto do app
        st.stop() # Interrompe a execução para esperar a nova senha

# --- Fim da lógica de parâmetros de URL ---


# Menu lateral
menu = st.sidebar.selectbox("Menu", ["Login", "Criar Conta", "Redefinir Senha"])

# -------------------------------
# LOGIN
# -------------------------------
if menu == "Login":
    st.subheader("Login")
    email = st.text_input("E-mail", key="login_email").lower() # Email em minúsculas
    senha = st.text_input("Senha", type="password", key="login_senha")
    if st.button("Entrar", key="btn_login"):
        ok, msg_ou_usuario = verificar_credenciais(email, senha)
        if ok:
            st.success("Login bem-sucedido!")
            st.session_state.user_id = msg_ou_usuario['id'] # Pega o ID do usuário retornado
            st.session_state.user_email = msg_ou_usuario['email']
            st.session_state.user_name = msg_ou_usuario['nome']
            st.session_state.user_type = msg_ou_usuario['tipo_usuario']
            st.session_state.logged_in = True
            st.session_state.page = "Avaliação de Dor" # Redireciona para a página de avaliação
            st.rerun()
        else:
            st.error(msg_ou_usuario)

# -------------------------------
# CRIAR CONTA
# -------------------------------
elif menu == "Criar Conta":
    st.subheader("Criar Nova Conta")
    with st.form("cadastro_form"):
        nome = st.text_input("Nome Completo").title() # Nome com primeira letra maiúscula
        email = st.text_input("E-mail", key="cadastro_email").lower() # Email em minúsculas
        senha = st.text_input("Senha", type="password", key="cadastro_senha")
        confirmar_senha = st.text_input("Confirmar Senha", type="password", key="cadastro_confirmar_senha")
        tipo_usuario = st.selectbox("Tipo de Usuário", ["Tutor", "Veterinário", "Clínica"], key="cadastro_tipo_usuario")
        pais = st.text_input("País", value="Brasil", key="cadastro_pais").title()

        submitted = st.form_submit_button("Cadastrar")
        if submitted:
            if not nome or not email or not senha or not confirmar_senha:
                st.error("Por favor, preencha todos os campos.")
            elif senha != confirmar_senha:
                st.error("As senhas não coincidem.")
            else:
                ok, msg = cadastrar_usuario(nome, email, senha, tipo_usuario, pais)
                if ok:
                    st.success(msg)
                    st.info("Você pode fazer login após confirmar seu e-mail.")
                else:
                    st.error(msg)

# -------------------------------
# REDEFINIR SENHA
# -------------------------------
elif menu == "Redefinir Senha":
    st.subheader("Redefinir Senha")
    st.write("Insira seu e-mail para receber um link de redefinição de senha.")
    email_reset = st.text_input("Seu e-mail", key="reset_email").lower() # Email em minúsculas
    if st.button("Enviar link de redefinição", key="btn_enviar_token"):
        ok, msg = solicitar_reset_senha(email_reset) # A função agora retorna (bool, str)
        if ok:
            st.info(msg)
        else:
            st.error(msg)
    st.markdown("---") # Separador visual
    st.write("Ou, se você já tem um token e não está usando o link do e-mail:")
    token_input = st.text_input("Token de redefinição", key="reset_token_manual")
    nova_senha = st.text_input("Nova senha", type="password", key="reset_nova_senha_manual")
    confirmar_nova_senha_manual = st.text_input("Confirmar nova senha", type="password", key="reset_confirmar_nova_senha_manual")
    if st.button("Alterar senha manualmente", key="btn_alterar_senha_manual"):
        if not token_input or not nova_senha or not confirmar_nova_senha_manual:
            st.error("Preencha o token e a nova senha (e a confirmação).")
        elif nova_senha != confirmar_nova_senha_manual:
            st.error("As senhas não coincidem.")
        else:
            # 1. Validar o token e obter o e-mail do usuário
            token_valido_status, msg_validacao, email_usuario_reset = validar_token_reset(token_input)
            if token_valido_status and email_usuario_reset:
                # 2. Redefinir a senha
                ok_redefinir, msg_redefinir = redefinir_senha_com_token(token_input, nova_senha)
                if ok_redefinir:
                    st.success(msg_redefinir)
                    st.info("Você pode fazer login agora.")
                else:
                    st.error(msg_redefinir)
            else:
                st.error(msg_validacao) # Exibe a mensagem de erro da validação do token

# -------------------------------
# Páginas do aplicativo (após login)
# -------------------------------
if st.session_state.get("logged_in"):
    st.sidebar.markdown("---")
    app_pages = {
        "Avaliação de Dor": avaliacao_app,
        "Cadastro de Pet": cadastro_pet_app,
        # "Administração": admin_app, # Adicione esta linha quando tiver a página Admin
    }

    # Exibir página Admin apenas para usuários admin
    if st.session_state.user_type == "Admin": # Supondo que 'Admin' é o tipo de usuário para administradores
        app_pages["Administração"] = None # Substitua None pela sua app de administração

    selected_app_page = st.sidebar.selectbox("Navegar", list(app_pages.keys()), index=list(app_pages.keys()).index(st.session_state.page) if st.session_state.page in app_pages else 0)

    if selected_app_page == "Avaliação de Dor":
        avaliacao_app()
    elif selected_app_page == "Cadastro de Pet":
        cadastro_pet_app()
    # elif selected_app_page == "Administração":
    #     admin_app() # Chame sua app de administração aqui

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()


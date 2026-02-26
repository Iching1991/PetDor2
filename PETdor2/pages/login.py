import streamlit as st
from backend.auth.user import fazer_login
from backend.utils.validators import validar_email


# ==========================================================
# 🔐 LOGIN PAGE
# ==========================================================
def render():

    st.title("🔐 Login")

    # Se já logado
    if st.session_state.get("user_data"):
        st.info("Você já está logado.")
        return

    # 🔑 FORM KEY DINÂMICA (evita duplicação)
    form_key = "form_login_unique"

    with st.form(key=form_key):

        email = st.text_input("E-mail").strip().lower()
        senha = st.text_input("Senha", type="password")

        col1, col2 = st.columns(2)

        entrar = col1.form_submit_button("Entrar")
        esqueci = col2.form_submit_button("Esqueci a senha")

    # ======================================================
    # 🔄 AÇÕES
    # ======================================================

    # Ir para recuperação
    if esqueci:
        st.session_state.pagina = "recuperar_senha"
        st.rerun()

    # Tentar login
    if not entrar:
        return

    if not validar_email(email):
        st.error("E-mail inválido.")
        return

    sucesso, mensagem, dados = fazer_login(email, senha)

    if not sucesso:
        st.error(mensagem)
        return

    # Salvar sessão
    st.session_state["user_data"] = dados
    st.session_state["pagina"] = "home"

    st.success("Login realizado com sucesso!")
    st.rerun()

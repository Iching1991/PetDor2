import streamlit as st
from backend.auth.user import fazer_login
from backend.utils.validators import validar_email


def render():

    st.title("🔐 Login PETDor")

    if st.session_state.get("user_data"):
        st.success("Você já está logado.")
        return

    with st.form("form_login"):

        email = st.text_input("E-mail").strip().lower()
        senha = st.text_input("Senha", type="password")

        entrar = st.form_submit_button("Entrar")

    if not entrar:
        return

    # -------------------------
    # Validações
    # -------------------------

    if not validar_email(email):
        st.error("E-mail inválido.")
        return

    sucesso, msg, usuario = fazer_login(email, senha)

    if not sucesso:
        st.error(msg)
        return

    # -------------------------
    # Sessão
    # -------------------------

    st.session_state.user_data = usuario
    st.session_state.pagina = "home"

    st.success("Login realizado com sucesso!")
    st.rerun()


# ⚠️ EXECUÇÃO DIRETA (evita tela branca)
render()

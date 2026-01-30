import streamlit as st
from backend.auth.login import login_usuario
from backend.utils.validators import validar_email

def render():
    st.header("🔐 Login")

    if st.session_state.get("user_data"):
        st.info("Você já está logado.")
        return

    with st.form("login_form"):
        email = st.text_input("E-mail").strip().lower()
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if not entrar:
        return

    if not validar_email(email):
        st.error("E-mail inválido.")
        return

    sucesso, resultado = login_usuario(email, senha)

    if not sucesso:
        st.error(resultado)
        return

    st.session_state["user_data"] = resultado
    st.session_state["pagina"] = "home"
    st.success("Login realizado com sucesso!")
    st.rerun()

# PetDor/pages/login.py
import streamlit as st
from auth.user import autenticar_usuario, buscar_usuario_por_id

def app():
    st.header("🔐 Login")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        ok, msg, user_id = autenticar_usuario(email, senha)
        if ok:
            st.success(msg)
            st.session_state.user_id = user_id
        else:
            st.error(msg)

    # Se já estiver logado mostra um pequeno menu
    if st.session_state.get("user_id"):
        user = buscar_usuario_por_id(st.session_state["user_id"])
        st.info(f"Logado como: **{user['nome']}** ({user['email']})")
        if st.button("Sair"):
            del st.session_state["user_id"]
            st.experimental_rerun()

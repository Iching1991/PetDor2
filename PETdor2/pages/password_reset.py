import streamlit as st
from backend.auth.password_reset import solicitar_reset_senha

def render():
    st.header("🔐 Recuperar Senha")

    email = st.text_input("E-mail")

    if st.button("Enviar link"):
        sucesso, msg = solicitar_reset_senha(email)
        if sucesso:
            st.success(msg)
        else:
            st.error(msg)





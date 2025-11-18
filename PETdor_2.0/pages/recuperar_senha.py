import streamlit as st
from auth.password_reset import solicitar_reset_senha

st.set_page_config(page_title="Recuperar Senha - PETDor")

def main():
    st.title("🔐 Recuperar Senha")

    email = st.text_input("Digite seu e-mail cadastrado")

    if st.button("Enviar link de recuperação"):
        if not email:
            st.error("Digite um e-mail válido.")
            return

        ok = solicitar_reset_senha(email)

        if ok:
            st.success("Se o e-mail existir no sistema, enviaremos um link para redefinir sua senha.")
        else:
            st.error("Erro ao solicitar redefinição. Tente novamente.")

main()

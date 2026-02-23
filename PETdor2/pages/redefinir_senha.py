import streamlit as st
from backend.auth.password_reset import redefinir_senha


def render():

    st.title("🔐 Redefinir Senha")

    # Verifica se veio de recovery
    st.info("Digite sua nova senha abaixo.")

    nova = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    if st.button("Alterar senha"):

        if not nova or not confirmar:
            st.warning("Preencha os campos.")
            return

        if nova != confirmar:
            st.error("Senhas não coincidem.")
            return

        sucesso, msg = redefinir_senha(nova)

        if sucesso:
            st.success(msg)
            st.button(
                "Ir para login",
                on_click=lambda: st.switch_page("pages/login.py")
            )
        else:
            st.error(msg)


render()

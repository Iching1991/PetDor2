import streamlit as st
from backend.auth.password_reset import redefinir_senha


def render():

    st.title("🔐 Redefinir Senha")

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
            st.success("Senha redefinida com sucesso!")

            if st.button("Ir para login"):
                st.session_state.pagina = "login"
                st.rerun()
        else:
            st.error(msg)


# ⚠️ EXECUÇÃO DIRETA
render()

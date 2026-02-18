import streamlit as st
from backend.auth.password_reset import redefinir_senha


def render():
    st.title("🔐 Redefinir Senha")

    # Verifica sessão criada pelo link do e-mail
    session = st.session_state.get("supabase_session")

    if not session:
        st.info(
            "Abra esta página pelo link enviado ao seu e-mail."
        )

    nova = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    if st.button("Alterar senha"):

        if not nova or not confirmar:
            st.warning("Preencha todos os campos.")
            return

        if nova != confirmar:
            st.error("Senhas não coincidem.")
            return

        sucesso, msg = redefinir_senha(nova)

        if sucesso:
            st.success("Senha redefinida com sucesso!")
        else:
            st.error(msg)

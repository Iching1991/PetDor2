import streamlit as st
from backend.database.supabase_client import supabase
from backend.auth.password_reset import redefinir_senha


def render():

    st.title("🔐 Redefinir Senha")

    # Capturar parâmetros (query + hash workaround)
    params = st.query_params

    access_token = params.get("access_token")
    refresh_token = params.get("refresh_token")

    # Se token vier via query (modo alternativo)
    if access_token and refresh_token:
        supabase.auth.set_session(access_token, refresh_token)

    # Verifica sessão
    session = supabase.auth.get_session()

    if not session or not session.user:
        st.error("Sessão inválida. Solicite um novo link.")
        return

    st.success("Sessão válida. Digite sua nova senha.")

    nova = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    if st.button("Alterar senha"):

        if nova != confirmar:
            st.error("Senhas não coincidem.")
            return

        sucesso, msg = redefinir_senha(nova)

        if sucesso:
            st.success(msg)
        else:
            st.error(msg)


render()

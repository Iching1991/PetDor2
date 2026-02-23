import streamlit as st
from backend.database.supabase_client import supabase
from backend.auth.password_reset import redefinir_senha


def render():

    st.title("🔐 Redefinir Senha")

    # ✅ Compatível com Streamlit 1.29
    params = st.experimental_get_query_params()

    access_token = params.get("access_token", [None])[0]
    refresh_token = params.get("refresh_token", [None])[0]

    # Se vier token via query
    if access_token and refresh_token:
        supabase.auth.set_session(access_token, refresh_token)

    session = supabase.auth.get_session()

    if not session or not session.user:
        st.error("Sessão inválida. Solicite um novo link.")
        return

    st.success("Sessão válida. Digite sua nova senha.")

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
        else:
            st.error(msg)


render()

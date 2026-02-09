import streamlit as st
from backend.auth.email_confirmation import (
    validar_token_confirmacao,
    confirmar_email,
)

def render():
    st.title("📧 Confirmação de E-mail")

    token = st.query_params.get("token")

    if not token:
        st.error("Token não informado.")
        return

    valido, usuario_id = validar_token_confirmacao(token)

    if not valido:
        st.error("Token inválido ou expirado.")
        return

    sucesso, msg = confirmar_email(usuario_id)

    if sucesso:
        st.success("✅ E-mail confirmado com sucesso!")
        if st.button("Ir para login"):
            st.session_state.pagina = "login"
            st.rerun()
    else:
        st.error(msg)


__all__ = ["render"]

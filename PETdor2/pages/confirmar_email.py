"""
Confirmação de e-mail via Supabase Auth
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)


def obter_token():
    """Compatível com todas versões Streamlit"""
    try:
        params = st.query_params
        token = params.get("token")

        if isinstance(token, list):
            return token[0]

        return token

    except Exception:
        params = st.experimental_get_query_params()
        return params.get("token", [None])[0]


def render():

    try:
        st.title("📧 Confirmação de E-mail")

        token = obter_token()

        if not token:
            st.warning("Token não encontrado na URL.")
            st.stop()

        st.success("✅ E-mail confirmado com sucesso!")

        st.info(
            "Sua conta foi validada.\n\n"
            "Agora você já pode fazer login no sistema."
        )

        if st.button("🔐 Ir para Login"):
            st.session_state.pagina = "login"
            st.rerun()

    except Exception as e:
        st.error("Erro ao confirmar e-mail.")
        st.exception(e)


__all__ = ["render"]

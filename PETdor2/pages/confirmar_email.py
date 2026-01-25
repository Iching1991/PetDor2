"""
Página de confirmação de e-mail - PETDor2
O usuário acessa via link recebido por e-mail com token.
"""

import streamlit as st
import logging

from backend.auth.email_confirmation import (
    validar_token_confirmacao,
    confirmar_email,
)

logger = logging.getLogger(__name__)


# ==========================================================
# Helpers
# ==========================================================

def obter_token_url() -> str | None:
    """
    Obtém o token da URL de forma compatível
    com versões antigas e novas do Streamlit.
    """
    try:
        params = st.query_params
        token = params.get("token")
        if isinstance(token, list):
            return token[0]
        return token
    except Exception:
        params = st.experimental_get_query_params()
        return params.get("token", [None])[0]


# ==========================================================
# Render
# ==========================================================

def render():
    st.title("📧 Confirmação de E-mail")

    token = obter_token_url()

    if not token:
        st.warning("⚠️ Token de confirmação não fornecido.")
        st.info("Verifique o link enviado para seu e-mail.")
        st.stop()

    with st.spinner("🔎 Validando token..."):
        token_valido, usuario_id = validar_token_confirmacao(token)

    if not token_valido or not usuario_id:
        st.error("❌ Token inválido, expirado ou já utilizado.")
        st.info("Solicite um novo link de confirmação.")
        st.stop()

    with st.spinner("✅ Confirmando e-mail..."):
        sucesso, mensagem = confirmar_email(usuario_id)

    if sucesso:
        st.success("🎉 E-mail confirmado com sucesso!")
        st.info("Agora você já pode fazer login no PETDor.")

        if st.button("🔐 Ir para Login"):
            st.session_state.pagina = "login"
            st.rerun()
    else:
        st.error(f"❌ Não foi possível confirmar o e-mail: {mensagem}")
        logger.error(f"Erro ao confirmar e-mail do usuário {usuario_id}: {mensagem}")


__all__ = ["render"]

"""
Página de confirmação de e-mail - PETDor2
O usuário acessa via link recebido por e-mail com token.
Compatível com Streamlit Cloud
"""

import streamlit as st
import logging
from typing import Optional

# ==========================================================
# 🔧 IMPORTS DO BACKEND
# ==========================================================

from backend.auth.email_confirmation import (
    validar_token_confirmacao,
    confirmar_email,
)

logger = logging.getLogger(__name__)

# ==========================================================
# 🔗 Helpers
# ==========================================================

def obter_token_url() -> Optional[str]:
    """
    Obtém o token da URL de forma compatível
    com versões novas e antigas do Streamlit.
    """
    try:
        # Streamlit novo
        params = st.query_params
        token = params.get("token")
        if isinstance(token, list):
            return token[0]
        return token
    except Exception:
        # Streamlit antigo
        params = st.experimental_get_query_params()
        return params.get("token", [None])[0]

# ==========================================================
# 🖥️ Renderização
# ==========================================================

def render():
    st.title("📧 Confirmação de E-mail")

    token = obter_token_url()

    # ------------------------------------------------------
    # ❌ Token ausente
    # ------------------------------------------------------
    if not token:
        st.warning("⚠️ Token de confirmação não encontrado.")
        st.info("Verifique se você acessou corretamente o link enviado por e-mail.")
        st.stop()

    # ------------------------------------------------------
    # 🔎 Validar token
    # ------------------------------------------------------
    with st.spinner("🔎 Validando token de confirmação..."):
        token_valido, usuario_id = validar_token_confirmacao(token)

    if not token_valido or not usuario_id:
        st.error("❌ Token inválido, expirado ou já utilizado.")
        st.info("Solicite um novo link de confirmação.")
        st.stop()

    # ------------------------------------------------------
    # ✅ Confirmar e-mail
    # ------------------------------------------------------
    with st.spinner("✅ Confirmando seu e-mail..."):
        sucesso, mensagem = confirmar_email(usuario_id)

    if sucesso:
        st.success("🎉 E-mail confirmado com sucesso!")
        st.info("Agora você já pode acessar sua conta no PETDor.")

        if st.button("🔐 Ir para Login"):
            st.session_state.pagina = "login"
            st.rerun()
    else:
        st.error("❌ Não foi possível confirmar o e-mail.")
        st.info(mensagem)
        logger.error(f"Erro ao confirmar e-mail do usuário {usuario_id}: {mensagem}")

# ==========================================================
# 🚀 Execução protegida (evita tela branca)
# ==========================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro inesperado ao carregar a página de confirmação.")
    st.exception(e)

__all__ = ["render"]



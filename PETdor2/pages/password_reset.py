# PETdor2/pages/password_reset.py
"""
Página de recuperação de senha - PETDor2
Envia link de redefinição de senha por e-mail.
"""

import streamlit as st
import logging

from backend.auth.password_reset import solicitar_reset_senha
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)


# ==========================================================
# Render
# ==========================================================

def render():
    st.header("🔐 Recuperar Senha")

    st.write(
        "Digite o e-mail utilizado no cadastro. "
        "Se ele existir no sistema, enviaremos um link para redefinir sua senha."
    )

    email = st.text_input("📧 E-mail cadastrado").strip().lower()

    if st.button("📨 Enviar link de recuperação"):
        # -----------------------------
        # Validações
        # -----------------------------
        if not email:
            st.error("❌ Por favor, digite seu e-mail.")
            return

        if not validar_email(email):
            st.error("❌ E-mail inválido.")
            return

        # -----------------------------
        # Solicitar reset
        # -----------------------------
        try:
            with st.spinner("⏳ Processando solicitação..."):
                sucesso, mensagem = solicitar_reset_senha(email)

            if sucesso:
                st.success("✅ Solicitação realizada com sucesso!")
                st.info(
                    "📧 Verifique sua caixa de entrada e a pasta de spam. "
                    "O link pode levar alguns minutos para chegar."
                )
            else:
                # Mensagem genérica (não expõe se e-mail existe ou não)
                st.warning(mensagem)

        except Exception as e:
            logger.error("Erro ao solicitar reset de senha", exc_info=True)
            st.error(
                "⚠️ Erro interno ao processar a solicitação. "
                "Tente novamente mais tarde."
            )


__all__ = ["render"]

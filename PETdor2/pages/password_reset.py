"""
Página de recuperação de senha - PETDor2
Solicita envio de link de redefinição por e-mail.
"""

import streamlit as st
import logging

from backend.auth.password_reset import solicitar_reset_senha
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)

# ==========================================================
# 🖥️ Render
# ==========================================================

def render():
    st.header("🔐 Recuperar Senha")

    st.write(
        "Digite o e-mail utilizado no cadastro. "
        "Se ele existir no sistema, enviaremos um link para redefinir sua senha."
    )

    email = st.text_input(
        "📧 E-mail cadastrado",
        placeholder="seu@email.com",
    ).strip().lower()

    if st.button("📨 Enviar link de recuperação"):
        # --------------------------------------------------
        # ✅ Validações
        # --------------------------------------------------
        if not email:
            st.error("❌ Por favor, digite seu e-mail.")
            return

        if not validar_email(email):
            st.error("❌ E-mail inválido.")
            return

        # --------------------------------------------------
        # 🔁 Solicitação de reset
        # --------------------------------------------------
        try:
            with st.spinner("⏳ Enviando link de recuperação..."):
                sucesso, mensagem = solicitar_reset_senha(email)

            # ⚠️ Mensagem SEMPRE genérica (segurança)
            st.success("✅ Solicitação processada com sucesso!")
            st.info(mensagem)
            st.info("📬 Verifique sua caixa de entrada e a pasta de spam.")

            st.divider()

            if st.button("🔐 Voltar para o login"):
                st.session_state.pagina = "login"
                st.rerun()

        except Exception as e:
            logger.exception("Erro ao solicitar reset de senha")
            st.error(
                "⚠️ Erro interno ao processar a solicitação. "
                "Tente novamente mais tarde."
            )


# ==========================================================
# 🚀 Execução protegida (ANTI tela branca)
# ==========================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro inesperado ao carregar a página de recuperação de senha.")
    st.exception(e)


__all__ = ["render"]



"""
Página de recuperação de senha - PETDor2
Solicita envio de link de redefinição por e-mail.
Compatível com Supabase REST + RLS
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
        "Digite o e-mail usado na sua conta do **PETDor**. "
        "Se ele estiver cadastrado, enviaremos um link para redefinir sua senha."
    )

    email = st.text_input(
        "📧 E-mail cadastrado",
        placeholder="seu@email.com",
        key="email_recuperacao",
    ).strip().lower()

    if st.button("📨 Enviar link de recuperação"):
        # --------------------------------------------------
        # ✅ Validações
        # --------------------------------------------------
        if not email:
            st.error("❌ Informe seu e-mail.")
            return

        if not validar_email(email):
            st.error("❌ E-mail inválido.")
            return

        # --------------------------------------------------
        # 🔁 Solicitação de reset
        # --------------------------------------------------
        try:
            with st.spinner("⏳ Processando solicitação..."):
                sucesso, mensagem = solicitar_reset_senha(email)

            # ⚠️ Mensagem sempre genérica (segurança)
            st.success("✅ Solicitação processada com sucesso!")
            st.info(mensagem)
            st.info("📬 Verifique sua caixa de entrada e a pasta de spam.")

            st.divider()

            if st.button("🔐 Voltar para o login"):
                st.session_state.pagina = "login"
                st.rerun()

        except Exception:
            logger.exception("Erro ao solicitar recuperação de senha")
            st.error(
                "⚠️ Erro interno ao processar a solicitação. "
                "Tente novamente mais tarde."
            )


# ==========================================================
# 🛡️ Proteção contra tela branca (Streamlit Cloud)
# ==========================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro inesperado ao carregar a página de recuperação de senha.")
    st.exception(e)


__all__ = ["render"]


# PETdor2/pages/recuperar_senha.py
"""
Página de recuperação de senha - solicita reset de senha por e-mail.
"""
import streamlit as st
import logging

# 🔧 Import absoluto do backend
from backend.auth.password_reset import solicitar_reset_senha

logger = logging.getLogger(__name__)

def render():
    """Renderiza a página de recuperação de senha."""
    st.header("🔐 Recuperar Senha")

    st.write(
        "Digite o e-mail que você usou para criar sua conta no **PETDor**. "
        "Se ele existir no sistema, enviaremos um link para redefinir sua senha."
    )

    email = st.text_input("📧 E-mail cadastrado", key="input_email_recuperacao")

    if st.button("Enviar link de recuperação", key="btn_enviar_recuperacao"):
        if not email:
            st.error("❌ Por favor, digite seu e-mail.")
            return

        try:
            with st.spinner("⏳ Processando solicitação..."):
                sucesso, mensagem = solicitar_reset_senha(email)

            if sucesso:
                st.success(f"✅ {mensagem}")
                st.info("Verifique sua caixa de entrada e a pasta de spam.")
            else:
                st.error(f"⚠ {mensagem}")

        except Exception as e:
            logger.error(f"Erro em recuperar_senha: {e}", exc_info=True)
            st.error("⚠ Erro interno ao processar a solicitação. Tente novamente mais tarde.")


__all__ = ["render"]

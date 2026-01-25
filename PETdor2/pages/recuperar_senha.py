"""
Página de recuperação de senha - PETDor2
Solicita envio de link de redefinição por e-mail.
Compatível com Supabase REST + RLS
"""

import streamlit as st
import logging

from backend.auth.password_reset import solicitar_reset_senha

logger = logging.getLogger(__name__)


# ==========================================================
# Renderização
# ==========================================================

def render():
    st.header("🔐 Recuperar Senha")

    st.write(
        "Digite o e-mail usado na sua conta do **PETDor**. "
        "Se ele estiver cadastrado, enviaremos um link para redefinir sua senha."
    )

    email = st.text_input("📧 E-mail", key="email_recuperacao")

    if st.button("Enviar link de recuperação"):
        if not email:
            st.error("❌ Informe seu e-mail.")
            return

        with st.spinner("⏳ Processando solicitação..."):
            sucesso, mensagem = solicitar_reset_senha(email)

        if sucesso:
            st.success(f"✅ {mensagem}")
            st.info("📬 Verifique sua caixa de entrada e a pasta de spam.")
        else:
            st.error(f"❌ {mensagem}")


__all__ = ["render"]

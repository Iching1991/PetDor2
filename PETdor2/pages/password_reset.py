# PETdor2/pages/password_reset.py
"""
Página de redefinição de senha usando token JWT.
O usuário recebe um link por e-mail e redefine a senha aqui.
"""

import streamlit as st
import logging

# 🔧 Imports absolutos do backend
from backend.auth.password_reset import validar_token_reset, redefinir_senha_com_token

logger = logging.getLogger(__name__)

def render():
    """Renderiza a página de redefinição de senha."""
    st.header("🔐 Redefinir Senha")

    # Obtém token da URL (compatível Streamlit 1.30+)
    token = st.query_params.get("token", [None])[0]

    if not token:
        st.warning("⚠️ Token de redefinição não fornecido.")
        st.info("Verifique o link enviado para seu e-mail.")
        return

    # Valida token
    with st.spinner("⏳ Validando token..."):
        token_valido, dados = validar_token_reset(token)

    if not token_valido:
        erro_msg = dados.get("erro", "Token inválido.")
        st.error(f"❌ {erro_msg}")
        st.info("Solicite um novo link na página de login.")
        return

    email = dados.get("email", "seu e-mail")
    st.success(f"✅ Token válido para **{email}**")
    st.divider()

    # Formulário de redefinição
    st.subheader("📝 Nova Senha")
    nova_senha = st.text_input(
        "Nova senha",
        type="password",
        key="input_nova_senha",
        help="Mínimo 8 caracteres"
    )
    confirmar_senha = st.text_input(
        "Confirmar senha",
        type="password",
        key="input_confirmar_senha"
    )

    if st.button("🔄 Redefinir Senha", key="btn_redefinir"):
        # Validações
        if not nova_senha or not confirmar_senha:
            st.error("❌ Preencha todos os campos.")
            return

        if len(nova_senha) < 8:
            st.error("❌ Senha deve ter pelo menos 8 caracteres.")
            return

        if nova_senha != confirmar_senha:
            st.error("❌ As senhas não correspondem.")
            return

        # Redefine senha
        with st.spinner("⏳ Redefinindo senha..."):
            sucesso, mensagem = redefinir_senha_com_token(token, nova_senha)
            if sucesso:
                st.success(f"✅ {mensagem}")
                st.info("🔐 Você já pode fazer login com sua nova senha!")
                if st.button("🔐 Ir para Login"):
                    st.session_state.pagina = "login"
                    st.rerun()
            else:
                st.error(f"❌ {mensagem}")


__all__ = ["render"]

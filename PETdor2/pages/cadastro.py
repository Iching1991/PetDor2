"""
Página de cadastro de usuários - PETDor2
"""

import streamlit as st
from backend.auth.user import cadastrar_usuario
from backend.utils.validators import validar_email


def render():
    st.title("📝 Criar Conta")

    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail").strip().lower()
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    pais = st.selectbox("País", ["Brasil", "Portugal", "EUA", "Outro"])
    tipo = st.selectbox("Tipo de conta", ["Tutor", "Veterinário", "Clínica"])

    if st.button("Criar Conta"):
        # -----------------------------
        # Validações
        # -----------------------------
        if not nome or not email or not senha:
            st.error("❌ Preencha todos os campos obrigatórios.")
            return

        if not validar_email(email):
            st.error("❌ E-mail inválido.")
            return

        if senha != confirmar:
            st.error("❌ As senhas não coincidem.")
            return

        if len(senha) < 8:
            st.error("❌ A senha deve ter pelo menos 8 caracteres.")
            return

        # -----------------------------
        # Cadastro
        # -----------------------------
        sucesso, mensagem = cadastrar_usuario(
            nome=nome,
            email=email,
            senha=senha,
            tipo=tipo,
            pais=pais,
        )

        if sucesso:
            st.success("✅ Conta criada com sucesso!")
            st.info("📧 Verifique seu e-mail para confirmar a conta.")
            st.session_state.pagina = "login"
            st.rerun()
        else:
            st.error(mensagem)


# ============================================================
# 🚀 EXECUÇÃO OBRIGATÓRIA
# ============================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro ao carregar a página de cadastro.")
    st.exception(e)


__all__ = ["render"]

"""
Página de cadastro de usuários - PETDor2
Criação de conta inicial (Tutor / Veterinário / Clínica)
"""

import streamlit as st
import logging

from backend.auth.user import criar_usuario, buscar_usuario_por_email
from backend.auth.security import gerar_hash_senha
from backend.auth.email_confirmation import enviar_email_confirmacao

logger = logging.getLogger(__name__)


def render():
    st.title("📝 Criar Conta")
    st.markdown("Preencha os dados abaixo para criar sua conta no PETDor.")

    # --------------------------------------------------
    # Campos do formulário
    # --------------------------------------------------
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    pais = st.selectbox("País", ["Brasil", "Portugal", "EUA", "Outro"])
    tipo = st.selectbox("Tipo de conta", ["Tutor", "Veterinário", "Clínica"])

    # --------------------------------------------------
    # Criar conta
    # --------------------------------------------------
    if st.button("Criar Conta"):
        # -----------------------------
        # Validações
        # -----------------------------
        if not nome or not email or not senha:
            st.error("❌ Preencha todos os campos obrigatórios.")
            return

        if senha != confirmar:
            st.error("❌ As senhas não coincidem.")
            return

        if len(senha) < 8:
            st.error("❌ A senha deve ter pelo menos 8 caracteres.")
            return

        email = email.strip().lower()

        # Verifica se já existe
        if buscar_usuario_por_email(email):
            st.error("❌ Já existe uma conta com este e-mail.")
            return

        tipo_usuario = tipo.lower().replace("í", "i").replace("ã", "a")

        dados_usuario = {
            "nome": nome.strip(),
            "email": email,
            "senha_hash": gerar_hash_senha(senha),
            "tipo_usuario": tipo_usuario,  # tutor | veterinario | clinica
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": False,
        }

        try:
            usuario = criar_usuario(dados_usuario)

            if not usuario:
                st.error("❌ Não foi possível criar a conta.")
                return

            # Enviar e-mail de confirmação
            ok_email, msg_email = enviar_email_confirmacao(
                email=email,
                nome=nome,
                user_id=usuario["id"],
            )

            if not ok_email:
                st.warning(
                    "Conta criada, mas não foi possível enviar o e-mail de confirmação."
                )
                logger.warning(msg_email)

            st.success("✅ Conta criada com sucesso!")
            st.info("📧 Verifique seu e-mail para confirmar sua conta.")

            st.session_state.pagina = "login"
            st.rerun()

        except Exception as e:
            logger.exception("Erro ao criar conta")
            st.error("❌ Erro interno ao criar conta. Tente novamente.")

    # --------------------------------------------------
    # Observações
    # --------------------------------------------------
    st.markdown(
        """
        ---
        **Observações:**  
        - Contas *Veterinário* e *Clínica* poderão adicionar CRMV / CNPJ posteriormente.  
        - Você precisa confirmar seu e-mail antes de fazer login.  
        """
    )


__all__ = ["render"]

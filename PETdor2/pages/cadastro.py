"""
Página de cadastro de usuários - PETDor2
Criação de conta inicial (Tutor / Veterinário / Clínica)
"""

import streamlit as st
import hashlib

from backend.auth.user import criar_usuario


def hash_senha(senha: str) -> str:
    """
    Gera hash simples da senha.
    (Pode ser trocado por bcrypt/argon2 no futuro)
    """
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def render():
    st.title("📝 Criar Conta")
    st.markdown("Preencha os dados abaixo para criar sua conta no PETDor.")

    # -----------------------------
    # Campos do formulário
    # -----------------------------
    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")
    pais = st.selectbox("País", ["Brasil", "Portugal", "EUA", "Outro"])
    tipo = st.selectbox("Tipo de conta", ["Tutor", "Veterinário", "Clínica"])

    # -----------------------------
    # Botão de cadastro
    # -----------------------------
    if st.button("Criar Conta"):
        # Validações básicas
        if not nome or not email or not senha:
            st.error("❌ Preencha todos os campos obrigatórios.")
            return

        if senha != confirmar:
            st.error("❌ As senhas não coincidem.")
            return

        if len(senha) < 6:
            st.error("❌ A senha deve ter pelo menos 6 caracteres.")
            return

        dados_usuario = {
            "nome": nome.strip(),
            "email": email.strip().lower(),
            "senha_hash": hash_senha(senha),
            "tipo_usuario": tipo.lower(),   # tutor | veterinario | clinica
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": False,
        }

        try:
            resultado = criar_usuario(dados_usuario)

            if resultado:
                st.success("✅ Conta criada com sucesso!")
                st.info("📧 Verifique seu e-mail para confirmar sua conta.")
                st.session_state.pagina = "login"
                st.rerun()
            else:
                st.error("❌ Não foi possível criar a conta. Verifique os dados.")
        except Exception as e:
            st.error(f"❌ Erro ao criar conta: {e}")

    # -----------------------------
    # Observações
    # -----------------------------
    st.markdown(
        """
        ---
        **Observações:**  
        - Contas *Veterinário* e *Clínica* poderão adicionar CRMV / CNPJ posteriormente.  
        - O país é apenas informativo por enquanto.  
        """
    )


__all__ = ["render"]

# PETdor2/pages/conta.py
"""
Página de gerenciamento de conta do usuário.
Permite atualizar dados pessoais, redefinir senha e gerenciar preferências.
"""

import streamlit as st
import logging
from typing import Dict, Any

from backend.database import (
    supabase_table_update,
)

logger = logging.getLogger(__name__)

# ==========================================================
# Atualizar dados do usuário
# ==========================================================

def atualizar_dados_usuario(
    usuario_id: str,
    nome: str,
    email: str,
) -> bool:
    try:
        atualizado = supabase_table_update(
            table="usuarios",
            filters={"id": usuario_id},
            data={
                "nome": nome.strip(),
                "email": email.strip().lower(),
            },
        )
        return atualizado is not None
    except Exception as e:
        logger.error("Erro ao atualizar dados do usuário", exc_info=True)
        return False


# ==========================================================
# Renderização
# ==========================================================

def render():
    st.header("👤 Minha Conta")

    # ------------------------------------------------------
    # Usuário logado
    # ------------------------------------------------------
    usuario: Dict[str, Any] = st.session_state.get("user_data")
    if not usuario:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        st.stop()

    usuario_id = usuario["id"]

    # ------------------------------------------------------
    # Abas
    # ------------------------------------------------------
    tab1, tab2 = st.tabs(["📋 Dados Pessoais", "⚙️ Conta"])

    # ------------------------------------------------------
    # ABA 1: Dados pessoais
    # ------------------------------------------------------
    with tab1:
        st.subheader("📋 Dados Pessoais")

        nome = st.text_input(
            "Nome completo",
            value=usuario.get("nome", ""),
        )

        email = st.text_input(
            "E-mail",
            value=usuario.get("email", ""),
        )

        st.write(f"**Tipo de usuário:** {usuario.get('tipo_usuario', '-')}")
        st.write(f"**E-mail confirmado:** {'✅' if usuario.get('email_confirmado') else '❌'}")
        st.write(f"**Criado em:** {usuario.get('data_cadastro', '-')}")
        
        if st.button("💾 Salvar alterações"):
            if not nome or not email:
                st.warning("⚠️ Preencha todos os campos.")
            else:
                sucesso = atualizar_dados_usuario(usuario_id, nome, email)
                if sucesso:
                    st.success("✅ Dados atualizados com sucesso!")
                    st.session_state["user_data"]["nome"] = nome
                    st.session_state["user_data"]["email"] = email
                    st.rerun()
                else:
                    st.error("❌ Erro ao atualizar dados.")

    # ------------------------------------------------------
    # ABA 2: Conta (informativo por enquanto)
    # ------------------------------------------------------
    with tab2:
        st.subheader("⚙️ Conta")

        st.info(
            """
            🔐 **Segurança da conta**

            - Alteração de senha  
            - Recuperação de conta  
            - Preferências de notificação  

            Essas funcionalidades estarão disponíveis em versões futuras.
            """
        )

        st.divider()

        st.warning("🗑️ **Exclusão de conta**")
        st.write(
            "Para excluir sua conta, entre em contato com o suporte."
        )

__all__ = ["render"]

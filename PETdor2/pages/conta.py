"""
Página de gerenciamento de conta do usuário - PETDor2
Permite visualizar e atualizar dados básicos da conta.
Compatível com Supabase REST + RLS
"""

import streamlit as st
import logging
from typing import Dict, Any

from backend.database import supabase_table_update
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)

# ==========================================================
# 🔄 Atualizar dados do usuário
# ==========================================================

def atualizar_dados_usuario(
    usuario_id: str,
    nome: str,
    email: str,
) -> bool:
    """
    Atualiza nome e e-mail do usuário.
    """
    try:
        resultado = supabase_table_update(
            table="usuarios",
            filters={"id": usuario_id},
            data={
                "nome": nome.strip(),
                "email": email.strip().lower(),
            },
        )
        return resultado is not None
    except Exception as e:
        logger.exception("Erro ao atualizar dados do usuário")
        return False


# ==========================================================
# 🖥️ Renderização
# ==========================================================

def render():
    st.title("👤 Minha Conta")

    # ------------------------------------------------------
    # 🔐 Usuário logado
    # ------------------------------------------------------
    usuario: Dict[str, Any] = st.session_state.get("user_data")

    if not usuario:
        st.warning("⚠️ Você precisa estar logado para acessar esta página.")
        st.stop()

    usuario_id = usuario.get("id")

    # ------------------------------------------------------
    # 📑 Abas
    # ------------------------------------------------------
    tab_dados, tab_conta = st.tabs(
        ["📋 Dados Pessoais", "⚙️ Conta"]
    )

    # ======================================================
    # 📋 ABA 1 — Dados Pessoais
    # ======================================================
    with tab_dados:
        st.subheader("📋 Dados Pessoais")

        nome = st.text_input(
            "Nome completo",
            value=usuario.get("nome", ""),
        )

        email = st.text_input(
            "E-mail",
            value=usuario.get("email", ""),
        )

        st.divider()

        st.write(f"**Tipo de usuário:** {usuario.get('tipo_usuario', '-').title()}")
        st.write(
            "**E-mail confirmado:**",
            "✅ Sim" if usuario.get("email_confirmado") else "❌ Não",
        )
        st.write(
            f"**Criado em:** {usuario.get('criado_em', '—')}"
        )

        # --------------------------------------------------
        # 💾 Salvar
        # --------------------------------------------------
        if st.button("💾 Salvar alterações"):
            if not nome or not email:
                st.warning("⚠️ Preencha todos os campos.")
                return

            if not validar_email(email):
                st.error("❌ E-mail inválido.")
                return

            sucesso = atualizar_dados_usuario(
                usuario_id=usuario_id,
                nome=nome,
                email=email,
            )

            if sucesso:
                st.success("✅ Dados atualizados com sucesso!")

                # Atualiza session_state
                st.session_state["user_data"]["nome"] = nome
                st.session_state["user_data"]["email"] = email

                st.rerun()
            else:
                st.error("❌ Erro ao atualizar os dados.")

    # ======================================================
    # ⚙️ ABA 2 — Conta
    # ======================================================
    with tab_conta:
        st.subheader("⚙️ Conta")

        st.info(
            """
            🔐 **Segurança da conta**

            Funcionalidades que serão adicionadas:
            • Alteração de senha  
            • Recuperação de conta  
            • Preferências de notificação  
            """
        )

        st.divider()

        st.warning("🗑️ **Exclusão de conta**")
        st.write(
            "Para excluir sua conta, entre em contato com o suporte do PETDor."
        )


# ==========================================================
# 🚀 Execução protegida (evita tela branca)
# ==========================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro inesperado ao carregar a página de conta.")
    st.exception(e)

__all__ = ["render"]

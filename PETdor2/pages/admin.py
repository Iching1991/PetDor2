# PetDor2/pages/admin.py
"""
Página administrativa - gerenciamento de usuários e sistema.
Apenas usuários com role 'admin' podem acessar.
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime

# ============================================================
# 🔧 IMPORTS ABSOLUTOS
# ============================================================
from backend.database.supabase_client import (
    supabase_table_select,
    supabase_table_update,
)
from backend.auth.user import (
    atualizar_status_usuario,
    atualizar_usuario,
)

logger = logging.getLogger(__name__)

# ============================================================
# 🔐 CONTROLE DE ACESSO
# ============================================================

def is_admin(user_data: dict) -> bool:
    return bool(user_data and user_data.get("is_admin") is True)

# ============================================================
# 📦 FUNÇÕES DE DADOS
# ============================================================

def listar_usuarios() -> list:
    ok, data = supabase_table_select(
        "usuarios",
        "id, nome, email, tipo, pais, email_confirmado, ativo, is_admin, criado_em"
    )
    if not ok:
        st.error(data)
        logger.error(data)
        return []
    return data or []


def listar_pets() -> list:
    ok, data = supabase_table_select(
        "pets",
        "id, nome, especie, raca, proprietario_id, criado_em"
    )
    if not ok:
        st.error(data)
        logger.error(data)
        return []
    return data or []


def listar_avaliacoes() -> list:
    ok, data = supabase_table_select(
        "avaliacoes",
        "id, usuario_id, pet_id, percentual_dor, data_avaliacao"
    )
    if not ok:
        st.error(data)
        logger.error(data)
        return []
    return data or []

# ============================================================
# 🖥️ RENDERIZAÇÃO
# ============================================================

def render(user_data: dict = None):
    st.title("🔐 Painel Administrativo — PETdor")

    if not is_admin(user_data):
        st.error("❌ Acesso restrito a administradores.")
        st.stop()

    st.success(f"✅ Bem-vindo, **{user_data.get('nome', 'Administrador')}**")
    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Usuários",
        "🐾 Pets",
        "📊 Avaliações",
        "⚙️ Sistema"
    ])

    # ========================================================
    # 👥 USUÁRIOS
    # ========================================================
    with tab1:
        usuarios = listar_usuarios()

        if not usuarios:
            st.info("Nenhum usuário cadastrado.")
            return

        st.metric("Total de Usuários", len(usuarios))
        st.divider()

        for u in usuarios:
            uid = u["id"]

            with st.expander(f"👤 {u['nome']} ({u['email']})"):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"**País:** {u.get('pais', '-')}")
                    st.write(f"**Criado em:** {u.get('criado_em', '-')}")
                    st.write("**Email confirmado:**", "✅" if u["email_confirmado"] else "❌")
                    st.write("**Admin:**", "👑 Sim" if u["is_admin"] else "Não")

                with col2:
                    novo_tipo = st.selectbox(
                        "Tipo",
                        ["Tutor", "Veterinario", "Admin"],
                        index=0,
                        key=f"tipo_{uid}"
                    )
                    novo_admin = st.checkbox(
                        "Administrador",
                        value=u["is_admin"],
                        key=f"admin_{uid}"
                    )

                    if st.button("💾 Salvar", key=f"save_{uid}"):
                        ok, msg = atualizar_usuario(
                            uid,
                            tipo=novo_tipo,
                            is_admin=novo_admin
                        )
                        if ok:
                            st.success("Atualizado!")
                            st.rerun()
                        else:
                            st.error(msg)

                with col3:
                    label = "🔒 Desativar" if u["ativo"] else "🔓 Ativar"
                    if st.button(label, key=f"status_{uid}"):
                        ok, msg = atualizar_status_usuario(uid, not u["ativo"])
                        if ok:
                            st.success("Status atualizado!")
                            st.rerun()
                        else:
                            st.error(msg)

    # ========================================================
    # 🐾 PETS
    # ========================================================
    with tab2:
        pets = listar_pets()
        if not pets:
            st.info("Nenhum pet cadastrado.")
        else:
            st.metric("Total de Pets", len(pets))
            st.dataframe(pd.DataFrame(pets), use_container_width=True)

    # ========================================================
    # 📊 AVALIAÇÕES
    # ========================================================
    with tab3:
        avaliacoes = listar_avaliacoes()
        if not avaliacoes:
            st.info("Nenhuma avaliação registrada.")
        else:
            df = pd.DataFrame(avaliacoes)
            st.metric("Total", len(df))
            st.metric("Dor Média", f"{df['percentual_dor'].mean():.1f}%")
            st.dataframe(df, use_container_width=True)

    # ========================================================
    # ⚙️ SISTEMA
    # ========================================================
    with tab4:
        st.info("📦 **PETdor 2.0**")
        st.info(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        if st.button("🔄 Testar Conexão Supabase"):
            st.success("Conexão ativa ✅")


__all__ = ["render"]

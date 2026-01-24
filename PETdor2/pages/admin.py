"""
Página administrativa - gerenciamento de usuários e sistema.
Apenas usuários com is_admin = true podem acessar.
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime

# ============================================================
# 🔧 IMPORTS DO BACKEND
# ============================================================
from backend.database import (
    supabase_table_select,
    supabase_table_update,
)

from backend.auth.user import (
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
    data = supabase_table_select(
        table="usuarios",
        select="id, nome, email, tipo_usuario, pais, email_confirmado, ativo, is_admin, criado_em"
    )
    return data or []


def listar_animais() -> list:
    data = supabase_table_select(
        table="animais",
        select="id, nome, especie, raca, tutor_id, ativo, criado_em"
    )
    return data or []


def listar_avaliacoes() -> list:
    data = supabase_table_select(
        table="avaliacoes_dor",
        select="id, animal_id, avaliador_id, pontuacao_percentual, nivel_dor, criado_em"
    )
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
        "🐾 Animais",
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
                        "Tipo de usuário",
                        ["tutor", "veterinario", "clinica", "admin"],
                        index=["tutor", "veterinario", "clinica", "admin"].index(
                            u.get("tipo_usuario", "tutor")
                        ),
                        key=f"tipo_{uid}"
                    )

                    novo_admin = st.checkbox(
                        "Administrador",
                        value=u["is_admin"],
                        key=f"admin_{uid}"
                    )

                    if st.button("💾 Salvar alterações", key=f"save_{uid}"):
                        ok = atualizar_usuario(
                            uid,
                            {
                                "tipo_usuario": novo_tipo,
                                "is_admin": novo_admin
                            }
                        )
                        if ok:
                            st.success("Usuário atualizado com sucesso.")
                            st.rerun()
                        else:
                            st.error("Erro ao atualizar usuário.")

                with col3:
                    label = "🔒 Desativar" if u["ativo"] else "🔓 Ativar"
                    if st.button(label, key=f"status_{uid}"):
                        ok = atualizar_usuario(uid, {"ativo": not u["ativo"]})
                        if ok:
                            st.success("Status atualizado.")
                            st.rerun()
                        else:
                            st.error("Erro ao atualizar status.")

    # ========================================================
    # 🐾 ANIMAIS
    # ========================================================
    with tab2:
        animais = listar_animais()

        if not animais:
            st.info("Nenhum animal cadastrado.")
        else:
            st.metric("Total de Animais", len(animais))
            st.dataframe(pd.DataFrame(animais), use_container_width=True)

    # ========================================================
    # 📊 AVALIAÇÕES
    # ========================================================
    with tab3:
        avaliacoes = listar_avaliacoes()

        if not avaliacoes:
            st.info("Nenhuma avaliação registrada.")
        else:
            df = pd.DataFrame(avaliacoes)
            st.metric("Total de Avaliações", len(df))
            st.metric(
                "Dor Média",
                f"{df['pontuacao_percentual'].mean():.1f}%"
            )
            st.dataframe(df, use_container_width=True)

    # ========================================================
    # ⚙️ SISTEMA
    # ========================================================
    with tab4:
        st.info("📦 **PETdor 2.0**")
        st.info(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        if st.button("🔄 Testar conexão com Supabase"):
            try:
                teste = supabase_table_select("usuarios", limit=1)
                if teste is not None:
                    st.success("Conexão ativa ✅")
                else:
                    st.error("Falha na conexão ❌")
            except Exception as e:
                st.error(f"Erro: {e}")


__all__ = ["render"]

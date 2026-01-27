"""
Página administrativa - gerenciamento de usuários e sistema.
Acesso exclusivo para usuários com is_admin = true.
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime

from backend.database import (
    supabase_table_select,
    supabase_table_update,
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
    return supabase_table_select(
        table="usuarios",
        select="id, nome, email, tipo_usuario, pais, email_confirmado, ativo, is_admin, criado_em"
    ) or []


def listar_animais() -> list:
    return supabase_table_select(
        table="animais",
        select="id, nome, especie, raca, tutor_id, ativo, criado_em"
    ) or []


def listar_avaliacoes() -> list:
    return supabase_table_select(
        table="avaliacoes_dor",
        select="id, animal_id, avaliador_id, pontuacao_total, nivel_dor, criado_em"
    ) or []

# ============================================================
# 🖥️ RENDERIZAÇÃO
# ============================================================

def render():
    st.title("🔐 Painel Administrativo — PETdor")

    user_data = st.session_state.get("user_data")

    if not is_admin(user_data):
        st.error("❌ Acesso restrito a administradores.")
        st.stop()

    st.success(f"✅ Bem-vindo, **{user_data.get('nome', 'Administrador')}**")
    st.divider()

    tab_usuarios, tab_animais, tab_avaliacoes, tab_sistema = st.tabs([
        "👥 Usuários",
        "🐾 Animais",
        "📊 Avaliações",
        "⚙️ Sistema"
    ])

    # ========================================================
    # 👥 USUÁRIOS
    # ========================================================
    with tab_usuarios:
        usuarios = listar_usuarios()

        if not usuarios:
            st.info("Nenhum usuário cadastrado.")
        else:
            st.metric("Total de Usuários", len(usuarios))
            st.divider()

            tipos_validos = ["tutor", "veterinario", "clinica", "admin"]

            for u in usuarios:
                uid = u["id"]

                with st.expander(f"👤 {u['nome']} ({u['email']})"):
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        st.write(f"**País:** {u.get('pais', '-')}")
                        st.write(f"**Criado em:** {u.get('criado_em', '-')}")
                        st.write("**Email confirmado:**", "✅" if u["email_confirmado"] else "❌")
                        st.write("**Admin:**", "👑 Sim" if u["is_admin"] else "Não")
                        st.write("**Ativo:**", "✅" if u["ativo"] else "❌")

                    with col2:
                        tipo_atual = u.get("tipo_usuario", "tutor")

                        novo_tipo = st.selectbox(
                            "Tipo de usuário",
                            tipos_validos,
                            index=tipos_validos.index(tipo_atual) if tipo_atual in tipos_validos else 0,
                            key=f"tipo_{uid}"
                        )

                        novo_admin = st.checkbox(
                            "Administrador",
                            value=u["is_admin"],
                            key=f"admin_{uid}"
                        )

                        if st.button("💾 Salvar", key=f"save_{uid}"):
                            atualizado = supabase_table_update(
                                table="usuarios",
                                filters={"id": uid},
                                data={
                                    "tipo_usuario": novo_tipo,
                                    "is_admin": novo_admin
                                }
                            )

                            if atualizado is not None:
                                st.success("Usuário atualizado com sucesso.")
                                st.rerun()
                            else:
                                st.error("Erro ao atualizar usuário.")

                        st.divider()

                        if st.button(
                            "🔒 Desativar" if u["ativo"] else "🔓 Ativar",
                            key=f"status_{uid}"
                        ):
                            atualizado = supabase_table_update(
                                table="usuarios",
                                filters={"id": uid},
                                data={"ativo": not u["ativo"]}
                            )

                            if atualizado is not None:
                                st.success("Status atualizado.")
                                st.rerun()
                            else:
                                st.error("Erro ao atualizar status.")

    # ========================================================
    # 🐾 ANIMAIS
    # ========================================================
    with tab_animais:
        animais = listar_animais()

        if not animais:
            st.info("Nenhum animal cadastrado.")
        else:
            st.metric("Total de Animais", len(animais))
            st.dataframe(pd.DataFrame(animais), use_container_width=True)

    # ========================================================
    # 📊 AVALIAÇÕES
    # ========================================================
    with tab_avaliacoes:
        avaliacoes = listar_avaliacoes()

        if not avaliacoes:
            st.info("Nenhuma avaliação registrada.")
        else:
            df = pd.DataFrame(avaliacoes)
            st.metric("Total de Avaliações", len(df))

            if "pontuacao_total" in df.columns:
                st.metric("Dor Média", f"{df['pontuacao_total'].mean():.1f}")

            st.dataframe(df, use_container_width=True)

    # ========================================================
    # ⚙️ SISTEMA
    # ========================================================
    with tab_sistema:
        st.info("📦 **PETdor 2.0**")
        st.info(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

        if st.button("🔄 Testar conexão com Supabase"):
            teste = supabase_table_select("usuarios", limit=1)
            if teste is not None:
                st.success("Conexão ativa ✅")
            else:
                st.error("Falha na conexão ❌")


# ============================================================
# 🚀 EXECUÇÃO OBRIGATÓRIA (SEM ISSO A PÁGINA FICA EM BRANCO)
# ============================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro ao carregar o painel administrativo.")
    st.exception(e)

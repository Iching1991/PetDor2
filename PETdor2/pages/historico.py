"""
Página de histórico de avaliações do PETDor2
Exibe todas as avaliações realizadas pelo usuário logado.
"""

import streamlit as st
import pandas as pd
import logging
import json
from datetime import datetime
from typing import List, Dict, Any

from backend.database import (
    supabase_table_select,
    supabase_table_delete,
)

logger = logging.getLogger(__name__)


# ==========================================================
# Buscar avaliações do tutor
# ==========================================================

def buscar_avaliacoes_tutor(tutor_id: str) -> List[Dict[str, Any]]:
    try:
        avaliacoes = supabase_table_select(
            table="avaliacoes_dor",
            filters={"avaliador_id": tutor_id},
            order="criado_em.desc",
        ) or []

        if not avaliacoes:
            return []

        # Busca TODOS os animais do tutor (REST-safe)
        animais = supabase_table_select(
            table="animais",
            filters={"tutor_id": tutor_id},
        ) or []

        animais_map = {a["id"]: a for a in animais}

        # Enriquecer avaliações
        for a in avaliacoes:
            animal = animais_map.get(a.get("animal_id"), {})
            a["animal_nome"] = animal.get("nome", "Desconhecido")
            a["animal_especie"] = animal.get("especie", "Desconhecida")

        return avaliacoes

    except Exception:
        logger.exception("Erro ao buscar histórico de avaliações")
        return []


# ==========================================================
# Deletar avaliação
# ==========================================================

def deletar_avaliacao(avaliacao_id: str) -> bool:
    try:
        return supabase_table_delete(
            table="avaliacoes_dor",
            filters={"id": avaliacao_id},
        )
    except Exception:
        logger.exception("Erro ao deletar avaliação")
        return False


# ==========================================================
# Renderização
# ==========================================================

def render():
    st.title("📊 Histórico de Avaliações")

    usuario = st.session_state.get("user_data")
    if not usuario:
        st.warning("⚠️ Faça login para acessar seu histórico.")
        st.stop()

    tutor_id = usuario["id"]
    avaliacoes = buscar_avaliacoes_tutor(tutor_id)

    if not avaliacoes:
        st.info("📭 Você ainda não registrou avaliações.")
        return

    st.success(f"✅ {len(avaliacoes)} avaliação(ões) encontrada(s)")
    st.divider()

    for aval in avaliacoes:
        aval_id = aval.get("id")
        criado_em = aval.get("criado_em")
        pontuacao = aval.get("pontuacao_total", 0)
        respostas = aval.get("respostas", {})
        animal_nome = aval.get("animal_nome")
        animal_especie = aval.get("animal_especie")

        try:
            data_formatada = pd.to_datetime(criado_em).strftime("%d/%m/%Y %H:%M")
        except Exception:
            data_formatada = str(criado_em)

        with st.expander(
            f"🐾 {animal_nome} — {animal_especie} — {data_formatada} — Pontuação: {pontuacao}"
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"📅 **Data:** {data_formatada}")
                st.write(f"🐾 **Animal:** {animal_nome}")
                st.write(f"🏷️ **Espécie:** {animal_especie}")

            with col2:
                st.write(f"🧮 **Pontuação de Dor:** {pontuacao}")
                max_ref = max(pontuacao, 10)
                st.progress(min(pontuacao / max_ref, 1.0))

            st.divider()
            st.write("📝 **Respostas:**")
            st.json(respostas)

            st.divider()
            col_del, col_exp = st.columns(2)

            with col_del:
                if st.button("🗑️ Deletar avaliação", key=f"del_{aval_id}"):
                    if deletar_avaliacao(aval_id):
                        st.success("Avaliação deletada com sucesso.")
                        st.rerun()
                    else:
                        st.error("Erro ao deletar avaliação.")

            with col_exp:
                json_data = json.dumps(
                    {
                        "avaliacao_id": aval_id,
                        "animal": f"{animal_nome} ({animal_especie})",
                        "data": data_formatada,
                        "pontuacao_total": pontuacao,
                        "respostas": respostas,
                    },
                    ensure_ascii=False,
                    indent=2,
                )

                st.download_button(
                    label="📥 Exportar JSON",
                    data=json_data,
                    file_name=f"avaliacao_{aval_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key=f"export_{aval_id}",
                )

    # ------------------------------------------------------
    # Resumo
    # ------------------------------------------------------
    st.divider()
    st.subheader("📈 Resumo Geral")

    total = len(avaliacoes)
    media = sum(a.get("pontuacao_total", 0) for a in avaliacoes) / total

    col1, col2 = st.columns(2)
    col1.metric("Total de Avaliações", total)
    col2.metric("Pontuação Média", f"{media:.1f}")


__all__ = ["render"]

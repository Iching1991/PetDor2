"""
Página de Avaliação de Dor - PETDor2
Modelo completo com categorias
Compatível com Supabase REST + RLS + Triggers
"""

import streamlit as st
import logging
from typing import Dict, Any, List

from backend.database import (
    supabase_table_select,
    supabase_table_insert,
)
from backend.especies.index import (
    buscar_especie_por_id,
    get_escala_labels,
)

logger = logging.getLogger(__name__)

# ============================================================
# 🐾 Carregar animais do tutor
# ============================================================

def carregar_animais_do_tutor(tutor_id: str) -> List[Dict[str, Any]]:
    try:
        return supabase_table_select(
            table="animais",
            filters={
                "tutor_id": tutor_id,
                "ativo": True,
            },
            order="nome.asc",
        ) or []
    except Exception as e:
        logger.error(f"Erro ao carregar animais do tutor {tutor_id}: {e}", exc_info=True)
        st.error("Erro ao carregar seus animais.")
        return []

# ============================================================
# 💾 Salvar avaliação
# ============================================================

def salvar_avaliacao(
    animal_id: str,
    avaliador_id: str,
    respostas: Dict[str, Any],
    pontuacao_total: int,
) -> bool:
    try:
        result = supabase_table_insert(
            table="avaliacoes_dor",
            data={
                "animal_id": animal_id,
                "avaliador_id": avaliador_id,
                "respostas": respostas,
                "pontuacao_total": pontuacao_total,
                "nivel_dor": str(pontuacao_total),
            },
        )
        return result is not None
    except Exception as e:
        logger.error(f"Erro ao salvar avaliação: {e}", exc_info=True)
        return False

# ============================================================
# 🖥️ Render da página
# ============================================================

def render():
    st.title("📋 Avaliação de Dor")

    usuario = st.session_state.get("user_data")
    if not usuario:
        st.warning("Você precisa estar logado.")
        st.stop()

    tutor_id = usuario["id"]

    animais = carregar_animais_do_tutor(tutor_id)

    if not animais:
        st.info("Você ainda não possui animais cadastrados.")
        return

    animal = st.selectbox(
        "Selecione o animal",
        animais,
        format_func=lambda a: f"{a['nome']} ({a['especie']})",
    )

    especie_cfg = buscar_especie_por_id(animal["especie"])
    if not especie_cfg:
        st.error("Espécie sem configuração de avaliação.")
        return

    categorias = especie_cfg.get("categorias", [])
    if not categorias:
        st.warning("Esta espécie não possui categorias configuradas.")
        return

    st.subheader(f"🧪 Avaliação para {animal['nome']}")

    respostas: Dict[str, Any] = {}
    pontuacao_total = 0

    for categoria in categorias:
        st.markdown(f"### 🔹 {categoria['nome']}")

        for pergunta in categoria.get("perguntas", []):
            labels = get_escala_labels(pergunta["escala"])

            key_radio = f"{animal['id']}_{categoria['id']}_{pergunta['id']}"

            escolha = st.radio(
                pergunta["texto"],
                labels,
                key=key_radio,
            )

            respostas[pergunta["id"]] = escolha
            pontuacao_total += labels.index(escolha)

        st.divider()

    st.metric("Pontuação Total", pontuacao_total)

    if st.button("💾 Salvar Avaliação"):
        sucesso = salvar_avaliacao(
            animal_id=animal["id"],
            avaliador_id=tutor_id,
            respostas=respostas,
            pontuacao_total=pontuacao_total,
        )

        if sucesso:
            st.success("Avaliação salva com sucesso 🐾")
            st.rerun()
        else:
            st.error("Erro ao salvar avaliação.")

# ============================================================
# 🚀 EXECUÇÃO OBRIGATÓRIA
# ============================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro ao carregar a página de avaliação.")
    st.exception(e)

__all__ = ["render"]

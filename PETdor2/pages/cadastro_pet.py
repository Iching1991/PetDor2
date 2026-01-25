"""
Página de cadastro de pets - PETDor2
Permite que tutores cadastrem e visualizem seus pets.
Compatível com Supabase REST + RLS
"""

import streamlit as st
import logging
from typing import List, Dict, Any, Optional

from backend.database import (
    supabase_table_insert,
    supabase_table_select,
)
from backend.especies.index import listar_especies

logger = logging.getLogger(__name__)

# ==========================================================
# Helpers
# ==========================================================

def cadastrar_pet(
    tutor_id: str,
    nome: str,
    especie_id: str,
    raca: Optional[str],
    peso: Optional[float],
) -> bool:
    """Insere um novo pet no banco."""
    try:
        result = supabase_table_insert(
            table="animais",
            data={
                "tutor_id": tutor_id,
                "nome": nome,
                "especie": especie_id,
                "raca": raca,
                "peso": peso,
                "ativo": True,
            },
        )
        return result is not None
    except Exception as e:
        logger.error(f"Erro ao cadastrar pet: {e}", exc_info=True)
        return False


def listar_pets_do_tutor(tutor_id: str) -> List[Dict[str, Any]]:
    """Lista pets do tutor logado."""
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
        logger.error(f"Erro ao listar pets: {e}", exc_info=True)
        return []


# ==========================================================
# Render
# ==========================================================

def render():
    st.title("🐾 Cadastro de Pet")

    usuario = st.session_state.get("user_data")
    if not usuario:
        st.warning("Você precisa estar logado para cadastrar pets.")
        st.stop()

    tutor_id = usuario["id"]

    # ------------------------------------------------------
    # Cadastro
    # ------------------------------------------------------
    st.subheader("Cadastrar novo pet")

    especies = listar_especies()
    if not especies:
        st.error("Nenhuma espécie configurada no sistema.")
        return

    especies_map = {
        f"{e['nome']}": e["id"]
        for e in especies
    }

    with st.form("form_cadastro_pet"):
        nome = st.text_input("Nome do pet")
        especie_nome = st.selectbox(
            "Espécie",
            list(especies_map.keys()),
        )
        raca = st.text_input("Raça (opcional)")
        peso = st.number_input(
            "Peso (kg)",
            min_value=0.0,
            step=0.1,
            format="%.1f",
        )

        submitted = st.form_submit_button("Cadastrar Pet")

    if submitted:
        if not nome:
            st.error("❌ Informe o nome do pet.")
            return

        sucesso = cadastrar_pet(
            tutor_id=tutor_id,
            nome=nome.strip(),
            especie_id=especies_map[especie_nome],
            raca=raca.strip() or None,
            peso=peso if peso > 0 else None,
        )

        if sucesso:
            st.success(f"✅ Pet **{nome}** cadastrado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Erro ao cadastrar o pet.")

    # ------------------------------------------------------
    # Lista
    # ------------------------------------------------------
    st.divider()
    st.subheader("Seus pets cadastrados")

    pets = listar_pets_do_tutor(tutor_id)

    if not pets:
        st.info("Você ainda não cadastrou nenhum pet.")
        return

    for pet in pets:
        with st.expander(f"🐾 {pet['nome']} ({pet['especie']})"):
            st.write(f"**Raça:** {pet.get('raca') or 'Não informada'}")
            st.write(
                f"**Peso:** {pet['peso']:.1f} kg"
                if pet.get("peso")
                else "**Peso:** Não informado"
            )


__all__ = ["render"]

"""
Página de histórico de avaliações do PETDor2
Exibe avaliações do usuário logado.
Exportação em PDF.
Deleção permitida apenas para administradores.
"""

import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

from backend.database import (
    supabase_table_select,
    supabase_table_delete,
)

logger = logging.getLogger(__name__)

# ==========================================================
# Buscar avaliações
# ==========================================================

def buscar_avaliacoes_usuario(usuario_id: str) -> List[Dict[str, Any]]:
    try:
        avaliacoes = supabase_table_select(
            table="avaliacoes_dor",
            filters={"avaliador_id": usuario_id},
            order="criado_em.desc",
        ) or []

        animais = supabase_table_select(
            table="animais",
            filters={"tutor_id": usuario_id},
        ) or []

        animais_map = {a["id"]: a for a in animais}

        for a in avaliacoes:
            animal = animais_map.get(a.get("animal_id"), {})
            a["animal_nome"] = animal.get("nome", "Desconhecido")
            a["animal_especie"] = animal.get("especie", "Desconhecida")

        return avaliacoes

    except Exception:
        logger.exception("Erro ao buscar avaliações")
        return []


# ==========================================================
# PDF
# ==========================================================

def gerar_pdf_avaliacao(avaliacao: Dict[str, Any]) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("PETDor – Relatório de Avaliação de Dor", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"<b>Animal:</b> {avaliacao['animal_nome']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Espécie:</b> {avaliacao['animal_especie']}", styles["Normal"]))
    elements.append(
        Paragraph(
            f"<b>Data:</b> {pd.to_datetime(avaliacao['criado_em']).strftime('%d/%m/%Y %H:%M')}",
            styles["Normal"],
        )
    )
    elements.append(Paragraph(f"<b>Pontuação Total:</b> {avaliacao['pontuacao_total']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("Respostas:", styles["Heading2"]))
    elements.append(Spacer(1, 6))

    for pergunta, resposta in avaliacao.get("respostas", {}).items():
        elements.append(
            Paragraph(
                f"- {pergunta.replace('_', ' ').title()}: <b>{resposta}</b>",
                styles["Normal"],
            )
        )

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


# ==========================================================
# Delete (admin)
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
# Render
# ==========================================================

def render():
    st.title("📊 Histórico de Avaliações")

    usuario = st.session_state.get("user_data")

    # ⚠️ NÃO usar st.stop antes de renderizar algo
    if not usuario:
        st.warning("Você precisa estar logado para acessar esta página.")
        return

    usuario_id = usuario["id"]
    is_admin = bool(usuario.get("is_admin"))

    avaliacoes = buscar_avaliacoes_usuario(usuario_id)

    if not avaliacoes:
        st.info("Nenhuma avaliação encontrada.")
        return

    for aval in avaliacoes:
        aval_id = aval["id"]

        data_formatada = pd.to_datetime(aval["criado_em"]).strftime("%d/%m/%Y %H:%M")

        with st.expander(
            f"🐾 {aval['animal_nome']} — {aval['animal_especie']} — {data_formatada} — Dor: {aval['pontuacao_total']}"
        ):
            st.metric("Pontuação de Dor", aval["pontuacao_total"])
            st.json(aval["respostas"])

            col1, col2 = st.columns(2)

            # PDF
            with col1:
                pdf = gerar_pdf_avaliacao(aval)
                st.download_button(
                    label="📄 Exportar PDF",
                    data=pdf,
                    file_name=f"avaliacao_{aval_id}.pdf",
                    mime="application/pdf",
                )

            # Delete (admin only)
            with col2:
                if is_admin:
                    if st.button("🗑️ Deletar avaliação", key=f"del_{aval_id}"):
                        if deletar_avaliacao(aval_id):
                            st.success("Avaliação deletada.")
                            st.rerun()
                        else:
                            st.error("Erro ao deletar.")
                else:
                    st.info("🔒 Apenas administradores podem deletar.")


# ==========================================================
# 🚀 EXECUÇÃO AUTOMÁTICA (ESSENCIAL)
# ==========================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro ao carregar o histórico de avaliações.")
    st.exception(e)


__all__ = ["render"]

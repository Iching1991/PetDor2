# PETdor2/pages/historico.py

import streamlit as st
from PETdor2.database.connection import conectar_db
import os

USING_POSTGRES = bool(os.getenv("DB_HOST"))
PH = "%s" if USING_POSTGRES else "?"


def buscar_avaliacoes_usuario(usuario_id):
    conn = conectar_db()
    cur = conn.cursor()

    sql = f"""
        SELECT a.id,
               a.data_avaliacao,
               a.percentual_dor,
               a.observacoes,
               p.nome AS pet_nome,
               p.especie AS pet_especie
        FROM avaliacoes a
        JOIN pets p ON a.pet_id = p.id
        WHERE a.usuario_id = {PH}
        ORDER BY a.data_avaliacao DESC
    """

    cur.execute(sql, (usuario_id,))
    rows = cur.fetchall()

    conn.close()
    return rows


def deletar_avaliacao(avaliacao_id):
    conn = conectar_db()
    cur = conn.cursor()

    sql = f"DELETE FROM avaliacoes WHERE id = {PH}"
    cur.execute(sql, (avaliacao_id,))

    conn.commit()
    conn.close()


def render():
    st.header("📊 Histórico de Avaliações")

    usuario = st.session_state.get("usuario")
    if not usuario:
        st.warning("Faça login para acessar seu histórico.")
        st.session_state.pagina = "login"
        st.stop()

    usuario_id = usuario["id"]

    # Buscar avaliações
    avaliacoes = buscar_avaliacoes_usuario(usuario_id)

    if not avaliacoes:
        st.info("Você ainda não registrou avaliações.")
        return

    # Detectar formato de row
    def get(row, k, idx):
        return row[k] if hasattr(row, "keys") else row[idx]

    # Renderizar todas as avaliações
    for a in avaliacoes:
        aval_id = get(a, "id", 0)
        data = get(a, "data_avaliacao", 1)
        dor = get(a, "percentual_dor", 2)
        obs = get(a, "observacoes", 3)
        pet_nome = get(a, "pet_nome", 4)
        pet_esp = get(a, "pet_especie", 5)

        with st.expander(f"{pet_nome} — {pet_esp} — {data} — Dor: {dor}%"):
            st.write(f"📅 **Data:** {data}")
            st.write(f"🐾 **Pet:** {pet_nome} ({pet_esp})")
            st.write(f"🔥 **Percentual de Dor:** {dor}%")
            st.write("📝 **Observações:**")
            st.write(obs or "Nenhuma observação.")

            if st.button("🗑 Deletar avaliação", key=f"del_{aval_id}"):
                try:
                    deletar_avaliacao(aval_id)
                    st.success("Avaliação deletada com sucesso.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erro ao deletar avaliação: {e}")

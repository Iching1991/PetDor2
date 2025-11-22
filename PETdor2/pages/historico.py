# PetDor/pages/historico.py
import streamlit as st
from database.connection import conectar_db

def buscar_avaliacoes_usuario(usuario_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.data_avaliacao, a.percentual_dor, a.observacoes,
               p.nome as pet_nome, p.especie as pet_especie
        FROM avaliacoes a
        JOIN pets p ON a.pet_id = p.id
        WHERE a.usuario_id = ?
        ORDER BY a.data_avaliacao DESC
    """, (usuario_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def deletar_avaliacao(avaliacao_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM avaliacoes WHERE id = ?", (avaliacao_id,))
    conn.commit()
    conn.close()

def app(user_id: int):
    st.header("📊 Histórico de Avaliações")
    if not user_id:
        st.warning("Faça login para ver seu histórico.")
        return

    avaliacoes = buscar_avaliacoes_usuario(user_id)
    if not avaliacoes:
        st.info("Você ainda não registrou avaliações.")
        return

    for a in avaliacoes:
        with st.expander(f"{a['pet_nome']} — {a['pet_especie']} — {a['data_avaliacao']} — Dor: {a['percentual_dor']}%"):
            st.write(f"**Data:** {a['data_avaliacao']}")
            st.write(f"**Pet:** {a['pet_nome']} ({a['pet_especie']})")
            st.write(f"**Percentual de dor:** {a['percentual_dor']}%")
            st.write("**Observações:**")
            st.write(a['observacoes'] or "Nenhuma observação.")
            if st.button("Deletar avaliação", key=f"del_{a['id']}"):
                try:
                    deletar_avaliacao(a['id'])
                    st.success("Avaliação deletada.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Erro ao deletar: {e}")

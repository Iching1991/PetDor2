# PetDor/pages/avaliacao.py
import streamlit as st
from database.connection import conectar_db
from utils.pdf_generator import gerar_pdf

def buscar_pets(tutor_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nome FROM pets WHERE tutor_id = ?", (tutor_id,))
    pets = cur.fetchall()
    conn.close()
    return pets

def registrar_avaliacao_db(pet_id, usuario_id, percentual, observacoes):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO avaliacoes (pet_id, usuario_id, percentual_dor, observacoes)
        VALUES (?, ?, ?, ?)
    """, (pet_id, usuario_id, percentual, observacoes))
    conn.commit()
    conn.close()

def app(user_id: int):
    st.header("📋 Avaliação de Dor")
    if not user_id:
        st.warning("Faça login para registrar avaliações.")
        return

    pets = buscar_pets(user_id)
    if not pets:
        st.info("Cadastre um pet primeiro em 'Cadastro de Pet'.")
        return

    pet_names = [p["nome"] for p in pets]
    pet_sel = st.selectbox("Selecione o pet", pet_names)
    pet_id = next(p["id"] for p in pets if p["nome"] == pet_sel)

    percentual = st.slider("Percentual de dor (%)", 0, 100, 50)
    observacoes = st.text_area("Observações")

    if st.button("Registrar Avaliação"):
        try:
            registrar_avaliacao_db(pet_id, user_id, percentual, observacoes)
            st.success("Avaliação registrada.")
        except Exception as e:
            st.error(f"Erro ao registrar avaliação: {e}")

    if st.button("Gerar PDF da avaliação"):
        try:
            filename = gerar_pdf(pet_sel, percentual, observacoes)
            with open(filename, "rb") as f:
                st.download_button("Baixar PDF", f, file_name=filename)
        except Exception as e:
            st.error(f"Erro ao gerar PDF: {e}")

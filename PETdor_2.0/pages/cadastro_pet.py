# PetDor/pages/cadastro_pet.py
import streamlit as st
from database.connection import conectar_db
from especies.loader import listar_especies

def cadastrar_pet_db(tutor_id, nome, especie, raca, peso):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pets (tutor_id, nome, especie, raca, peso)
        VALUES (?, ?, ?, ?, ?)
    """, (tutor_id, nome, especie, raca, peso))
    conn.commit()
    conn.close()

def listar_pets_db(tutor_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pets WHERE tutor_id = ?", (tutor_id,))
    pets = cur.fetchall()
    conn.close()
    return pets

def app(user_id: int):
    st.header("🐾 Cadastro de Pet")
    if not user_id:
        st.warning("Você precisa estar logado para cadastrar pets.")
        return

    with st.form("form_cadastro_pet"):
        nome = st.text_input("Nome do pet")
        especie = st.selectbox("Espécie", listar_especies())
        raca = st.text_input("Raça (opcional)")
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Cadastrar Pet")

    if submitted:
        if not nome or not especie:
            st.error("Nome e espécie são obrigatórios.")
        else:
            try:
                cadastrar_pet_db(user_id, nome, especie, raca, peso if peso > 0 else None)
                st.success(f"Pet '{nome}' cadastrado com sucesso.")
            except Exception as e:
                st.error(f"Erro ao cadastrar pet: {e}")

    st.markdown("---")
    st.subheader("Seus pets")
    pets = listar_pets_db(user_id)
    if not pets:
        st.info("Nenhum pet cadastrado ainda.")
    else:
        for p in pets:
            st.write(f"- **{p['nome']}** — {p['especie']} — {p['raca'] or 'Raça não informada'} — {p['peso'] or 'Peso não informado'} kg")

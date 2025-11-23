# PETdor2/pages/admin.py

import streamlit as st
import os
from PETdor2.database.connection import conectar_db
from PETdor2.auth.user import atualizar_status_usuario, atualizar_tipo_usuario

USING_POSTGRES = bool(os.getenv("DB_HOST"))


# ==========================================================
# Verifica se o usuário é admin
# (Versão simples: admin = tipo_usuario == 'Admin')
# ==========================================================
def is_admin(usuario):
    if not usuario:
        return False

    # Para PostgreSQL → dict-like
    # Para SQLite → Row (índices)
    try:
        tipo = usuario["tipo_usuario"]
    except Exception:
        tipo = usuario[4]  # índice seguro no SQLite

    return tipo.lower() == "admin"


# ==========================================================
# Consulta usuários
# ==========================================================
def listar_usuarios():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, email, tipo_usuario, pais, email_confirmado,
               ativo, criado_em
        FROM usuarios
        ORDER BY criado_em DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


# ==========================================================
# Página principal
# ==========================================================
def render():
    st.title("🔐 Painel Administrativo — PETdor")

    usuario = st.session_state.get("usuario")

    if not usuario or not is_admin(usuario):
        st.error("Acesso restrito a administradores.")
        return

    st.success(f"Bem-vindo, administrador **{usuario['nome']}**!")

    st.markdown("---")
    st.subheader("👥 Usuários cadastrados")

    usuarios = listar_usuarios()

    if not usuarios:
        st.info("Nenhum usuário cadastrado.")
        return

    for u in usuarios:
        # Compatível com dict (PostgreSQL) e Row (SQLite)
        get = lambda row, key, idx: row[key] if hasattr(row, "keys") else row[idx]

        uid = get(u, "id", 0)
        nome = get(u, "nome", 1)
        email = get(u, "email", 2)
        tipo = get(u, "tipo_usuario", 3)
        pais = get(u, "pais", 4)
        confirmado = get(u, "email_confirmado", 5)
        ativo = get(u, "ativo", 6)
        criado_em = get(u, "criado_em", 7)

        col1, col2, col3 = st.columns([3, 2, 2])

        with col1:
            st.write(f"**{nome}**  \n📧 {email}  \n🌎 {pais}")
            st.write(f"🕒 Criado em: {criado_em}")
            st.write(f"✔ Confirmado: {'Sim' if confirmado else 'Não'}")

        with col2:
            novo_tipo = st.selectbox(
                "Tipo",
                ["Tutor", "Veterinario", "Admin"],
                index=["Tutor", "Veterinario", "Admin"].index(tipo),
                key=f"tipo_{uid}",
            )

            if novo_tipo != tipo:
                if st.button(f"Salvar tipo ({uid})", key=f"btn_tipo_{uid}"):
                    atualizar_tipo_usuario(uid, novo_tipo)
                    st.success("Tipo atualizado!")
                    st.experimental_rerun()

        with col3:
            novo_status = not ativo
            status_label = "Desativar" if ativo else "Ativar"

            if st.button(f"{status_label} ({uid})", key=f"btn_status_{uid}"):
                atualizar_status_usuario(uid, novo_status)
                st.success("Status atualizado!")
                st.experimental_rerun()

        st.markdown("---")



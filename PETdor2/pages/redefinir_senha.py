"""
Página de redefinição de senha - PETDor2
"""

import streamlit as st
from supabase import create_client

# ============================================================
# 🔑 CONFIG
# ============================================================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# 🧠 CAPTURAR TOKEN
# ============================================================

def get_token():

    params = st.query_params

    access_token = params.get("access_token")
    type_ = params.get("type")

    if type_ != "recovery":
        return None

    return access_token


# ============================================================
# 🔐 RESET
# ============================================================

def render():

    st.title("🔑 Redefinir senha")

    token = get_token()

    if not token:
        st.error("Link inválido ou expirado.")
        st.stop()

    nova_senha = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar nova senha", type="password")

    if st.button("Atualizar senha"):

        if nova_senha != confirmar:
            st.error("As senhas não coincidem.")
            return

        if len(nova_senha) < 8:
            st.error("Senha deve ter pelo menos 8 caracteres.")
            return

        try:
            supabase.auth.set_session(
                access_token=token,
                refresh_token=token
            )

            supabase.auth.update_user({
                "password": nova_senha
            })

            st.success("Senha atualizada com sucesso!")
            st.info("Você já pode fazer login.")

        except Exception as e:
            st.error("Erro ao atualizar senha.")
            st.exception(e)


# ============================================================
# 🚀 EXECUÇÃO
# ============================================================

render()
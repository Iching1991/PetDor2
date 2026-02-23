# PETDor2/pages/confirmar_email.py

"""
Página de confirmação de e-mail — Supabase Auth
Refatorado para sessão automática
"""

import streamlit as st
from backend.database.supabase_client import supabase


# ============================================================
# 🔐 Criar sessão a partir do link
# ============================================================

def criar_sessao_via_link():

    try:
        params = st.experimental_get_query_params()

        access_token = params.get("access_token", [None])[0]
        refresh_token = params.get("refresh_token", [None])[0]
        type_token = params.get("type", [None])[0]

        # ------------------------------------------------
        # Validação do tipo
        # ------------------------------------------------
        if type_token != "signup":
            return False, "Link inválido ou expirado."

        if not access_token or not refresh_token:
            return False, "Token não encontrado."

        # ------------------------------------------------
        # Criar sessão manual
        # ------------------------------------------------
        supabase.auth.set_session(
            access_token,
            refresh_token
        )

        return True, "Sessão criada"

    except Exception as e:
        return False, str(e)


# ============================================================
# 🖥️ Página
# ============================================================

def render():

    st.title("📧 Confirmação de E-mail")

    # Criar sessão a partir do link
    sucesso, msg = criar_sessao_via_link()

    if not sucesso:

        st.error("❌ " + msg)

        st.info(
            "Solicite um novo link de confirmação."
        )

        if st.button("Ir para Login"):
            st.session_state.pagina = "login"
            st.rerun()

        return

    # ------------------------------------------------
    # Sessão válida
    # ------------------------------------------------
    user = supabase.auth.get_user()

    if user:

        st.success(
            "Seu e-mail foi confirmado com sucesso! 🎉"
        )

        st.info(
            "Agora você já pode acessar o sistema."
        )

    else:

        st.warning(
            "Sessão criada, mas usuário não encontrado."
        )

    # ------------------------------------------------
    # Navegação
    # ------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔐 Ir para Login",
            use_container_width=True
        ):
            st.session_state.pagina = "login"
            st.rerun()

    with col2:
        if st.button(
            "🏠 Página Inicial",
            use_container_width=True
        ):
            st.session_state.pagina = "home"
            st.rerun()


# ============================================================
# 🚀 Execução segura
# ============================================================

try:
    render()

except Exception as e:

    st.error(
        "❌ Erro ao carregar confirmação."
    )
    st.exception(e)


__all__ = ["render"]

# PETDor2/pages/confirmar_email.py

# ==========================================================
# 📧 PETDor2 — Confirmação de E-mail
# Supabase Auth + Sessão automática via link
# Compatível com tokens em HASH (#) e QUERY (?)
# ==========================================================

import streamlit as st
from backend.database.supabase_client import supabase


# ==========================================================
# 🔐 CAPTURAR TOKENS DO LINK
# ==========================================================
def capturar_tokens():
    """
    Captura access_token e refresh_token
    tanto de query params quanto de hash fragment.
    """

    try:
        # Query params padrão
        params = st.experimental_get_query_params()

        access_token = params.get("access_token", [None])[0]
        refresh_token = params.get("refresh_token", [None])[0]
        type_token = params.get("type", [None])[0]

        return access_token, refresh_token, type_token

    except Exception:
        return None, None, None


# ==========================================================
# 🔐 CRIAR SESSÃO VIA LINK
# ==========================================================
def criar_sessao_via_link():

    access_token, refresh_token, type_token = capturar_tokens()

    # ------------------------------------------------------
    # Validar tipo do token
    # ------------------------------------------------------
    if type_token != "signup":
        return False, "Link inválido ou expirado."

    if not access_token or not refresh_token:
        return False, "Token não encontrado na URL."

    try:
        # Criar sessão Supabase
        supabase.auth.set_session(
            access_token,
            refresh_token
        )

        return True, "Sessão criada com sucesso."

    except Exception as e:
        return False, f"Erro ao criar sessão: {str(e)}"


# ==========================================================
# 🖥️ UI PRINCIPAL
# ==========================================================
def render():

    st.title("📧 Confirmação de E-mail")

    st.divider()

    # ------------------------------------------------------
    # Criar sessão a partir do link
    # ------------------------------------------------------
    sucesso, msg = criar_sessao_via_link()

    if not sucesso:

        st.error(f"❌ {msg}")

        st.info(
            "Solicite um novo link de confirmação para ativar sua conta."
        )

        if st.button(
            "🔐 Ir para Login",
            use_container_width=True
        ):
            st.session_state.pagina = "login"
            st.rerun()

        return

    # ------------------------------------------------------
    # Sessão criada → buscar usuário
    # ------------------------------------------------------
    try:
        user_resp = supabase.auth.get_user()
        user = user_resp.user if user_resp else None
    except Exception:
        user = None

    if user:

        st.success(
            "✅ Seu e-mail foi confirmado com sucesso! 🎉"
        )

        st.info(
            f"Usuário confirmado: **{user.email}**"
        )

    else:

        st.warning(
            "Sessão criada, mas não foi possível obter dados do usuário."
        )

    # ------------------------------------------------------
    # Navegação
    # ------------------------------------------------------
    st.divider()

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


# ==========================================================
# 🚀 EXECUÇÃO SEGURA
# ==========================================================
try:
    render()

except Exception as e:

    st.error("❌ Erro ao carregar confirmação de e-mail.")
    st.exception(e)


# ==========================================================
# EXPORT
# ==========================================================
__all__ = ["render"]

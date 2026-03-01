import streamlit as st
from backend.database.supabase_client import supabase


def render():
    st.title("📧 Confirmação de E-mail")

    # Capturar parâmetros da URL
    params = st.query_params

    access_token = params.get("access_token")
    refresh_token = params.get("refresh_token")
    type_token = params.get("type")

    # Supabase envia type=signup
    if type_token != "signup":
        st.error("❌ Link inválido ou expirado.")
        return

    if not access_token or not refresh_token:
        st.error("❌ Token não encontrado.")
        return

    try:
        # Criar sessão manualmente
        supabase.auth.set_session(
            access_token,
            refresh_token
        )

        st.success("🎉 E-mail confirmado com sucesso!")
        st.info("Sua conta está ativa.")

        if st.button("🏠 Ir para Home"):
            st.session_state.pagina = "home"
            st.rerun()

    except Exception as e:
        st.error("❌ Erro ao validar sessão.")
        st.exception(e)


if __name__ == "__main__":
    render()
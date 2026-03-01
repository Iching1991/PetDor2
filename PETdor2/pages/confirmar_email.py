import streamlit as st
import streamlit.components.v1 as components
from backend.database.supabase_client import supabase


def capturar_hash():

    components.html(
        """
        <script>
        const hash = window.location.hash.substring(1);
        const params = new URLSearchParams(hash);

        const access_token = params.get("access_token");
        const refresh_token = params.get("refresh_token");

        if (access_token && refresh_token) {
            window.parent.postMessage({
                access_token: access_token,
                refresh_token: refresh_token
            }, "*");
        }
        </script>
        """,
        height=0,
    )


def render():

    st.title("📧 Confirmação de E-mail")

    capturar_hash()

    if "access_token" not in st.session_state:
        st.info("Validando confirmação...")
        return

    try:
        supabase.auth.set_session(
            st.session_state["access_token"],
            st.session_state["refresh_token"],
        )

        st.success("🎉 E-mail confirmado com sucesso!")

    except Exception:
        st.error("❌ Link inválido ou expirado.")
        return

    if st.button("🔐 Ir para Login"):
        st.session_state.pagina = "login"
        st.rerun()


render()
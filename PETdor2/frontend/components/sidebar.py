import streamlit as st


# ==========================================================
# CONFIG
# ==========================================================
PAGINAS = {

    "🏠 Home": "home",

    "📊 Avaliação": "avaliacao",
    "📜 Histórico": "historico",

    "👤 Conta": {
        "Minha conta": "conta",
        "Confirmar e-mail": "confirmar_email",
    },

    "🐶 Pets": {
        "Cadastro pet": "cadastro_pet",
    },

    "🔐 Acesso": {
        "Login": "login",
        "Cadastro": "cadastro",
        "Recuperar senha": "recuperar_senha",
    },

    "⚙️ Admin": "admin",

    "ℹ️ Sobre": "sobre",
}


# ==========================================================
# RENDER
# ==========================================================
def render_sidebar():

    with st.sidebar:

        # -------------------------
        # Branding
        # -------------------------
        st.markdown(
            """
            <h2 style='margin-bottom:0;'>🐾 PETDor</h2>
            <small>Sistema de Avaliação de Dor Animal</small>
            """,
            unsafe_allow_html=True
        )

        st.divider()

        pagina_atual = st.session_state.get("pagina", "home")

        # -------------------------
        # Loop páginas
        # -------------------------
        for titulo, valor in PAGINAS.items():

            # -------------------------
            # Grupo
            # -------------------------
            if isinstance(valor, dict):

                st.markdown(f"**{titulo}**")

                for sub_titulo, sub_valor in valor.items():

                    if st.button(
                        sub_titulo,
                        use_container_width=True,
                        type="primary"
                        if pagina_atual == sub_valor
                        else "secondary"
                    ):
                        st.session_state.pagina = sub_valor
                        st.rerun()

            # -------------------------
            # Página simples
            # -------------------------
            else:

                if st.button(
                    titulo,
                    use_container_width=True,
                    type="primary"
                    if pagina_atual == valor
                    else "secondary"
                ):
                    st.session_state.pagina = valor
                    st.rerun()

        st.divider()

        # -------------------------
        # Rodapé
        # -------------------------
        st.caption("© 2026 PETDor")

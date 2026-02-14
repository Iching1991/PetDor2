import streamlit as st


def render():

    st.title("📧 Confirmação de E-mail")

    st.success(
        "Seu e-mail foi confirmado com sucesso! 🎉"
    )

    st.info(
        "Agora você já pode fazer login no sistema."
    )

    if st.button("Ir para Login"):
        st.session_state.pagina = "login"
        st.rerun()


# ⚠️ EXECUÇÃO DIRETA
render()


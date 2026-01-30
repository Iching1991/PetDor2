import streamlit as st

def render():
    st.success("✅ E-mail confirmado com sucesso!")
    st.info("Agora você pode fazer login no PETDor.")

    if st.button("🔐 Ir para Login"):
        st.session_state.pagina = "login"
        st.rerun()

render()

import streamlit as st
from auth.email_confirmation import confirmar_email

st.set_page_config(page_title="Confirmar E-mail - PETDor")

def main():
    st.title("📨 Confirmar E-mail")

    token = st.query_params.get("token", None)

    if not token:
        st.error("Token não fornecido.")
        return

    with st.spinner("Validando token..."):
        sucesso, msg = confirmar_email(token)

    if sucesso:
        st.success(msg)
        st.info("Agora você já pode fazer login.")
        st.page_link("pages/login.py", label="Ir para Login")
    else:
        st.error(msg)

main()

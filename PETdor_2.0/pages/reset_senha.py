import streamlit as st
from auth.password_reset import validar_token_reset, redefinir_senha

st.set_page_config(page_title="Redefinir Senha - PETDor")

def main():
    st.title("🔑 Redefinir Senha")

    token = st.query_params.get("token", None)

    if not token:
        st.error("Token ausente.")
        return

    valido, usuario_id = validar_token_reset(token)

    if not valido:
        st.error("Token inválido ou expirado.")
        return

    st.success("Token validado! Defina sua nova senha:")

    nova_senha = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    if st.button("Alterar senha"):
        if nova_senha != confirmar:
            st.error("As senhas não coincidem.")
            return

        ok = redefinir_senha(usuario_id, nova_senha, token)

        if ok:
            st.success("Senha redefinida com sucesso!")
            st.page_link("pages/login.py", label="Ir para Login")
        else:
            st.error("Erro ao redefinir senha.")

main()

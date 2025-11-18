# PetDor/pages/conta.py
import streamlit as st
from auth.user import buscar_usuario_por_id, atualizar_usuario, alterar_senha, deletar_usuario

def app():
    st.header("👤 Minha Conta")
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Faça login para acessar sua conta.")
        return

    user = buscar_usuario_por_id(user_id)
    if not user:
        st.error("Usuário não encontrado.")
        return

    st.subheader("Dados Pessoais")
    nome = st.text_input("Nome", value=user["nome"])
    email = st.text_input("E-mail", value=user["email"])

    if st.button("Salvar alterações"):
        ok = atualizar_usuario(user_id, nome=nome, email=email)
        if ok:
            st.success("Dados atualizados.")
        else:
            st.error("Erro ao atualizar.")

    st.markdown("---")
    st.subheader("Alterar senha")
    nova = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar nova senha", type="password")
    if st.button("Alterar senha"):
        if nova != confirmar:
            st.error("As senhas não conferem.")
        else:
            ok, msg = alterar_senha(user_id, nova)
            if ok:
                st.success("Senha alterada.")
            else:
                st.error(msg)

    st.markdown("---")
    st.subheader("Desativar conta")
    if st.button("Desativar minha conta"):
        if deletar_usuario(user_id):
            st.success("Conta desativada. Você será desconectado.")
            del st.session_state["user_id"]
            st.experimental_rerun()
        else:
            st.error("Erro ao desativar conta.")

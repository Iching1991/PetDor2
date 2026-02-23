import streamlit as st
import re

from backend.auth.password_reset import redefinir_senha


# ==========================================================
# 🔎 Validador de senha
# ==========================================================
def validar_senha(senha: str):

    regras = {
        "8+ caracteres": len(senha) >= 8,
        "Letra maiúscula": bool(re.search(r"[A-Z]", senha)),
        "Letra minúscula": bool(re.search(r"[a-z]", senha)),
        "Número": bool(re.search(r"[0-9]", senha)),
        "Caractere especial": bool(re.search(r"[^A-Za-z0-9]", senha)),
    }

    return regras


# ==========================================================
# 🎨 Render
# ==========================================================
def render():

    st.title("🔐 Redefinir Senha")

    # ----------------------------
    # Capturar parâmetros URL
    # ----------------------------
    params = st.experimental_get_query_params()

    access_token = params.get("access_token", [None])[0]
    type_token = params.get("type", [None])[0]

    if not access_token or type_token != "recovery":
        st.error("Sessão inválida. Solicite um novo link.")
        return

    # ----------------------------
    # Inputs
    # ----------------------------
    nova = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    # ----------------------------
    # Validação dinâmica
    # ----------------------------
    if nova:

        regras = validar_senha(nova)

        st.markdown("### 🛡️ Requisitos da senha")

        for regra, ok in regras.items():

            if ok:
                st.markdown(f"✅ {regra}")
            else:
                st.markdown(f"❌ {regra}")

    # ----------------------------
    # Confirmação
    # ----------------------------
    if confirmar:

        if nova == confirmar:
            st.markdown("✅ Senhas coincidem")
        else:
            st.markdown("❌ Senhas não coincidem")

    # ----------------------------
    # Botão
    # ----------------------------
    if st.button("Alterar senha"):

        if not nova or not confirmar:
            st.warning("Preencha os campos.")
            return

        regras = validar_senha(nova)

        if not all(regras.values()):
            st.error(
                "A senha não atende todos os requisitos."
            )
            return

        if nova != confirmar:
            st.error("Senhas não coincidem.")
            return

        sucesso, msg = redefinir_senha(nova)

        if sucesso:
            st.success("Senha redefinida com sucesso!")
        else:
            st.error(msg)


# ==========================================================
render()

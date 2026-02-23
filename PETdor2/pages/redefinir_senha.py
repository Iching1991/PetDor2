#PetDor/PETdor2/pages/redefinir_senha.py

import streamlit as st
import re

from backend.auth.password_reset import redefinir_senha
from backend.utils.password_strength import (
    calcular_forca_senha,
    classificar_forca
)


def validar_regras(senha: str):

    return {
        "8+ caracteres": len(senha) >= 8,
        "Maiúscula": bool(re.search(r"[A-Z]", senha)),
        "Minúscula": bool(re.search(r"[a-z]", senha)),
        "Número": bool(re.search(r"[0-9]", senha)),
        "Especial": bool(re.search(r"[^A-Za-z0-9]", senha)),
    }


def render():

    st.title("🔐 Redefinir Senha")

    params = st.experimental_get_query_params()

    access_token = params.get("access_token", [None])[0]
    type_token = params.get("type", [None])[0]

    if not access_token or type_token != "recovery":
        st.error("Sessão inválida. Solicite novo link.")
        return

    nova = st.text_input("Nova senha", type="password")
    confirmar = st.text_input("Confirmar senha", type="password")

    # ----------------------------
    # Barra de força
    # ----------------------------
    if nova:

        score = calcular_forca_senha(nova)
        label, color = classificar_forca(score)

        st.progress(score / 100)
        st.markdown(
            f"**Força:** :{color}[{label}] ({score}%)"
        )

        st.markdown("### Requisitos")

        for regra, ok in validar_regras(nova).items():

            st.markdown(
                f"{'✅' if ok else '❌'} {regra}"
            )

    # ----------------------------
    # Botão
    # ----------------------------
    if st.button("Alterar senha"):

        if nova != confirmar:
            st.error("Senhas não coincidem.")
            return

        sucesso, msg = redefinir_senha(nova)

        if sucesso:
            st.success("Senha redefinida!")
        else:
            st.error(msg)


render()

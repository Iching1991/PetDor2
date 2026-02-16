"""
Página de cadastro de usuários - PETDor2
Cadastro com checklist de senha em tempo real
"""

import re
import streamlit as st
from backend.auth.user import cadastrar_usuario
from backend.utils.validators import validar_email


# ============================================================
# 🔐 VALIDADORES DE SENHA
# ============================================================

def validar_senha_requisitos(senha: str):
    requisitos = {
        "8+ caracteres": len(senha) >= 8,
        "Letra maiúscula": bool(re.search(r"[A-Z]", senha)),
        "Letra minúscula": bool(re.search(r"[a-z]", senha)),
        "Número": bool(re.search(r"\d", senha)),
        "Caractere especial": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha)),
    }
    return requisitos


def forca_senha_score(reqs: dict):
    return sum(reqs.values())


# ============================================================
# 🎨 CHECKLIST VISUAL
# ============================================================

def render_checklist(reqs):
    st.markdown("**Requisitos da senha:**")

    for item, ok in reqs.items():
        if ok:
            st.markdown(f"✅ {item}")
        else:
            st.markdown(f"❌ {item}")


def render_forca(score):
    if score <= 2:
        st.error("Senha fraca")
    elif score == 3:
        st.warning("Senha média")
    elif score == 4:
        st.info("Senha boa")
    else:
        st.success("Senha forte")


# ============================================================
# 📝 PÁGINA
# ============================================================

def render():
    st.title("📝 Criar Conta")

    nome = st.text_input("Nome completo")
    email = st.text_input("E-mail").strip().lower()

    # -----------------------------
    # Senha
    # -----------------------------
    senha = st.text_input("Senha", type="password")

    if senha:
        reqs = validar_senha_requisitos(senha)
        score = forca_senha_score(reqs)

        render_checklist(reqs)
        render_forca(score)
    else:
        reqs = validar_senha_requisitos("")

    # -----------------------------
    # Confirmar senha
    # -----------------------------
    confirmar = st.text_input("Confirmar senha", type="password")

    if confirmar:
        if senha == confirmar:
            st.success("✅ Senhas coincidem")
        else:
            st.error("❌ Senhas não coincidem")

    # -----------------------------
    # Outros campos
    # -----------------------------
    pais = st.selectbox(
        "País",
        ["Brasil", "Portugal", "EUA", "Outro"]
    )

    tipo = st.selectbox(
        "Tipo de conta",
        ["Tutor", "Veterinário", "Clínica"]
    )

    # ============================================================
    # 🚀 BOTÃO
    # ============================================================

    senha_valida = all(reqs.values())
    senhas_iguais = senha == confirmar and senha != ""

    botao_disabled = not (
        nome and
        email and
        senha_valida and
        senhas_iguais and
        validar_email(email)
    )

    if st.button("Criar Conta", disabled=botao_disabled):

        # -----------------------------
        # Cadastro
        # -----------------------------
        sucesso, mensagem = cadastrar_usuario(
            nome=nome,
            email=email,
            senha=senha,
            tipo=tipo,
            pais=pais,
        )

        if sucesso:
            st.success("✅ Conta criada com sucesso!")
            st.info("📧 Verifique seu e-mail para confirmar a conta.")
            st.session_state.pagina = "login"
            st.rerun()
        else:
            st.error(mensagem)


# ============================================================
# 🚀 EXECUÇÃO
# ============================================================

try:
    render()
except Exception as e:
    st.error("❌ Erro ao carregar a página de cadastro.")
    st.exception(e)


__all__ = ["render"]
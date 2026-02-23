#PetDor2/PETdor2/pages/cadastro.py

"""
Página de cadastro de usuários - PETDor2
Cadastro com checklist + barra de força
"""

import re
import streamlit as st

from backend.auth.user import cadastrar_usuario
from backend.utils.validators import validar_email
from backend.utils.password_strength import (
    calcular_forca_senha,
    classificar_forca,
)

# ============================================================
# 🔐 VALIDADORES DE REQUISITOS
# ============================================================

def validar_senha_requisitos(senha: str):

    return {
        "8+ caracteres": len(senha) >= 8,
        "Letra maiúscula": bool(re.search(r"[A-Z]", senha)),
        "Letra minúscula": bool(re.search(r"[a-z]", senha)),
        "Número": bool(re.search(r"\d", senha)),
        "Caractere especial": bool(
            re.search(r"[^A-Za-z0-9]", senha)
        ),
    }


# ============================================================
# 🎨 CHECKLIST VISUAL
# ============================================================

def render_checklist(reqs: dict):

    st.markdown("### 🔎 Requisitos da senha")

    for item, ok in reqs.items():

        if ok:
            st.markdown(f"✅ {item}")
        else:
            st.markdown(f"❌ {item}")


# ============================================================
# 📊 BARRA DE FORÇA
# ============================================================

def render_barra_forca(senha: str):

    score = calcular_forca_senha(senha)
    label, color = classificar_forca(score)

    st.progress(score / 100)

    st.markdown(
        f"**Força da senha:** :{color}[{label}] ({score}%)"
    )

    return score


# ============================================================
# 📝 PÁGINA
# ============================================================

def render():

    st.title("📝 Criar Conta")

    # ------------------------------------------------
    # Dados básicos
    # ------------------------------------------------
    nome = st.text_input("Nome completo")

    email = (
        st.text_input("E-mail")
        .strip()
        .lower()
    )

    if email and not validar_email(email):
        st.error("E-mail inválido.")

    # ------------------------------------------------
    # Senha
    # ------------------------------------------------
    senha = st.text_input(
        "Senha",
        type="password",
        help="Use letras, números e símbolos."
    )

    if senha:

        # Checklist
        reqs = validar_senha_requisitos(senha)
        render_checklist(reqs)

        # Barra
        score = render_barra_forca(senha)

    else:
        reqs = validar_senha_requisitos("")
        score = 0

    # ------------------------------------------------
    # Confirmar senha
    # ------------------------------------------------
    confirmar = st.text_input(
        "Confirmar senha",
        type="password"
    )

    if confirmar:

        if senha == confirmar:
            st.success("✅ Senhas coincidem")
        else:
            st.error("❌ Senhas não coincidem")

    # ------------------------------------------------
    # Outros campos
    # ------------------------------------------------
    pais = st.selectbox(
        "País",
        ["Brasil", "Portugal", "EUA", "Outro"]
    )

    tipo = st.selectbox(
        "Tipo de conta",
        ["Tutor", "Veterinário", "Clínica"]
    )

    # ============================================================
    # 🚀 VALIDAÇÕES FINAIS
    # ============================================================

    senha_valida = all(reqs.values())
    senhas_iguais = senha == confirmar and senha != ""
    email_valido = validar_email(email)

    forca_minima = score >= 60   # bloqueia fracas

    botao_disabled = not (
        nome
        and email
        and senha_valida
        and senhas_iguais
        and email_valido
        and forca_minima
    )

    # ============================================================
    # 🚀 BOTÃO CADASTRO
    # ============================================================

    if st.button(
        "Criar Conta",
        disabled=botao_disabled,
        use_container_width=True,
    ):

        sucesso, mensagem = cadastrar_usuario(
            nome=nome,
            email=email,
            senha=senha,
            tipo=tipo,
            pais=pais,
        )

        if sucesso:

            st.success("✅ Conta criada com sucesso!")
            st.info(
                "📧 Verifique seu e-mail para confirmar o cadastro."
            )

            st.session_state.pagina = "login"
            st.rerun()

        else:
            st.error(mensagem)


# ============================================================
# 🚀 EXECUÇÃO SEGURA
# ============================================================

try:
    render()

except Exception as e:

    st.error(
        "❌ Erro ao carregar a página de cadastro."
    )
    st.exception(e)


__all__ = ["render"]

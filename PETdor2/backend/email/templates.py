import streamlit as st


def template_confirmacao_email(nome: str, token: str) -> str:
    url = (
        f"{st.secrets['email']['FRONTEND_URL']}"
        f"?pagina=confirmar_email&token={token}"
    )

    return f"""
    <h2>Bem-vindo ao PETDor 🐾</h2>
    <p>Olá <b>{nome}</b>,</p>
    <p>Confirme seu e-mail clicando no botão abaixo:</p>
    <p>
        <a href="{url}" style="
            padding:12px 20px;
            background:#4CAF50;
            color:#ffffff;
            text-decoration:none;
            border-radius:6px;">
            Confirmar e-mail
        </a>
    </p>
    <p>Se você não criou esta conta, ignore este e-mail.</p>
    """


def template_reset_senha(nome: str, token: str) -> str:
    url = (
        f"{st.secrets['email']['FRONTEND_URL']}"
        f"?pagina=redefinir_senha&token={token}"
    )

    return f"""
    <h2>Redefinição de senha 🔐</h2>
    <p>Olá <b>{nome}</b>,</p>
    <p>Você solicitou a redefinição de senha.</p>
    <p>
        <a href="{url}" style="
            padding:12px 20px;
            background:#FF9800;
            color:#ffffff;
            text-decoration:none;
            border-radius:6px;">
            Criar nova senha
        </a>
    </p>
    <p>Se não foi você, ignore este e-mail.</p>
    """

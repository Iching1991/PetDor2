from streamlit import secrets


def email_confirmacao(nome: str, token: str) -> str:
    url = f"{secrets['email']['FRONTEND_URL']}?pagina=confirmar_email&token={token}"

    return f"""
    <h2>Bem-vindo ao PETDor 🐾</h2>
    <p>Olá <b>{nome}</b>,</p>
    <p>Confirme seu e-mail clicando no botão abaixo:</p>
    <p>
        <a href="{url}" style="padding:10px 20px;background:#4CAF50;color:#fff;text-decoration:none;">
            Confirmar e-mail
        </a>
    </p>
    <p>Se você não criou esta conta, ignore este e-mail.</p>
    """

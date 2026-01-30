import requests
import streamlit as st

RESEND_API_URL = "https://api.resend.com/emails"


def enviar_email(destinatario: str, assunto: str, html: str) -> bool:
    try:
        api_key = st.secrets["email"]["RESEND_API_KEY"]
        email_from = st.secrets["email"]["EMAIL_FROM"]

        payload = {
            "from": email_from,
            "to": [destinatario],
            "subject": assunto,
            "html": html,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            RESEND_API_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )

        r.raise_for_status()
        return True

    except Exception as e:
        print("❌ Erro ao enviar e-mail:", e)
        return False


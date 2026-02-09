import base64
import requests
import streamlit as st


def enviar_pdf_email(
    destinatario: str,
    assunto: str,
    corpo: str,
    pdf_bytes: bytes,
    nome_arquivo: str,
) -> bool:

    api_key = st.secrets["email"]["RESEND_API_KEY"]
    email_from = st.secrets["email"]["EMAIL_FROM"]

    pdf_base64 = base64.b64encode(pdf_bytes).decode()

    payload = {
        "from": email_from,
        "to": [destinatario],
        "subject": assunto,
        "html": corpo,
        "attachments": [
            {
                "filename": nome_arquivo,
                "content": pdf_base64,
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    r = requests.post(
        "https://api.resend.com/emails",
        json=payload,
        headers=headers,
    )

    return r.status_code in (200, 201)

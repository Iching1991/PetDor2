from supabase import create_client
import streamlit as st
from typing import Tuple

supabase = create_client(
    st.secrets["supabase"]["SUPABASE_URL"],
    st.secrets["supabase"]["SUPABASE_KEY"]
)

def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    try:
        supabase.auth.reset_password_for_email(
            email,
            {"redirect_to": "https://petdor.streamlit.app/resetar_senha"}
        )
        return True, "Se o e-mail existir, o link foi enviado."
    except Exception as e:
        return False, str(e)

import uuid
from typing import Tuple

from backend.database import supabase_table_select, supabase_table_update
from backend.email.service import enviar_email
from backend.email.templates import template_reset_senha
from backend.auth.user import hash_senha


def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    email = email.lower().strip()

    usuario = supabase_table_select(
        table="usuarios",
        filters={"email": email},
        limit=1,
    )

    if not usuario:
        return True, "Se o e-mail existir, enviaremos um link."

    usuario = usuario[0]
    token = str(uuid.uuid4())

    supabase_table_update(
        table="usuarios",
        filters={"id": usuario["id"]},
        data={"password_reset_token": token},
    )

    enviar_email(
        destinatario=email,
        assunto="Redefinição de senha – PETDor",
        html=template_reset_senha(usuario["nome"], token),
    )

    return True, "Se o e-mail existir, enviaremos um link."


def redefinir_senha(token: str, nova_senha: str) -> Tuple[bool, str]:
    usuario = supabase_table_select(
        table="usuarios",
        filters={"password_reset_token": token},
        limit=1,
    )

    if not usuario:
        return False, "Token inválido ou expirado."

    usuario = usuario[0]

    supabase_table_update(
        table="usuarios",
        filters={"id": usuario["id"]},
        data={
            "senha_hash": hash_senha(nova_senha),
            "password_reset_token": None,
        },
    )

    return True, "Senha alterada com sucesso."

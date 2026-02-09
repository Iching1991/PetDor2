from typing import Tuple
from backend.database import supabase_table_select, supabase_table_update


def validar_token_confirmacao(token: str) -> Tuple[bool, str | None]:
    resultado = supabase_table_select(
        table="usuarios",
        filters={"email_confirm_token": token},
        limit=1,
    )

    if not resultado:
        return False, None

    return True, resultado[0]["id"]


def confirmar_email(usuario_id: str) -> Tuple[bool, str]:
    atualizado = supabase_table_update(
        table="usuarios",
        filters={"id": usuario_id},
        data={
            "email_confirmado": True,
            "email_confirm_token": None,
        },
    )

    if atualizado is None:
        return False, "Erro ao confirmar e-mail."

    return True, "E-mail confirmado com sucesso."

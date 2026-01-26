# backend/database/__init__.py

from .user import (
    cadastrar_usuario,
    buscar_usuario_por_email,
    verificar_credenciais,
    atualizar_usuario,
    atualizar_status_usuario,
    redefinir_senha,
    marcar_email_como_confirmado,
    deletar_usuario,
)

__all__ = [
    "cadastrar_usuario",
    "buscar_usuario_por_email",
    "verificar_credenciais",
    "atualizar_usuario",
    "atualizar_status_usuario",
    "redefinir_senha",
    "marcar_email_como_confirmado",
    "deletar_usuario",
]

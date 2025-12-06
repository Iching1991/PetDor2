# PetDor2/backend/auth/__init__.py
"""
Pacote de autenticação e gerenciamento de usuários do PETDor2.
"""

from .user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    atualizar_usuario,
    atualizar_tipo_usuario,
    atualizar_status_usuario,
    alterar_senha,
    deletar_usuario,
    marcar_email_como_confirmado,
)

from .password_reset import solicitar_reset_senha, redefinir_senha_com_token
from .email_confirmation import enviar_email_confirmacao, confirmar_email_com_token
from .security import (
    hash_password,
    verify_password,
    gerar_token_jwt,
    validar_token_jwt,
    gerar_token_reset_senha,
    validar_token_reset_senha,
    gerar_token_confirmacao_email,
    validar_token_confirmacao_email,
    usuario_logado,
    logout,
)

__all__ = [
    "cadastrar_usuario",
    "verificar_credenciais",
    "buscar_usuario_por_id",
    "buscar_usuario_por_email",
    "atualizar_usuario",
    "atualizar_tipo_usuario",
    "atualizar_status_usuario",
    "alterar_senha",
    "deletar_usuario",
    "marcar_email_como_confirmado",
    "solicitar_reset_senha",
    "redefinir_senha_com_token",
    "enviar_email_confirmacao",
    "confirmar_email_com_token",
    "hash_password",
    "verify_password",
    "gerar_token_jwt",
    "validar_token_jwt",
    "gerar_token_reset_senha",
    "validar_token_reset_senha",
    "gerar_token_confirmacao_email",
    "validar_token_confirmacao_email",
    "usuario_logado",
    "logout",
]

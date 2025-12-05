# PetDor2/backend/auth/__init__.py
"""
Módulo de autenticação e gerenciamento de usuários do PETDor.
Expõe funções principais de criação, validação, segurança e recuperação de acesso.
"""

# -----------------------------
# Importações de user.py
# -----------------------------
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

# -----------------------------
# Importações de password_reset.py
# -----------------------------
from .password_reset import (
    solicitar_reset_senha,
    redefinir_senha_com_token,
)

# -----------------------------
# Importações de email_confirmation.py
# -----------------------------
from .email_confirmation import (
    enviar_email_confirmacao,
    confirmar_email_com_token,
)

# -----------------------------
# Importações de security.py
# -----------------------------
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

# -----------------------------
# Exportação pública do pacote
# -----------------------------
__all__ = [
    # user.py
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

    # password_reset.py
    "solicitar_reset_senha",
    "redefinir_senha_com_token",

    # email_confirmation.py
    "enviar_email_confirmacao",
    "confirmar_email_com_token",

    # security.py
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

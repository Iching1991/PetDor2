# backend/auth/user.py

from typing import Dict, Any, Optional
from backend.database import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

# ----------------------------------------------
# Criar usuário
# ----------------------------------------------
def criar_usuario(dados: Dict[str, Any]) -> Optional[Dict]:
    return supabase_table_insert("usuarios", dados)

# ----------------------------------------------
# Buscar usuário por e-mail
# ----------------------------------------------
def buscar_usuario_por_email(email: str) -> Optional[Dict]:
    result = supabase_table_select(
        table="usuarios",
        filters={"email": email},
        limit=1
    )
    return result[0] if result else None

# ----------------------------------------------
# Autenticação
# ----------------------------------------------
def autenticar_usuario(email: str, senha_hash: str):
    user = buscar_usuario_por_email(email)

    if not user:
        return False, "Usuário não encontrado."

    if user.get("senha_hash") != senha_hash:
        return False, "Senha incorreta."

    return True, user

# ----------------------------------------------
# Atualizar usuário
# ----------------------------------------------
def atualizar_usuario(user_id: str, dados: Dict[str, Any]):
    return supabase_table_update(
        table="usuarios",
        filters={"id": user_id},
        data=dados
    )

# ----------------------------------------------
# Deletar usuário
# ----------------------------------------------
def deletar_usuario(user_id: str) -> bool:
    return supabase_table_delete(
        table="usuarios",
        filters={"id": user_id}
    )

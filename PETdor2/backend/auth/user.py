"""
Módulo central de usuários do PETDor2
Compatível com Supabase REST + RLS
"""

import hashlib
from typing import Dict, Any, Tuple, Optional

from backend.database import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

# ==========================================================
# Utils
# ==========================================================

def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

# ==========================================================
# Criar usuário (Cadastro)
# ==========================================================

def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str,
    pais: str
) -> Tuple[bool, str]:
    try:
        email = email.lower().strip()

        existente = supabase_table_select(
            table="usuarios",
            filters={"email": email},
            limit=1
        )
        if existente:
            return False, "Este e-mail já está cadastrado."

        supabase_table_insert(
            table="usuarios",
            data={
                "nome": nome.strip(),
                "email": email,
                "senha_hash": hash_senha(senha),
                "tipo_usuario": tipo.lower(),
                "pais": pais,
                "email_confirmado": False,
                "ativo": True,
                "is_admin": False,
            }
        )

        return True, "Conta criada com sucesso."

    except Exception as e:
        return False, f"Erro ao criar usuário: {e}"

# ==========================================================
# Buscar usuário
# ==========================================================

def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    resultado = supabase_table_select(
        table="usuarios",
        filters={"email": email.lower()},
        limit=1
    )
    return resultado[0] if resultado else None

# ==========================================================
# Login
# ==========================================================

def verificar_credenciais(email: str, senha: str) -> Tuple[bool, Any]:
    usuario = buscar_usuario_por_email(email)

    if not usuario:
        return False, "Usuário não encontrado."

    if not usuario.get("ativo", True):
        return False, "Usuário desativado."

    if usuario.get("senha_hash") != hash_senha(senha):
        return False, "Senha incorreta."

    return True, usuario

# ==========================================================
# Atualizar dados
# ==========================================================

def atualizar_usuario(user_id: str, dados: Dict[str, Any]) -> Tuple[bool, str]:
    atualizado = supabase_table_update(
        table="usuarios",
        filters={"id": user_id},
        data=dados
    )

    if atualizado is None:
        return False, "Erro ao atualizar usuário."

    return True, "Usuário atualizado com sucesso."

# ==========================================================
# Status
# ==========================================================

def atualizar_status_usuario(user_id: str, ativo: bool) -> Tuple[bool, str]:
    return atualizar_usuario(user_id, {"ativo": ativo})

# ==========================================================
# Redefinir senha
# ==========================================================

def redefinir_senha(user_id: str, senha_atual: str, nova_senha: str) -> Tuple[bool, str]:
    usuario = supabase_table_select(
        table="usuarios",
        filters={"id": user_id},
        limit=1
    )

    if not usuario:
        return False, "Usuário não encontrado."

    usuario = usuario[0]

    if usuario.get("senha_hash") != hash_senha(senha_atual):
        return False, "Senha atual incorreta."

    supabase_table_update(
        table="usuarios",
        filters={"id": user_id},
        data={"senha_hash": hash_senha(nova_senha)}
    )

    return True, "Senha alterada com sucesso."

# ==========================================================
# Confirmar e-mail
# ==========================================================

def marcar_email_como_confirmado(email: str) -> Tuple[bool, str]:
    atualizado = supabase_table_update(
        table="usuarios",
        filters={"email": email.lower()},
        data={
            "email_confirmado": True,
            "email_confirm_token": None,
        }
    )

    if atualizado is None:
        return False, "Erro ao confirmar e-mail."

    return True, "E-mail confirmado com sucesso."

# ==========================================================
# Deletar
# ==========================================================

def deletar_usuario(user_id: str) -> bool:
    return supabase_table_delete(
        table="usuarios",
        filters={"id": user_id}
    )

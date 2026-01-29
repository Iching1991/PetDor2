"""
Módulo central de usuários do PETDor2
Cadastro, login e gerenciamento de usuários
Compatível com Supabase REST + RLS (service_role)
"""

import hashlib
import logging
from typing import Dict, Any, Tuple, Optional

from backend.database.supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

logger = logging.getLogger(__name__)

# ==========================================================
# Utils
# ==========================================================

def hash_senha(senha: str) -> str:
    """Gera hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

# ==========================================================
# Cadastro de usuário
# ==========================================================

def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str,
    pais: str,
) -> Tuple[bool, str]:
    try:
        email = email.strip().lower()

        # Verifica se já existe
        existente = supabase_table_select(
            table="usuarios",
            filters={"email": email},
            limit=1,
        )

        if existente:
            return False, "Este e-mail já está cadastrado."

        payload = {
            "nome": nome.strip(),
            "email": email,
            "senha_hash": hash_senha(senha),
            "tipo_usuario": tipo.lower(),
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": False,
        }

        inserido = supabase_table_insert(
            table="usuarios",
            data=payload,
        )

        if not inserido:
            logger.error("Falha ao inserir usuário no Supabase", extra={"payload": payload})
            return False, "Erro ao criar conta. Tente novamente."

        return True, "Conta criada com sucesso."

    except Exception as e:
        logger.exception("Erro inesperado ao cadastrar usuário")
        return False, "Erro interno ao criar conta."

# ==========================================================
# Buscar usuário
# ==========================================================

def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    try:
        resultado = supabase_table_select(
            table="usuarios",
            filters={"email": email.strip().lower()},
            limit=1,
        )
        return resultado[0] if resultado else None
    except Exception:
        logger.exception("Erro ao buscar usuário por email")
        return None

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
# Atualização de dados
# ==========================================================

def atualizar_usuario(user_id: str, dados: Dict[str, Any]) -> Tuple[bool, str]:
    try:
        atualizado = supabase_table_update(
            table="usuarios",
            filters={"id": user_id},
            data=dados,
        )

        if atualizado is None:
            return False, "Erro ao atualizar usuário."

        return True, "Usuário atualizado com sucesso."

    except Exception:
        logger.exception("Erro ao atualizar usuário")
        return False, "Erro interno ao atualizar usuário."

# ==========================================================
# Ativar / desativar
# ==========================================================

def atualizar_status_usuario(user_id: str, ativo: bool) -> Tuple[bool, str]:
    return atualizar_usuario(user_id, {"ativo": ativo})

# ==========================================================
# Redefinir senha (logado)
# ==========================================================

def redefinir_senha(
    user_id: str,
    senha_atual: str,
    nova_senha: str,
) -> Tuple[bool, str]:
    try:
        usuario = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        if not usuario:
            return False, "Usuário não encontrado."

        usuario = usuario[0]

        if usuario.get("senha_hash") != hash_senha(senha_atual):
            return False, "Senha atual incorreta."

        supabase_table_update(
            table="usuarios",
            filters={"id": user_id},
            data={"senha_hash": hash_senha(nova_senha)},
        )

        return True, "Senha alterada com sucesso."

    except Exception:
        logger.exception("Erro ao redefinir senha")
        return False, "Erro interno ao redefinir senha."

# ==========================================================
# Confirmar e-mail
# ==========================================================

def marcar_email_como_confirmado(email: str) -> Tuple[bool, str]:
    try:
        atualizado = supabase_table_update(
            table="usuarios",
            filters={"email": email.strip().lower()},
            data={
                "email_confirmado": True,
                "email_confirm_token": None,
            },
        )

        if atualizado is None:
            return False, "Erro ao confirmar e-mail."

        return True, "E-mail confirmado com sucesso."

    except Exception:
        logger.exception("Erro ao confirmar e-mail")
        return False, "Erro interno ao confirmar e-mail."

# ==========================================================
# Deletar usuário
# ==========================================================

def deletar_usuario(user_id: str) -> bool:
    try:
        return supabase_table_delete(
            table="usuarios",
            filters={"id": user_id},
        )
    except Exception:
        logger.exception("Erro ao deletar usuário")
        return False

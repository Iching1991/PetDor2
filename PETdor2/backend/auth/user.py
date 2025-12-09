# PetDor2/backend/auth/user.py
"""
Gerenciamento de usuários do PETDor.
Inclui cadastro, login, busca, atualização, deleção e validação.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

# ============================================================
# IMPORTS SEGUROS (ABSOLUTOS PARA EVITAR CICLO)
# ============================================================
from backend.database.supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

from backend.utils.validators import validar_email
from .security import hash_password, verify_password

logger = logging.getLogger(__name__)

# Nome da tabela
TABELA_USUARIOS = "usuarios"

# Campos permitidos para atualização
CAMPOS_ATUALIZAVEIS = {
    "nome", "email", "senha_hash", "tipo", "pais",
    "email_confirmado", "ativo", "is_admin",
    "email_confirm_token", "reset_password_token",
    "reset_password_expires_at",
}

# ============================================================
# 🔹 Funções auxiliares internas
# ============================================================

def _normalizar_email(email: str) -> str:
    return email.strip().lower()


def _agora() -> str:
    return datetime.now().isoformat()


# ============================================================
# 🔹 Cadastro
# ============================================================

def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    confirmar_senha: str,
    tipo_usuario: str = "Tutor",
    pais: str = "Brasil",
    is_admin: bool = False,
) -> Tuple[bool, str]:
    """
    Cadastra novo usuário no Supabase.
    """
    try:
        # ----------- Validações ----------- #
        if not all([nome, email, senha, confirmar_senha]):
            return False, "Preencha todos os campos obrigatórios."

        if senha != confirmar_senha:
            return False, "As senhas não conferem."

        if len(senha) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres."

        if not validar_email(email):
            return False, "E-mail inválido."

        email = _normalizar_email(email)

        # ----------- Verificar duplicação ----------- #
        ok, existente = supabase_table_select(
            TABELA_USUARIOS,
            "id",
            {"email": email},
            single=False
        )

        if not ok:
            logger.error(f"Erro ao verificar e-mail {email}: {existente}")
            return False, f"Erro ao verificar usuário: {existente}"

        if existente:
            return False, "E-mail já cadastrado."

        # ----------- Inserir ----------- #
        senha_hash = hash_password(senha)
        dados_usuario = {
            "nome": nome.strip(),
            "email": email,
            "senha_hash": senha_hash,
            "tipo": tipo_usuario,
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": is_admin,
            "criado_em": _agora(),
            "atualizado_em": _agora(),
        }

        ok_insert, result = supabase_table_insert(TABELA_USUARIOS, dados_usuario)

        if not ok_insert or not result:
            logger.error(f"Erro ao criar usuário: {result}")
            return False, "Erro ao criar conta."

        user_id = result[0]["id"]

        logger.info(f"Usuário criado: {email} (ID {user_id})")
        return True, "Conta criada com sucesso. Verifique seu e-mail para confirmar."

    except Exception as e:
        logger.exception("Erro inesperado no cadastro de usuário.")
        return False, f"Erro interno ao criar conta: {e}"


# ============================================================
# 🔹 Login / Autenticação
# ============================================================

def verificar_credenciais(email: str, senha: str) -> Tuple[bool, str | Dict[str, Any]]:
    """
    Verifica login do usuário.
    """
    try:
        if not email or not senha:
            return False, "E-mail e senha são obrigatórios."

        email = _normalizar_email(email)

        ok, usuario = supabase_table_select(
            TABELA_USUARIOS,
            "*",
            {"email": email},
            single=True
        )

        if not ok:
            logger.error(f"Erro ao buscar usuário {email}: {usuario}")
            return False, "Erro ao tentar fazer login."

        if not usuario:
            return False, "E-mail ou senha incorretos."

        if not verify_password(senha, usuario.get("senha_hash", "")):
            return False, "E-mail ou senha incorretos."

        if not usuario.get("ativo"):
            return False, "Sua conta está inativa."

        logger.info(f"Login OK: {email}")
        return True, usuario

    except Exception as e:
        logger.exception("Erro ao verificar credenciais.")
        return False, f"Erro interno ao fazer login: {e}"

# ============================================================
# 🔹 Busca de Usuário
# ============================================================

def buscar_usuario_por_email(email: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    try:
        email = _normalizar_email(email)
        return supabase_table_select(TABELA_USUARIOS, "*", {"email": email}, single=True)
    except Exception:
        logger.exception(f"Erro ao buscar usuário {email}.")
        return False, None


def buscar_usuario_por_id(user_id: int) -> Tuple[bool, Optional[Dict[str, Any]]]:
    try:
        return supabase_table_select(TABELA_USUARIOS, "*", {"id": user_id}, single=True)
    except Exception:
        logger.exception(f"Erro ao buscar usuário ID {user_id}.")
        return False, None

# ============================================================
# 🔹 Atualização de Usuário
# ============================================================

def atualizar_usuario(user_id: int, **kwargs: Any) -> Tuple[bool, str]:
    """
    Atualiza dados do usuário.
    """
    try:
        dados_update = {k: v for k, v in kwargs.items() if k in CAMPOS_ATUALIZAVEIS}

        if not dados_update:
            return False, "Nenhum campo válido para atualizar."

        if "email" in dados_update:
            dados_update["email"] = _normalizar_email(dados_update["email"])

        dados_update["atualizado_em"] = _agora()

        ok, res = supabase_table_update(
            TABELA_USUARIOS, dados_update, {"id": user_id}
        )
        if ok:
            logger.info(f"Usuário {user_id} atualizado: {dados_update}")
            return True, "Usuário atualizado com sucesso."
        return False, f"Erro ao atualizar usuário: {res}"

    except Exception as e:
        logger.exception(f"Erro ao atualizar usuário {user_id}.")
        return False, f"Erro interno ao atualizar: {e}"


def alterar_senha(user_id: int, nova_senha: str) -> Tuple[bool, str]:
    try:
        if len(nova_senha) < 8:
            return False, "A senha deve ter pelo menos 8 caracteres."
        return atualizar_usuario(user_id, senha_hash=hash_password(nova_senha))
    except Exception as e:
        logger.exception(f"Erro ao alterar senha do usuário {user_id}.")
        return False, f"Erro interno ao alterar senha: {e}"

# ============================================================
# 🔹 Deletar Usuário
# ============================================================

def deletar_usuario(user_id: int) -> Tuple[bool, str]:
    try:
        ok, res = supabase_table_delete(TABELA_USUARIOS, {"id": user_id})
        if ok:
            logger.info(f"Usuário {user_id} deletado.")
            return True, "Usuário deletado com sucesso."
        return False, f"Erro ao deletar usuário: {res}"
    except Exception as e:
        logger.exception(f"Erro ao deletar usuário {user_id}.")
        return False, f"Erro interno ao deletar: {e}"

# ============================================================
# 🔹 Operações auxiliares
# ============================================================

def atualizar_tipo_usuario(user_id: int, novo_tipo: str) -> Tuple[bool, str]:
    return atualizar_usuario(user_id, tipo=novo_tipo)


def atualizar_status_usuario(user_id: int, novo_status: bool) -> Tuple[bool, str]:
    return atualizar_usuario(user_id, ativo=novo_status)


def marcar_email_como_confirmado(email: str) -> Tuple[bool, str]:
    """
    Marca o e-mail como confirmado após o usuário clicar no link.
    """
    try:
        email = _normalizar_email(email)
        dados = {
            "email_confirmado": True,
            "email_confirm_token": None,
            "atualizado_em": _agora()
        }
        ok, _ = supabase_table_update(TABELA_USUARIOS, dados, {"email": email})
        if ok:
            logger.info(f"E-mail confirmado: {email}")
            return True, "E-mail confirmado com sucesso."
        return False, "Falha ao confirmar e-mail."
    except Exception as e:
        logger.exception("Erro ao confirmar e-mail.")
        return False, f"Erro interno: {e}"

"""
Autenticação e Cadastro de Usuários - PETDor2
Refatorado para constraint tipo_usuario_check

Tipos válidos no banco:
admin | tutor | vet | clinica
"""

from typing import Tuple, Optional, Dict, Any
import streamlit as st
import logging
import re

logger = logging.getLogger(__name__)

# ==========================================================
# 🔁 NORMALIZAÇÃO DE TIPOS
# ==========================================================

TIPO_MAP = {
    "tutor": "tutor",
    "Tutor": "tutor",

    "veterinario": "vet",
    "Veterinario": "vet",
    "veterinário": "vet",
    "Veterinário": "vet",
    "vet": "vet",

    "clinica": "clinica",
    "Clínica": "clinica",
    "clinica veterinaria": "clinica",

    "admin": "admin",
    "Administrador": "admin",
}

TIPOS_VALIDOS = {"admin", "tutor", "vet", "clinica"}


def normalizar_tipo(tipo: str) -> str:
    tipo = tipo.strip()

    if tipo in TIPO_MAP:
        return TIPO_MAP[tipo]

    tipo_lower = tipo.lower()

    if tipo_lower in TIPO_MAP:
        return TIPO_MAP[tipo_lower]

    return tipo_lower


# ==========================================================
# 📝 CADASTRO
# ==========================================================

def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str,
    pais: str,
) -> Tuple[bool, str]:

    from backend.database.supabase_client import supabase
    from backend.database import (
        supabase_table_insert,
        supabase_table_select,
    )

    try:
        # -------------------------
        # Normalização
        # -------------------------
        email = email.lower().strip()
        nome = nome.strip()
        pais = pais.strip()

        tipo_original = tipo
        tipo = normalizar_tipo(tipo)

        # -------------------------
        # Validar tipo
        # -------------------------
        if tipo not in TIPOS_VALIDOS:
            return False, (
                f"Tipo de usuário inválido: {tipo_original}. "
                f"Use: tutor, veterinário ou clínica."
            )

        # -------------------------
        # Validações básicas
        # -------------------------
        if len(nome) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres."

        if len(senha) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres."

        if "@" not in email:
            return False, "E-mail inválido."

        logger.info(f"🔄 Cadastro iniciado: {email}")

        # -------------------------
        # Verificar duplicata
        # -------------------------
        existente = supabase_table_select(
            table="usuarios",
            filters={"email": email},
            limit=1,
        )

        if existente:
            return False, "Este e-mail já está cadastrado."

        # -------------------------
        # Criar no Auth
        # -------------------------
        auth_resp = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {
                "email_redirect_to":
                    st.secrets["app"]["STREAMLIT_APP_URL"]
                    + "/confirmar_email",
                "data": {
                    "nome": nome,
                    "tipo_usuario": tipo,
                }
            }
        })

        if not auth_resp.user:
            return False, "Erro ao criar usuário."

        user_id = auth_resp.user.id

        logger.info(f"✅ Auth criado: {user_id}")

        # -------------------------
        # Criar perfil
        # -------------------------
        perfil = supabase_table_insert(
            table="usuarios",
            data={
                "id": user_id,
                "nome": nome,
                "email": email,
                "tipo_usuario": tipo,
                "pais": pais,
                "ativo": True,
                "is_admin": tipo == "admin",
            },
        )

        if not perfil:
            return False, "Erro ao criar perfil."

        logger.info(f"✅ Perfil criado: {user_id}")

        return True, (
            "Conta criada com sucesso! "
            "Verifique seu e-mail."
        )

    except Exception as e:
        logger.exception("Erro cadastro")

        error_msg = str(e).lower()

        if "23514" in error_msg:
            return False, (
                "Tipo de usuário inválido para o banco."
            )

        if "already registered" in error_msg:
            return False, "E-mail já cadastrado."

        if "weak password" in error_msg:
            return False, "Senha muito fraca."

        return False, "Erro ao criar conta."


# ==========================================================
# 🔐 LOGIN
# ==========================================================

def fazer_login(
    email: str,
    senha: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:

    from backend.database.supabase_client import supabase
    from backend.database import supabase_table_select

    try:
        email = email.lower().strip()

        auth_resp = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha,
        })

        if not auth_resp.user:
            return False, "Credenciais inválidas.", None

        user_id = auth_resp.user.id

        usuario = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        if not usuario:
            return False, "Perfil não encontrado.", None

        return True, "Login realizado!", usuario[0]

    except Exception as e:
        logger.exception("Erro login")

        if "email not confirmed" in str(e).lower():
            return False, "Confirme seu e-mail.", None

        return False, "Erro no login.", None


# ==========================================================
# 🔄 RESET SENHA
# ==========================================================

def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:

    from backend.database.supabase_client import supabase

    try:
        if len(nova_senha) < 6:
            return False, "Mínimo 6 caracteres."

        supabase.auth.update_user({
            "password": nova_senha
        })

        return True, "Senha redefinida com sucesso."

    except Exception:
        return False, "Erro ao redefinir senha."


# ==========================================================
# 👤 USUÁRIO ATUAL
# ==========================================================

def obter_usuario_atual() -> Optional[Dict[str, Any]]:

    from backend.database.supabase_client import supabase
    from backend.database import supabase_table_select

    try:
        session = supabase.auth.get_session()

        if not session or not session.user:
            return None

        user_id = session.user.id

        usuario = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        return usuario[0] if usuario else None

    except Exception:
        return None


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "cadastrar_usuario",
    "fazer_login",
    "redefinir_senha",
    "obter_usuario_atual",
]

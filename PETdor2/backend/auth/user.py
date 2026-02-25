"""
Autenticação e Cadastro de Usuários - PETDor2
Sistema híbrido: Supabase Auth + tabela usuarios customizada

✔ Corrige erro usuarios_tipo_usuario_check
✔ Normalização segura de tipo_usuario
✔ Tratamento robusto de erros
✔ Lazy imports
✔ Logs detalhados
"""

from typing import Tuple, Optional, Dict, Any
import streamlit as st
import logging
import re

logger = logging.getLogger(__name__)

# ==========================================================
# 🔧 NORMALIZAÇÃO DE TIPO USUÁRIO
# ==========================================================

TIPO_MAP = {
    "Tutor": "tutor",
    "Veterinário": "veterinario",
    "Veterinario": "veterinario",
    "Clínica": "clinica",
    "Clinica": "clinica",
    "Admin": "admin",
}

TIPOS_VALIDOS = {"tutor", "veterinario", "clinica", "admin"}


def normalizar_tipo_usuario(tipo: str) -> str:
    if not tipo:
        return "tutor"

    tipo = tipo.strip()

    # Primeiro tenta mapear pelo nome amigável
    if tipo in TIPO_MAP:
        return TIPO_MAP[tipo]

    # Remove acentos manualmente (fallback simples)
    tipo = (
        tipo.lower()
        .replace("á", "a")
        .replace("ã", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("ú", "u")
        .replace("ç", "c")
    )

    if tipo not in TIPOS_VALIDOS:
        return "tutor"

    return tipo


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
    from backend.database import supabase_table_insert, supabase_table_select

    try:
        email = email.lower().strip()
        nome = nome.strip()
        pais = pais.strip()
        tipo_normalizado = normalizar_tipo_usuario(tipo)

        # -------------------------
        # Validações básicas
        # -------------------------
        if len(nome) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres."

        if len(senha) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres."

        if "@" not in email:
            return False, "E-mail inválido."

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
                    st.secrets["app"]["STREAMLIT_APP_URL"] + "/confirmar_email",
                "data": {
                    "nome": nome,
                    "tipo_usuario": tipo_normalizado,
                }
            }
        })

        if not auth_resp.user:
            return False, "Erro ao criar usuário."

        user_id = auth_resp.user.id

        # -------------------------
        # Criar perfil
        # -------------------------
        perfil = supabase_table_insert(
            table="usuarios",
            data={
                "id": user_id,
                "nome": nome,
                "email": email,
                "tipo_usuario": tipo_normalizado,
                "pais": pais,
                "ativo": True,
                "is_admin": False,
            },
        )

        if not perfil:
            return False, "Erro ao criar perfil."

        return True, (
            "Conta criada com sucesso! "
            "Verifique seu e-mail para confirmar."
        )

    except Exception as e:
        logger.exception("Erro no cadastro")

        error_msg = str(e).lower()

        if "429" in error_msg:
            return False, "Muitas tentativas. Aguarde."

        if "email rate limit exceeded" in error_msg:
            return False, "Limite de envio de e-mails atingido."

        if "23505" in error_msg or "duplicate" in error_msg:
            return False, "Este e-mail já está cadastrado."

        if "usuarios_tipo_usuario_check" in error_msg:
            return False, "Tipo de usuário inválido."

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
            return False, "E-mail ou senha incorretos.", None

        user_id = auth_resp.user.id

        usuario = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        if not usuario:
            return False, "Perfil não encontrado.", None

        if not usuario[0].get("ativo", True):
            return False, "Conta inativa.", None

        return True, "Login realizado com sucesso!", usuario[0]

    except Exception as e:
        logger.exception("Erro no login")

        error_msg = str(e).lower()

        if "email not confirmed" in error_msg:
            return False, "Confirme seu e-mail antes de fazer login.", None

        if "invalid login credentials" in error_msg:
            return False, "E-mail ou senha incorretos.", None

        return False, "Erro ao fazer login.", None


# ==========================================================
# 🚪 LOGOUT
# ==========================================================

def fazer_logout() -> Tuple[bool, str]:
    from backend.database.supabase_client import supabase

    try:
        supabase.auth.sign_out()
        return True, "Logout realizado."
    except:
        return False, "Erro ao fazer logout."


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

        usuario = supabase_table_select(
            table="usuarios",
            filters={"id": session.user.id},
            limit=1,
        )

        return usuario[0] if usuario else None

    except:
        return None


def esta_autenticado() -> bool:
    return obter_usuario_atual() is not None


def e_admin() -> bool:
    usuario = obter_usuario_atual()
    return usuario.get("is_admin", False) if usuario else False


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "cadastrar_usuario",
    "fazer_login",
    "fazer_logout",
    "obter_usuario_atual",
    "esta_autenticado",
    "e_admin",
]

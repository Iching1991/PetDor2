"""
Autenticação e Cadastro de Usuários — PETDor2
Versão estável para Supabase Auth + constraints + rate limit
"""

from typing import Tuple, Optional, Dict, Any
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# 🔧 NORMALIZAÇÃO DE TIPO (compatível com constraint)
# ==========================================================

TIPOS_VALIDOS = {
    "admin": "admin",
    "tutor": "tutor",
    "veterinario": "vet",
    "vet": "vet",
    "clinica": "clinica",
    "clínica": "clinica",
}


def normalizar_tipo(tipo: str) -> str:
    if not tipo:
        return "tutor"
    return TIPOS_VALIDOS.get(tipo.lower().strip(), "tutor")


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
        # -------------------------
        # Normalização
        # -------------------------
        nome = nome.strip()
        email = email.lower().strip()
        senha = senha.strip()
        tipo = normalizar_tipo(tipo)
        pais = pais.strip()

        # -------------------------
        # Validações básicas
        # -------------------------
        if len(nome) < 3:
            return False, "Nome muito curto."

        if "@" not in email:
            return False, "E-mail inválido."

        if len(senha) < 6:
            return False, "Senha deve ter no mínimo 6 caracteres."

        # -------------------------
        # Verificar duplicata
        # -------------------------
        existente = supabase_table_select(
            table="usuarios",
            filters={"email": email},
            limit=1,
        )

        if existente:
            return False, "E-mail já cadastrado."

        # -------------------------
        # Criar no Supabase Auth
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

        if not auth_resp or not auth_resp.user:
            return False, "Erro ao criar usuário no Auth."

        user_id = auth_resp.user.id

        # -------------------------
        # Criar perfil local
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

        return True, (
            "Conta criada com sucesso! "
            "Verifique seu e-mail para confirmar."
        )

    except Exception as e:
        logger.exception("Erro no cadastro")

        msg = str(e).lower()

        if "email rate limit exceeded" in msg:
            return False, "Limite de envio de e-mails atingido. Aguarde 15 minutos."

        if "429" in msg:
            return False, "Muitas tentativas. Aguarde alguns minutos."

        if "duplicate key" in msg:
            return False, "E-mail já cadastrado."

        if "usuarios_tipo_usuario_check" in msg:
            return False, "Tipo inválido. Use: tutor, vet ou clinica."

        return False, "Erro ao cadastrar."


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

        if not auth_resp or not auth_resp.user:
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
        msg = str(e).lower()

        if "email not confirmed" in msg:
            return False, "Confirme seu e-mail antes de fazer login.", None

        if "invalid login credentials" in msg:
            return False, "Credenciais inválidas.", None

        if "429" in msg:
            return False, "Muitas tentativas. Aguarde.", None

        return False, "Erro no login.", None


# ==========================================================
# 🚪 LOGOUT
# ==========================================================

def fazer_logout() -> Tuple[bool, str]:

    from backend.database.supabase_client import supabase

    try:
        supabase.auth.sign_out()
        return True, "Logout realizado."
    except:
        return False, "Erro no logout."


# ==========================================================
# 🔄 RECUPERAÇÃO DE SENHA
# ==========================================================

def solicitar_recuperacao_senha(email: str) -> Tuple[bool, str]:

    from backend.database.supabase_client import supabase

    try:
        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to":
                    st.secrets["app"]["STREAMLIT_APP_URL"]
                    + "/redefinir_senha"
            }
        )
        return True, "E-mail enviado."
    except Exception as e:
        if "429" in str(e):
            return False, "Aguarde antes de tentar novamente."
        return False, "Erro ao enviar e-mail."


# ==========================================================
# 🔐 REDEFINIR SENHA
# ==========================================================

def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:

    from backend.database.supabase_client import supabase

    try:
        if len(nova_senha) < 6:
            return False, "Senha fraca."

        supabase.auth.update_user({"password": nova_senha})

        return True, "Senha redefinida com sucesso."
    except:
        return False, "Erro ao redefinir senha."


# ==========================================================
# 👤 USUÁRIO ATUAL
# ==========================================================

def obter_usuario_atual():

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

    except:
        return None


# ==========================================================
# 👑 ADMIN
# ==========================================================

def e_admin() -> bool:

    usuario = obter_usuario_atual()

    if not usuario:
        return False

    return usuario.get("is_admin", False) is True


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "cadastrar_usuario",
    "fazer_login",
    "fazer_logout",
    "solicitar_recuperacao_senha",
    "redefinir_senha",
    "obter_usuario_atual",
    "e_admin",
]
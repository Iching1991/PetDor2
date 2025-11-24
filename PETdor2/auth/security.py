# PETdor2/auth/security.py
"""
Módulo de segurança - hash de senhas e gerenciamento de tokens JWT.
"""
import bcrypt
import jwt
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui_mudar_em_producao")

def hash_password(senha: str) -> str:
    """Gera hash bcrypt da senha."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')

def verify_password(senha: str, hash_senha: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    try:
        return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False

def criar_token(usuario_id: int, expiracao_horas: int = 24) -> str:
    """Cria um token JWT com data de expiração."""
    payload = {
        "usuario_id": usuario_id,
        "exp": datetime.utcnow() + timedelta(hours=expiracao_horas),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def validar_token(token: str) -> dict:
    """Valida um token JWT e retorna o payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Token inválido")
        return None

def generate_reset_token(email: str, expiracao_horas: int = 1) -> str:
    """
    Gera um token JWT para reset de senha.
    Token expira em 1 hora por padrão.
    """
    payload = {
        "email": email,
        "tipo": "reset_password",
        "exp": datetime.utcnow() + timedelta(hours=expiracao_horas),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    logger.info(f"✅ Token de reset gerado para {email}")
    return token

def verify_reset_token(token: str) -> tuple[bool, str]:
    """
    Valida um token de reset de senha.
    Retorna (True, email) se válido, (False, mensagem_erro) se inválido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Verifica se é um token de reset
        if payload.get("tipo") != "reset_password":
            return False, "Token inválido (tipo incorreto)"

        email = payload.get("email")
        if not email:
            return False, "Token inválido (sem e-mail)"

        logger.info(f"✅ Token de reset válido para {email}")
        return True, email

    except jwt.ExpiredSignatureError:
        logger.warning("Token de reset expirado")
        return False, "Token expirado. Solicite um novo link."

    except jwt.InvalidTokenError as e:
        logger.warning(f"Token de reset inválido: {e}")
        return False, "Token inválido."

    except Exception as e:
        logger.error(f"Erro ao validar token de reset: {e}")
        return False, "Erro ao validar token."

def generate_email_confirmation_token(usuario_id: int, email: str, expiracao_horas: int = 24) -> str:
    """
    Gera um token JWT para confirmação de e-mail.
    Token expira em 24 horas por padrão.
    """
    payload = {
        "usuario_id": usuario_id,
        "email": email,
        "tipo": "email_confirmation",
        "exp": datetime.utcnow() + timedelta(hours=expiracao_horas),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    logger.info(f"✅ Token de confirmação de e-mail gerado para {email}")
    return token

def verify_email_confirmation_token(token: str) -> tuple[bool, int, str]:
    """
    Valida um token de confirmação de e-mail.
    Retorna (True, usuario_id, email) se válido, (False, None, mensagem_erro) se inválido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

        # Verifica se é um token de confirmação
        if payload.get("tipo") != "email_confirmation":
            return False, None, "Token inválido (tipo incorreto)"

        usuario_id = payload.get("usuario_id")
        email = payload.get("email")

        if not usuario_id or not email:
            return False, None, "Token inválido (dados incompletos)"

        logger.info(f"✅ Token de confirmação válido para {email}")
        return True, usuario_id, email

    except jwt.ExpiredSignatureError:
        logger.warning("Token de confirmação expirado")
        return False, None, "Token expirado. Solicite um novo link."

    except jwt.InvalidTokenError as e:
        logger.warning(f"Token de confirmação inválido: {e}")
        return False, None, "Token inválido."

    except Exception as e:
        logger.error(f"Erro ao validar token de confirmação: {e}")
        return False, None, "Erro ao validar token."

def usuario_logado():
    """Retorna o usuário logado da sessão do Streamlit."""
    import streamlit as st
    return st.session_state.get("usuario")

def logout():
    """Faz logout do usuário."""
    import streamlit as st
    st.session_state.usuario = None
    logger.info("✅ Usuário desconectado")

__all__ = [
    "hash_password",
    "verify_password",
    "criar_token",
    "validar_token",
    "generate_reset_token",
    "verify_reset_token",
    "generate_email_confirmation_token",
    "verify_email_confirmation_token",
    "usuario_logado",
    "logout",
]


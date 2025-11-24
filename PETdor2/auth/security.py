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

SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")

def hash_password(senha: str) -> str:
    """Gera hash bcrypt da senha."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')

def verify_password(senha: str, hash_senha: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))

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
        logger.error("Token expirado")
        return None
    except jwt.InvalidTokenError:
        logger.error("Token inválido")
        return None

def usuario_logado():
    """Retorna o usuário logado da sessão do Streamlit."""
    import streamlit as st
    return st.session_state.get("usuario")

def logout():
    """Faz logout do usuário."""
    import streamlit as st
    st.session_state.usuario = None

__all__ = ["hash_password", "verify_password", "criar_token", "validar_token", "usuario_logado", "logout"]

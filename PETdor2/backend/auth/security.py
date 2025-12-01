# PETdor2/backend/auth/security.py
"""
Módulo de segurança - hash de senhas e gerenciamento de tokens JWT.
"""
import bcrypt
import jwt
import logging
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# ==========================================================
# CONFIGURAÇÕES DE SEGURANÇA
# ==========================================================
# A SECRET_KEY é CRÍTICA para a segurança dos tokens JWT.
# Use uma chave forte e armazene-a de forma segura (variável de ambiente).
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui_mudar_em_producao")
ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30 # Não usado diretamente aqui, mas útil para tokens de sessão
RESET_TOKEN_EXPIRE_HOURS = 1 # Token de reset de senha expira em 1 hora
CONFIRMATION_TOKEN_EXPIRE_HOURS = 24 # Token de confirmação de e-mail expira em 24 horas

# ==========================================================
# HASHING DE SENHAS (BCRYPT)
# ==========================================================
def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        logger.error("Hash de senha inválido fornecido para verificação.", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao verificar senha: {e}", exc_info=True)
        return False

# ==========================================================
# GERAÇÃO E VALIDAÇÃO DE TOKENS JWT
# ==========================================================
def gerar_token_reset_senha(email: str, expiracao_horas: int = RESET_TOKEN_EXPIRE_HOURS) -> str:
    """
    Gera um token JWT para reset de senha.
    Token expira em 1 hora por padrão.
    """
    payload = {
        "sub": email, # Subject do token, geralmente o identificador do usuário
        "tipo": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=expiracao_horas),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"✅ Token de reset de senha gerado para {email}")
    return token

def validar_token_reset_senha(token: str) -> Tuple[bool, Optional[str]]:
    """
    Valida um token de reset de senha.
    Retorna (True, email) se válido, (False, mensagem_erro) se inválido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("tipo") != "password_reset":
            return False, "Token inválido (tipo incorreto)"
        email = payload.get("sub")
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
        logger.error(f"Erro ao validar token de reset: {e}", exc_info=True)
        return False, "Erro ao validar token."

def gerar_token_confirmacao_email(usuario_id: int, email: str, expiracao_horas: int = CONFIRMATION_TOKEN_EXPIRE_HOURS) -> str:
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
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"✅ Token de confirmação de e-mail gerado para {email}")
    return token

def validar_token_confirmacao_email(token: str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Valida um token de confirmação de e-mail.
    Retorna (True, usuario_id, email) se válido, (False, None, mensagem_erro) se inválido.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
        logger.error(f"Erro ao validar token de confirmação: {e}", exc_info=True)
        return False, None, "Erro ao validar token."

__all__ = [
    "hash_password",
    "verify_password",
    "gerar_token_reset_senha",
    "validar_token_reset_senha",
    "gerar_token_confirmacao_email",
    "validar_token_confirmacao_email",
]

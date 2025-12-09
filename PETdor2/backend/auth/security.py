# PetDor2/backend/auth/security.py
"""
Módulo central de segurança do PETDOR.
Inclui:
- Hashing e verificação de senha com bcrypt
- Criação e validação de tokens JWT
- Tokens específicos para reset de senha e confirmação de e-mail
- Funções auxiliares de sessão (Streamlit)
"""

import os
import bcrypt
import jwt
import logging
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURAÇÃO DO JWT
# =============================================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "sua_chave_secreta_muito_longa_e_aleatoria_mude_em_producao"
)
ALGORITHM = "HS256"


# =============================================================================
# HASH DE SENHA
# =============================================================================

def hash_password(senha: str) -> str:
    """Gera hash seguro usando bcrypt."""
    try:
        hashed = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
        return hashed.decode("utf-8")
    except Exception as e:
        logger.error(f"Erro ao gerar hash da senha: {e}")
        raise


def verify_password(senha: str, senha_hash: str) -> bool:
    """Valida senha contra hash armazenado."""
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except Exception as e:
        logger.error(f"Erro na verificação de senha: {e}")
        return False


# =============================================================================
# JWT - BASE
# =============================================================================

def gerar_token_jwt(dados: Dict[str, Any], expiracao_horas: int = 1) -> str:
    """Gera JWT com expiração definida."""
    try:
        agora = datetime.now(timezone.utc)
        payload = {
            **dados,
            "iat": agora,
            "exp": agora + timedelta(hours=expiracao_horas),
        }
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        logger.error(f"Erro ao gerar JWT: {e}")
        raise


def validar_token_jwt(token: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Valida JWT e retorna payload ou erro."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload, "Token válido"
    except jwt.ExpiredSignatureError:
        return None, "Token expirado"
    except jwt.InvalidTokenError:
        return None, "Token inválido"
    except Exception as e:
        logger.error(f"Erro ao validar JWT: {e}")
        return None, "Erro na validação do token"


# =============================================================================
# TOKENS ESPECÍFICOS — RESET DE SENHA
# =============================================================================

def gerar_token_reset_senha(usuario_id: int, email: str) -> str:
    """Gera token JWT exclusivo para recuperar senha."""
    dados = {
        "tipo": "reset_senha",
        "usuario_id": usuario_id,
        "email": email,
    }
    return gerar_token_jwt(dados, expiracao_horas=1)


def validar_token_reset_senha(token: str) -> Optional[Dict[str, Any]]:
    """
    Valida token de reset e retorna payload ou None.
    """
    payload, msg = validar_token_jwt(token)
    if not payload:
        return None

    if payload.get("tipo") != "reset_senha":
        return None

    if not payload.get("email") or not payload.get("usuario_id"):
        return None

    return payload


# =============================================================================
# TOKENS ESPECÍFICOS — CONFIRMAÇÃO DE E-MAIL
# =============================================================================

def gerar_token_confirmacao_email(usuario_id: int, email: str) -> str:
    """Gera token JWT para confirmação de e-mail."""
    dados = {
        "tipo": "confirmacao_email",
        "usuario_id": usuario_id,
        "email": email,
    }
    return gerar_token_jwt(dados, expiracao_horas=24)


def validar_token_confirmacao_email(token: str) -> Optional[Dict[str, Any]]:
    """Valida token de confirmação de e-mail."""
    payload, msg = validar_token_jwt(token)
    if not payload:
        return None

    if payload.get("tipo") != "confirmacao_email":
        return None

    if not payload.get("email") or not payload.get("usuario_id"):
        return None

    return payload


# =============================================================================
# LEGADOS — MANTIDOS TEMPORARIAMENTE PARA COMPATIBILIDADE
# =============================================================================

def gerar_token(expiracao_horas: int = 1) -> Tuple[str, str]:
    """Token legado simples (⚠️ não recomendado para produção)."""
    logger.warning("Função legada 'gerar_token' usada. Prefira JWT.")
    import secrets
    token = secrets.token_urlsafe(32)
    expira_em = (datetime.now() + timedelta(hours=expiracao_horas)).strftime("%Y-%m-%d %H:%M:%S")
    return token, expira_em


def token_valido(expira_em: str) -> bool:
    """Validação legada — NÃO USE EM NOVOS CÓDIGOS."""
    logger.warning("Função legada 'token_valido' usada. Prefira JWT.")
    try:
        return datetime.strptime(expira_em, "%Y-%m-%d %H:%M:%S") > datetime.now()
    except:
        return False


# =============================================================================
# SESSÃO — STREAMLIT
# =============================================================================

def usuario_logado(session_state) -> bool:
    """Retorna True se usuário estiver autenticado no Streamlit."""
    return session_state.get("user_id") is not None


def logout(session_state) -> None:
    """Limpa dados de login do Streamlit."""
    session_state.pop("user_id", None)
    session_state.pop("user_data", None)
    session_state["page"] = "Login"
    logger.info("Usuário desconectado.")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "hash_password",
    "verify_password",
    "gerar_token_jwt",
    "validar_token_jwt",
    "gerar_token_reset_senha",
    "validar_token_reset_senha",
    "gerar_token_confirmacao_email",
    "validar_token_confirmacao_email",
    "usuario_logado",
    "logout",
    # Legados
    "gerar_token",
    "token_valido",
]

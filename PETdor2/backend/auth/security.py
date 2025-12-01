# PetDor2/auth/security.py
"""
Módulo de segurança do PETDOR
Inclui hashing de senha (bcrypt), verificação e tokens JWT (melhor que tokens simples).
Mantém compatibilidade com funções antigas.
"""
import bcrypt
import jwt
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)

# Chave secreta para JWT - DEVE ser definida no .env
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui_mudar_em_producao")
ALGORITHM = "HS256"

# -------------------------------
# HASH DE SENHA (mantido igual)
# -------------------------------
def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash seguro para a senha (compatível com código antigo).
    """
    try:
        hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        return hash_senha.decode('utf-8')
    except Exception as e:
        logger.error(f"Erro ao gerar hash de senha: {e}")
        raise

# -------------------------------
# VALIDAR SENHA (mantido igual)
# -------------------------------
def verificar_senha(senha: str, hash_senha: str) -> bool:
    """
    Verifica se a senha corresponde ao hash (compatível com código antigo).
    """
    try:
        return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False

# -------------------------------
# TOKENS JWT (NOVO - melhor que tokens simples)
# -------------------------------
def gerar_token_jwt(dados: Dict[str, Any], expiracao_horas: int = 1) -> str:
    """
    Gera token JWT com expiração.
    """
    try:
        payload = {
            **dados,
            "exp": datetime.now(timezone.utc) + timedelta(hours=expiracao_horas),
            "iat": datetime.now(timezone.utc)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    except Exception as e:
        logger.error(f"Erro ao gerar token JWT: {e}")
        raise

def validar_token_jwt(token: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Valida token JWT e retorna payload ou mensagem de erro.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload, "Token válido"
    except jwt.ExpiredSignatureError:
        return None, "Token expirado"
    except jwt.InvalidTokenError:
        return None, "Token inválido"
    except Exception as e:
        logger.error(f"Erro ao validar token JWT: {e}")
        return None, "Erro na validação do token"

# -------------------------------
# TOKENS PARA RESET DE SENHA (NOVO)
# -------------------------------
def gerar_token_reset_senha(email: str, user_id: int) -> str:
    """
    Gera token JWT específico para reset de senha.
    """
    dados = {"tipo": "reset_senha", "email": email, "user_id": user_id}
    return gerar_token_jwt(dados, expiracao_horas=1)  # Expira em 1 hora

def validar_token_reset_senha(token: str) -> Tuple[Optional[str], str]:
    """
    Valida token de reset de senha e retorna email ou mensagem de erro.
    """
    payload, mensagem = validar_token_jwt(token)
    if not payload:
        return None, mensagem

    if payload.get("tipo") != "reset_senha":
        return None, "Token inválido para reset de senha"

    email = payload.get("email")
    if not email:
        return None, "Token corrompido"

    return email, "Token válido"

# -------------------------------
# TOKENS PARA CONFIRMAÇÃO DE E-MAIL (NOVO)
# -------------------------------
def gerar_token_confirmacao_email(email: str, user_id: int) -> str:
    """
    Gera token JWT específico para confirmação de e-mail.
    """
    dados = {"tipo": "confirmacao_email", "email": email, "user_id": user_id}
    return gerar_token_jwt(dados, expiracao_horas=24)  # Expira em 24 horas

def validar_token_confirmacao_email(token: str) -> Tuple[Optional[str], str]:
    """
    Valida token de confirmação e-mail e retorna email ou mensagem de erro.
    """
    payload, mensagem = validar_token_jwt(token)
    if not payload:
        return None, mensagem

    if payload.get("tipo") != "confirmacao_email":
        return None, "Token inválido para confirmação de e-mail"

    email = payload.get("email")
    if not email:
        return None, "Token corrompido"

    return email, "Token válido"

# -------------------------------
# FUNÇÕES ANTIGAS (para compatibilidade)
# -------------------------------
def gerar_token(expiracao_horas: int = 1) -> Tuple[str, str]:
    """
    Mantém compatibilidade com código antigo (tokens bcrypt simples).
    """
    try:
        # Gera token simples (não recomendado para produção)
        import secrets
        token = secrets.token_urlsafe(32)
        expira_em = (datetime.now() + timedelta(hours=expiracao_horas)).strftime("%Y-%m-%d %H:%M:%S")
        return token, expira_em
    except Exception as e:
        logger.error(f"Erro ao gerar token simples: {e}")
        raise

def token_valido(expira_em: str) -> bool:
    """
    Mantém compatibilidade com código antigo.
    """
    try:
        return datetime.strptime(expira_em, "%Y-%m-%d %H:%M:%S") > datetime.now()
    except Exception as e:
        logger.error(f"Erro ao validar expiração do token simples: {e}")
        return False

# -------------------------------
# FUNÇÕES DE SESSÃO (para Streamlit)
# -------------------------------
def usuario_logado(session_state) -> bool:
    """Verifica se usuário está logado (para Streamlit session_state)."""
    return "user_id" in session_state and session_state["user_id"] is not None

def logout(session_state) -> None:
    """Faz logout limpando session_state (para Streamlit)."""
    if "user_id" in session_state:
        del session_state["user_id"]
    if "user_data" in session_state:
        del session_state["user_data"]
    logger.info("👋 Usuário fez logout")

__all__ = [
    "gerar_hash_senha",
    "verificar_senha",
    "gerar_token_jwt",
    "validar_token_jwt",
    "gerar_token_reset_senha",
    "validar_token_reset_senha",
    "gerar_token_confirmacao_email",
    "validar_token_confirmacao_email",
    "usuario_logado",
    "logout",
    # Compatibilidade
    "gerar_token",
    "token_valido",
]

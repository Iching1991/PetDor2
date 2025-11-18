"""
Módulo de segurança do PETDOR
Inclui hashing de senha, verificação e geração de tokens
"""
import bcrypt
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# -------------------------------
# HASH DE SENHA
# -------------------------------
def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash seguro para a senha
    """
    try:
        hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        return hash_senha.decode('utf-8')
    except Exception as e:
        logger.error(f"Erro ao gerar hash de senha: {e}")
        raise

# -------------------------------
# VALIDAR SENHA
# -------------------------------
def verificar_senha(senha: str, hash_senha: str) -> bool:
    """
    Verifica se a senha corresponde ao hash
    """
    try:
        return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False

# -------------------------------
# GERAR TOKEN
# -------------------------------
def gerar_token(expiracao_horas: int = 1) -> (str, str):
    """
    Gera token único (bcrypt) e retorna token + data de expiração
    """
    try:
        token = bcrypt.gensalt().decode()
        expira_em = (datetime.now() + timedelta(hours=expiracao_horas)).strftime("%Y-%m-%d %H:%M:%S")
        return token, expira_em
    except Exception as e:
        logger.error(f"Erro ao gerar token: {e}")
        raise

# -------------------------------
# VALIDAR EXPIRAÇÃO
# -------------------------------
def token_valido(expira_em: str) -> bool:
    """
    Verifica se o token ainda é válido
    """
    try:
        return datetime.strptime(expira_em, "%Y-%m-%d %H:%M:%S") > datetime.now()
    except Exception as e:
        logger.error(f"Erro ao validar expiração do token: {e}")
        return False

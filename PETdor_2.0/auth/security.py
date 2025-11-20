# PETdor_2.0/auth/security.py
"""
Módulo de segurança do PETDOR
Inclui hashing de senha, verificação e geração de tokens
"""
import bcrypt
from datetime import datetime, timedelta
import logging
import uuid # Adicionado para gerar tokens únicos

logger = logging.getLogger(__name__)

# -------------------------------
# HASH DE SENHA
# -------------------------------
def hash_password(senha: str) -> str: # RENOMEADO de gerar_hash_senha
    """
    Gera um hash seguro para a senha.
    """
    try:
        hash_senha = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        return hash_senha.decode('utf-8')
    except Exception as e:
        logger.error(f"Erro ao gerar hash de senha: {e}")
        raise

# -------------------------------
# VERIFICAR SENHA
# -------------------------------
def verify_password(senha: str, hashed_password: str) -> bool: # RENOMEADO de verificar_senha
    """
    Verifica se a senha fornecida corresponde ao hash armazenado.
    """
    try:
        return bcrypt.checkpw(senha.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False

# -------------------------------
# GERAR TOKEN DE CONFIRMAÇÃO DE E-MAIL
# -------------------------------
def generate_email_token() -> str: # RENOMEADO de gerar_token e adaptado para e-mail
    """
    Gera um token único para confirmação de e-mail usando UUID.
    """
    return str(uuid.uuid4())

# -------------------------------
# VERIFICAR TOKEN DE E-MAIL (SIMPLIFICADO)
# -------------------------------
def verify_email_token(token: str) -> bool:
    """
    Verifica a validade básica de um token de e-mail.
    (A lógica de expiração e uso único é geralmente tratada no banco de dados).
    """
    return bool(token) # Um token UUID é "válido" se não for nulo/vazio.
                       # A validação real (se já foi usado, se expirou)
                       # é feita na função confirmar_email no user.py.

# As funções 'gerar_token' e 'token_valido' originais foram adaptadas/removidas
# para corresponder às importações de 'user.py'. Se precisar de tokens com
# expiração para outras finalidades, podemos recriá-las.

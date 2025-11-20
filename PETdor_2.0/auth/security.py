# PETdor_2.0/auth/security.py
"""
Módulo de segurança do PETDOR
Inclui hashing de senha, verificação e geração de tokens
"""
import bcrypt
from datetime import datetime, timedelta
import logging
import uuid # Adicionei uuid aqui, caso generate_email_token precise dele

logger = logging.getLogger(__name__)

# -------------------------------
# HASH DE SENHA
# -------------------------------
def hash_password(senha: str) -> str: # RENOMEADO de gerar_hash_senha
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
def verify_password(senha: str, hashed_password: str) -> bool: # RENOMEADO de verificar_senha
    """
    Verifica se a senha corresponde ao hash
    """
    try:
        return bcrypt.checkpw(senha.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False

# -------------------------------
# GERAR TOKEN DE E-MAIL
# -------------------------------
def generate_email_token() -> str: # RENOMEADO de gerar_token, e simplificado para email
    """
    Gera um token único para confirmação de e-mail.
    """
    return str(uuid.uuid4()) # Usando uuid para um token simples e único

# -------------------------------
# VALIDAR TOKEN DE E-MAIL (se precisar de verificação de expiração)
# -------------------------------
# Se você tiver um token que expira, pode usar uma função como esta.
# No seu user.py, você importa verify_email_token, então vamos criar uma.
def verify_email_token(token: str) -> bool:
    """
    Verifica a validade de um token de e-mail.
    (Atualmente, apenas verifica se não é nulo/vazio. A lógica de expiração
    será tratada no banco de dados, se o token tiver um campo de expiração lá.)
    """
    return bool(token) # Um token UUID é sempre "válido" até ser usado ou expirado no DB

# Nota: A função 'token_valido' e 'gerar_token' com expiração foram removidas/adaptadas
# para focar nos nomes que você importa e na funcionalidade de e-mail.
# Se precisar de tokens com expiração para outras finalidades, podemos recriar.

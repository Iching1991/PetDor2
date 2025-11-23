# PETdor2/auth/security.py
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

# Certifique-se de que SECRET_KEY está definida nas variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_padrao_muito_segura_e_longa")
if SECRET_KEY == "sua_chave_secreta_padrao_muito_segura_e_longa":
    logger.warning("SECRET_KEY não definida nas variáveis de ambiente. Usando valor padrão. ISSO NÃO É SEGURO PARA PRODUÇÃO!")

def hash_password(password):
    """Gera o hash de uma senha."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Verifica se uma senha corresponde ao hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def generate_email_token(email, expiration_hours=24):
    """Gera um token JWT para confirmação de e-mail."""
    payload = {
        "email": email,
        "exp": datetime.now() + timedelta(hours=expiration_hours),
        "type": "email_confirmation"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_email_token(token):
    """Verifica e decodifica um token JWT de confirmação de e-mail."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") == "email_confirmation":
            return True, payload["email"]
        return False, None
    except jwt.ExpiredSignatureError:
        logger.warning("Token de confirmação de e-mail expirado.")
        return False, None
    except jwt.InvalidTokenError:
        logger.warning("Token de confirmação de e-mail inválido.")
        return False, None

def generate_reset_token(email, expiration_hours=1):
    """Gera um token JWT para redefinição de senha."""
    payload = {
        "email": email,
        "exp": datetime.now() + timedelta(hours=expiration_hours),
        "type": "password_reset"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_reset_token(token):
    """Verifica e decodifica um token JWT de redefinição de senha."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") == "password_reset":
            return True, payload["email"]
        return False, None
    except jwt.ExpiredSignatureError:
        logger.warning("Token de redefinição de senha expirado.")
        return False, None
    except jwt.InvalidTokenError:
        logger.warning("Token de redefinição de senha inválido.")
        return False, None

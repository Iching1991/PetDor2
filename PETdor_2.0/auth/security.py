# PETdor_2_0/auth/security.py
import os
from datetime import datetime, timedelta
import jwt
import bcrypt # Ou from passlib.context import CryptContext se você trocou

# --- Configuração para bcrypt ---
# Se você está usando bcrypt diretamente:
def hash_password(password: str) -> str:
    # bcrypt.gensalt() gera um salt aleatório
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

# Se você está usando passlib:
# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)
# def verify_password(password: str, hashed: str) -> bool:
#     return pwd_context.verify(password, hashed)


# --- Configuração para JWT (tokens de e-mail e reset de senha) ---
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_muito_segura") # Use uma chave forte em produção!
ALGORITHM = "HS256"

def generate_email_token(email: str) -> str:
    expire = datetime.now() + timedelta(hours=24) # Token válido por 24 horas
    to_encode = {"sub": email, "exp": expire, "type": "email_confirm"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_email_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "email_confirm":
            return payload.get("sub")
        return None
    except jwt.ExpiredSignatureError:
        return None # Token expirado
    except jwt.InvalidTokenError:
        return None # Token inválido

def generate_reset_token(email: str) -> str:
    expire = datetime.now() + timedelta(hours=1) # Token válido por 1 hora
    to_encode = {"sub": email, "exp": expire, "type": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_reset_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") == "password_reset":
            return payload.get("sub")
        return None
    except jwt.ExpiredSignatureError:
        return None # Token expirado
    except jwt.InvalidTokenError:
        return None # Token inválido

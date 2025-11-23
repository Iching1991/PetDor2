# PETdor2/auth/security.py
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
import os
import logging

logger = logging.getLogger(__name__)

# ===============================
# Configuração da SECRET_KEY
# ===============================
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_padrao_muito_segura_e_longa")
if SECRET_KEY == "sua_chave_secreta_padrao_muito_segura_e_longa":
    logger.warning(
        "SECRET_KEY não definida nas variáveis de ambiente. "
        "Usando valor padrão. ISSO NÃO É SEGURO PARA PRODUÇÃO!"
    )

# ===============================
# Funções de hash de senha
# ===============================
def hash_password(password: str) -> str:
    """Gera o hash de uma senha usando bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica se a senha corresponde ao hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


# ===============================
# Funções de token JWT
# ===============================
def _generate_token(email: str, token_type: str, expiration_hours: int) -> str:
    """Gera um token JWT genérico."""
    payload = {
        "email": email,
        "type": token_type,
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=expiration_hours)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def _verify_token(token: str, expected_type: str) -> tuple[bool, str | None]:
    """
    Verifica e decodifica um token JWT.
    Retorna (True, email) se válido, (False, None) caso contrário.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") == expected_type:
            return True, payload.get("email")
        return False, None
    except jwt.ExpiredSignatureError:
        logger.warning(f"Token {expected_type} expirado.")
        return False, None
    except jwt.InvalidTokenError:
        logger.warning(f"Token {expected_type} inválido.")
        return False, None


# ===============================
# Token específico para e-mail
# ===============================
def generate_email_token(email: str, expiration_hours: int = 24) -> str:
    """Gera token JWT para confirmação de e-mail."""
    return _generate_token(email, "email_confirmation", expiration_hours)


def verify_email_token(token: str) -> str | None:
    """Verifica token JWT de confirmação de e-mail e retorna e-mail se válido."""
    valid, email = _verify_token(token, "email_confirmation")
    return email if valid else None


# ===============================
# Token específico para reset de senha
# ===============================
def generate_reset_token(email: str, expiration_hours: int = 1) -> str:
    """Gera token JWT para redefinição de senha."""
    return _generate_token(email, "password_reset", expiration_hours)


def verify_reset_token(token: str) -> str | None:
    """Verifica token JWT de redefinição de senha e retorna e-mail se válido."""
    valid, email = _verify_token(token, "password_reset")
    return email if valid else None

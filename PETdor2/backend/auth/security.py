# PetDor2/backend/auth/security.py
import streamlit as st
import bcrypt
import jwt
from datetime import datetime, timedelta
import secrets
from typing import Optional, Dict, Any

def gerar_hash_senha(senha: str) -> str:
    """
    Gera um hash bcrypt da senha fornecida.

    Args:
        senha: Senha em texto plano

    Returns:
        Hash da senha
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')

def verificar_senha(senha: str, hash_senha: str) -> bool:
    """
    Verifica se a senha corresponde ao hash.

    Args:
        senha: Senha em texto plano
        hash_senha: Hash armazenado no banco

    Returns:
        True se a senha estiver correta, False caso contrário
    """
    return bcrypt.checkpw(senha.encode('utf-8'), hash_senha.encode('utf-8'))

def gerar_token(usuario_id: int, email: str, tipo_usuario: str, is_admin: bool = False, expiracao_horas: int = 24) -> str:
    """
    Gera um token JWT com informações do usuário.

    Args:
        usuario_id: ID do usuário no banco
        email: Email do usuário
        tipo_usuario: Tipo do usuário (tutor, veterinario, clinica)
        is_admin: Se o usuário é admin
        expiracao_horas: Tempo de expiração do token em horas

    Returns:
        Token JWT assinado
    """
    try:
        secret_key = st.secrets.get("SECRET_KEY", "chave-secreta-padrao-desenvolvimento")

        payload = {
            "id": str(usuario_id),  # Convertido para string para compatibilidade
            "user_id": str(usuario_id),  # Alias para auth.jwt()->>'user_id'
            "email": email,
            "tipo_usuario": tipo_usuario,
            "is_admin": is_admin,
            "exp": datetime.utcnow() + timedelta(hours=expiracao_horas),
            "iat": datetime.utcnow()
        }

        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
    except Exception as e:
        st.error(f"Erro ao gerar token: {e}")
        return None

def verificar_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica e decodifica um token JWT.

    Args:
        token: Token JWT a ser verificado

    Returns:
        Dicionário com os dados do usuário ou None se inválido
    """
    try:
        secret_key = st.secrets.get("SECRET_KEY", "chave-secreta-padrao-desenvolvimento")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        st.error("Token expirado. Faça login novamente.")
        return None
    except jwt.InvalidTokenError:
        st.error("Token inválido.")
        return None
    except Exception as e:
        st.error(f"Erro ao verificar token: {e}")
        return None

def gerar_token_confirmacao_email() -> str:
    """
    Gera um token seguro para confirmação de email.

    Returns:
        Token aleatório de 32 caracteres hexadecimais
    """
    return secrets.token_urlsafe(32)

def gerar_token_reset_senha() -> str:
    """
    Gera um token seguro para reset de senha.

    Returns:
        Token aleatório de 32 caracteres hexadecimais
    """
    return secrets.token_urlsafe(32)

def validar_forca_senha(senha: str) -> tuple[bool, str]:
    """
    Valida a força de uma senha.

    Args:
        senha: Senha a ser validada

    Returns:
        Tupla (válida, mensagem)
    """
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres"

    if not any(c.isupper() for c in senha):
        return False, "A senha deve conter pelo menos uma letra maiúscula"

    if not any(c.islower() for c in senha):
        return False, "A senha deve conter pelo menos uma letra minúscula"

    if not any(c.isdigit() for c in senha):
        return False, "A senha deve conter pelo menos um número"

    return True, "Senha válida"

def fazer_login(email: str, senha: str) -> Optional[Dict[str, Any]]:
    """
    Realiza o login do usuário.

    Args:
        email: Email do usuário
        senha: Senha em texto plano

    Returns:
        Dicionário com token e dados do usuário ou None se falhar
    """
    from backend.auth.user import verificar_credenciais

    usuario = verificar_credenciais(email, senha)

    if not usuario:
        return None

    if not usuario.get("ativo", False):
        st.error("Usuário inativo. Entre em contato com o suporte.")
        return None

    if not usuario.get("email_confirmado", False):
        st.warning("Email não confirmado. Verifique sua caixa de entrada.")
        return None

    # Gerar token com TODOS os campos necessários
    token = gerar_token(
        usuario_id=usuario["id"],
        email=usuario["email"],
        tipo_usuario=usuario.get("tipo_usuario", "tutor"),
        is_admin=usuario.get("is_admin", False)
    )

    if not token:
        return None

    return {
        "token": token,
        "usuario": {
            "id": usuario["id"],
            "nome": usuario["nome"],
            "email": usuario["email"],
            "tipo_usuario": usuario.get("tipo_usuario", "tutor"),
            "is_admin": usuario.get("is_admin", False)
        }
    }

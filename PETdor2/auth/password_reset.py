# PETdor2/auth/password_reset.py
"""
Módulo de recuperação de senha - gerencia reset de senhas.
Usa tokens JWT com expiração de 1 hora.
"""
import logging
from datetime import datetime, timedelta
import os
from .security import generate_reset_token, verify_reset_token, hash_password
from utils.email_sender import enviar_email_recuperacao_senha
from database.supabase_client import get_supabase

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera token JWT de reset, salva no DB e envia e-mail.
    Retorna (True, msg) sempre que possível para não vazar existência.
    """
    try:
        supabase = get_supabase()

        # 1. Buscar usuário no Supabase
        response = (
            supabase
            .from_("usuarios")
            .select("id, nome, email")
            .eq("email", email.lower())
            .execute()
        )

        if not response.data:
            # Não revelar existência
            logger.warning(f"Tentativa de reset para e-mail não encontrado: {email}")
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

        usuario = response.data[0]
        usuario_id = usuario["id"]
        nome = usuario["nome"]
        email_db = usuario["email"]

        # 2. Gerar token JWT
        token = generate_reset_token(email_db)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        # 3. Salvar token no Supabase
        update_response = (
            supabase
            .from_("usuarios")
            .update({
                "reset_password_token": token,
                "reset_password_expires": expires_at.isoformat()
            })
            .eq("id", usuario_id)
            .execute()
        )

        if not update_response.data:
            logger.error(f"Erro ao salvar token para {email_db}")
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

        # 4. Enviar e-mail
        try:
            reset_link = f"{os.getenv('STREAMLIT_APP_URL', 'http://localhost:8501')}?action=reset_password&token={token}"
            email_enviado, msg_email = enviar_email_recuperacao_senha(
                email_db, 
                nome, 
                reset_link
            )
            if email_enviado:
                logger.info(f"✅ E-mail de redefinição enviado para {email_db}")
            else:
                logger.warning(f"Falha ao enviar e-mail para {email_db}: {msg_email}")

        except Exception as e:
            logger.warning(f"Erro ao enviar e-mail: {e}")

        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

    except Exception as e:
        logger.error(f"Erro em solicitar_reset_senha: {e}", exc_info=True)
        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

def validar_token_reset(token: str) -> tuple[bool, str, str]:
    """
    Verifica se um token de redefinição de senha é válido e não expirou.
    Retorna (True, mensagem, email_usuario) ou (False, mensagem, None)
    """
    try:
        supabase = get_supabase()

        # 1. Valida token JWT
        token_valido, resultado = verify_reset_token(token)

        if not token_valido:
            logger.warning(f"Tentativa de validação com token inválido")
            return False, resultado, None  # resultado contém a mensagem de erro

        email = resultado  # resultado contém o email

        # 2. Verifica se o token ainda está no banco de dados
        response = (
            supabase
            .from_("usuarios")
            .select("id, reset_password_expires")
            .eq("reset_password_token", token)
            .execute()
        )

        if not response.data:
            logger.warning(f"Tentativa de validação com token não encontrado no banco")
            return False, "Token de redefinição inválido ou já utilizado.", None

        usuario = response.data[0]
        expires_at = usuario.get("reset_password_expires")

        # 3. Verifica expiração
        if not expires_at or datetime.fromisoformat(expires_at) < datetime.utcnow():
            logger.warning(f"Tentativa de validação com token expirado para {email}")
            return False, "Token de redefinição expirado. Solicite um novo.", None

        logger.info(f"✅ Token de reset válido para {email}")
        return True, "Token válido.", email

    except Exception as e:
        logger.error(f"Erro em validar_token_reset: {e}", exc_info=True)
        return False, "Erro ao validar token.", None

def redefinir_senha_com_token(token: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine a senha de um usuário usando um token válido.
    """
    try:
        # 1. Validar token
        token_valido, msg, email_usuario = validar_token_reset(token)
        if not token_valido:
            return False, msg

        # 2. Validar força da senha
        if len(nova_senha) < 8:
            return False, "Senha deve ter pelo menos 8 caracteres."

        # 3. Criar hash da nova senha
        senha_hash = hash_password(nova_senha)

        # 4. Atualizar Supabase: nova senha e invalidar token
        supabase = get_supabase()
        update_response = (
            supabase
            .from_("usuarios")
            .update({
                "senha_hash": senha_hash,
                "reset_password_token": None,
                "reset_password_expires": None
            })
            .eq("email", email_usuario)
            .execute()
        )

        if not update_response.data:
            logger.error(f"Erro ao redefinir senha para {email_usuario}")
            return False, "Erro interno ao redefinir senha."

        logger.info(f"✅ Senha redefinida com sucesso para {email_usuario}")
        return True, "Senha redefinida com sucesso. Você já pode fazer login."

    except Exception as e:
        logger.error(f"Erro em redefinir_senha_com_token: {e}", exc_info=True)
        return False, "Erro interno ao redefinir senha."

__all__ = [
    "solicitar_reset_senha",
    "validar_token_reset",
    "redefinir_senha_com_token",
]

# PETdor2/auth/password_reset.py
import streamlit as st
import logging
from datetime import datetime, timedelta
import os

from database.connection import conectar_db
from auth.security import generate_reset_token, verify_reset_token # Nomes padronizados
from auth.user import buscar_usuario_por_email, redefinir_senha # Reutiliza redefinir_senha do user.py
from utils.email_sender import enviar_email_recuperacao_senha # Nome da função corrigido

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera um token de reset de senha e envia por e-mail.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        usuario = buscar_usuario_por_email(email)
        if not usuario:
            logger.warning(f"Tentativa de reset de senha para e-mail não registrado: {email}")
            # Para segurança, sempre retorne uma mensagem genérica, mesmo se o e-mail não existir
            return True, "Se o e-mail estiver registrado, um link de redefinição de senha será enviado."

        token = generate_reset_token(email)
        expires_at = datetime.utcnow() + timedelta(minutes=30) # Token expira em 30 minutos

        cur.execute(
            "UPDATE usuarios SET reset_password_token = %s, reset_password_expires = %s WHERE id = %s",
            (token, expires_at, usuario["id"])
        )
        conn.commit()

        ok_email, msg_email = enviar_email_recuperacao_senha(email, token)
        if ok_email:
            logger.info(f"Link de reset de senha enviado para {email}")
            return True, "Um link de redefinição de senha foi enviado para o seu e-mail."
        else:
            logger.error(f"Falha ao enviar e-mail de reset de senha para {email}: {msg_email}")
            return False, f"Erro ao enviar e-mail de redefinição de senha: {msg_email}"

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao solicitar reset de senha para {email}: {e}", exc_info=True)
        return False, f"Erro interno ao solicitar redefinição de senha: {e}"
    finally:
        if conn:
            conn.close()

def validar_token_reset(token: str) -> tuple[bool, str, str | None]:
    """
    Valida um token de reset de senha.
    Retorna (status, mensagem, email_do_token).
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        email_do_token = verify_reset_token(token)
        if not email_do_token:
            return False, "Token inválido ou expirado.", None

        cur.execute(
            "SELECT id, email, reset_password_expires FROM usuarios WHERE email = %s AND reset_password_token = %s",
            (email_do_token, token)
        )
        usuario_db = cur.fetchone()

        if not usuario_db:
            return False, "Token não encontrado ou já utilizado.", None

        # Verificar expiração do token no banco de dados
        if usuario_db[2] and usuario_db[2] < datetime.utcnow():
            return False, "Token expirado.", None

        return True, "Token válido.", email_do_token
    except Exception as e:
        logger.error(f"Erro ao validar token de reset de senha: {e}", exc_info=True)
        return False, f"Erro interno ao validar token: {e}", None
    finally:
        if conn:
            conn.close()

def redefinir_senha_com_token(token: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine a senha de um usuário após a validação do token.
    Esta função também invalida o token após o uso.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Primeiro, valida o token para obter o e-mail
        status_validacao, msg_validacao, email_usuario = validar_token_reset(token)
        if not status_validacao or not email_usuario:
            return False, msg_validacao

        # Redefine a senha usando a função de user.py
        ok_redefinir, msg_redefinir = redefinir_senha(email_usuario, nova_senha)
        if not ok_redefinir:
            return False, msg_redefinir

        # Invalida o token após o uso
        cur.execute(
            "UPDATE usuarios SET reset_password_token = NULL, reset_password_expires = NULL WHERE email = %s",
            (email_usuario,)
        )
        conn.commit()
        logger.info(f"Senha redefinida e token invalidado para {email_usuario}")
        return True, "Senha redefinida com sucesso."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao redefinir senha com token: {e}", exc_info=True)
        return False, f"Erro interno ao redefinir senha: {e}"
    finally:
        if conn:
            conn.close()

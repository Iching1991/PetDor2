# PETdor_2_0/auth/password_reset.py
import logging
import streamlit as st
import os
from datetime import datetime, timedelta

from database.connection import conectar_db
from .security import hash_password, generate_email_token, verify_email_token, verify_password # Importa as funções de segurança com os nomes corretos
from utils.email_sender import enviar_email_recuperacao_senha # Importação absoluta para o email_sender

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera um token de reset de senha e envia um e-mail para o usuário.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # 1. Buscar usuário pelo e-mail
        cur.execute("SELECT id, nome, email FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()

        if not usuario:
            logger.warning(f"Tentativa de reset de senha para e-mail não encontrado: {email}")
            return False, "Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha."

        # 2. Gerar um token de reset (podemos reutilizar generate_email_token ou criar um específico)
        reset_token = generate_email_token() # Reutilizando a função de token
        token_expiracao = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S") # Token expira em 1 hora

        # 3. Armazenar o token e a expiração no banco de dados para o usuário
        cur.execute(
            "UPDATE usuarios SET reset_password_token = %s, reset_password_expires = %s WHERE id = %s",
            (reset_token, token_expiracao, usuario['id'])
        )
        conn.commit()

        # 4. Enviar e-mail com o link de reset
        enviar_email_recuperacao_senha(usuario['email'], usuario['nome'], reset_token)

        logger.info(f"Link de reset de senha enviado para {email}")
        return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir sua senha."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao solicitar reset de senha para {email}: {e}", exc_info=True)
        return False, f"Erro interno ao solicitar reset de senha: {e}"
    finally:
        if conn:
            conn.close()

def validar_token_reset(token: str) -> tuple[bool, str, str | None]:
    """
    Verifica se o token de reset de senha é válido e não expirou.
    Retorna (True, email_do_usuario) se válido, (False, None) caso contrário.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, email, reset_password_expires FROM usuarios WHERE reset_password_token = %s",
            (token,)
        )
        usuario = cur.fetchone()

        if not usuario:
            return False, "Token de redefinição de senha inválido ou já utilizado.", None

        expiracao_str = usuario['reset_password_expires']
        if expiracao_str:
            token_expiracao = datetime.strptime(expiracao_str, "%Y-%m-%d %H:%M:%S")
            if datetime.now() > token_expiracao:
                # Token expirado, limpar no banco de dados
                cur.execute("UPDATE usuarios SET reset_password_token = NULL, reset_password_expires = NULL WHERE id = %s", (usuario['id'],))
                conn.commit()
                return False, "Token de redefinição de senha expirado. Por favor, solicite um novo.", None
        else:
            # Se não há data de expiração, o token é inválido (ou já foi usado)
            return False, "Token de redefinição de senha inválido ou já utilizado.", None

        return True, "Token válido.", usuario['email']

    except Exception as e:
        logger.error(f"Erro ao validar token de reset de senha: {e}", exc_info=True)
        return False, f"Erro interno ao validar token: {e}", None
    finally:
        if conn:
            conn.close()

def redefinir_senha(email: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine a senha do usuário após a validação do token.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Hash da nova senha
        senha_hash = hash_password(nova_senha)

        # Atualizar a senha e limpar o token de reset
        cur.execute(
            "UPDATE usuarios SET senha_hash = %s, reset_password_token = NULL, reset_password_expires = NULL WHERE email = %s",
            (senha_hash, email)
        )
        conn.commit()

        logger.info(f"Senha redefinida com sucesso para {email}")
        return True, "Sua senha foi redefinida com sucesso. Você já pode fazer login."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao redefinir senha para {email}: {e}", exc_info=True)
        return False, f"Erro interno ao redefinir senha: {e}"
    finally:
        if conn:
            conn.close()

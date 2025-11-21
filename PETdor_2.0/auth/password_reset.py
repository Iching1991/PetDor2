# PETdor_2_0/auth/password_reset.py
import streamlit as st
import logging
from datetime import datetime, timedelta
import os # Adicionado para usar os.getenv se necessário para URLs

from database.connection import conectar_db
# Importa as funções de segurança para tokens de reset
from .security import generate_reset_token, verify_reset_token # Assumindo que estas serão criadas/renomeadas em security.py
# Importa a função de envio de e-mail com o nome CORRETO
from utils.email_sender import enviar_email_recuperacao_senha # CORRIGIDO: nome da função

logger = logging.getLogger(__name__)

def solicitar_reset_senha(email: str):
    """
    Inicia o processo de redefinição de senha para o e-mail fornecido.
    Gera um token de reset e envia um e-mail ao usuário.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        cur.execute("SELECT id, nome, email FROM usuarios WHERE email = ?", (email,))
        usuario = cur.fetchone()

        if not usuario:
            logger.warning(f"Tentativa de reset de senha para e-mail não encontrado: {email}")
            return False, "E-mail não encontrado."

        # Gera o token de reset e define a expiração (1 hora)
        token = generate_reset_token(email) # Usa a função de security
        expires_at = datetime.now() + timedelta(hours=1)

        # Salva o token e a expiração no banco de dados
        cur.execute("UPDATE usuarios SET reset_password_token = ?, reset_password_expires = ? WHERE id = ?",
                    (token, expires_at, usuario['id']))
        conn.commit()

        # Envia o e-mail de redefinição de senha
        # CORRIGIDO: Chama a função com o nome correto
        enviado = enviar_email_recuperacao_senha(usuario['email'], usuario['nome'], token)

        if enviado:
            logger.info(f"E-mail de reset de senha enviado para {email}")
            return True, "Um link para redefinir sua senha foi enviado para seu e-mail."
        else:
            logger.error(f"Falha ao enviar e-mail de reset de senha para {email}")
            return False, "Erro ao enviar e-mail de redefinição de senha. Tente novamente mais tarde."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao solicitar reset de senha para {email}: {e}", exc_info=True)
        return False, f"Erro interno ao solicitar reset de senha: {e}"
    finally:
        if conn:
            conn.close()

def validar_token_reset(token: str):
    """
    Verifica se um token de redefinição de senha é válido e não expirou.
    Retorna o e-mail associado ao token se válido, None caso contrário.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Busca o usuário pelo token
        cur.execute("SELECT email, reset_password_expires FROM usuarios WHERE reset_password_token = ?", (token,))
        usuario = cur.fetchone()

        if not usuario:
            return None # Token não encontrado

        # Verifica a expiração do token
        if usuario['reset_password_expires'] and usuario['reset_password_expires'] > datetime.now():
            # Token válido e não expirado
            return usuario['email']
        else:
            # Token expirado ou sem data de expiração
            logger.warning(f"Tentativa de usar token de reset expirado ou inválido para e-mail: {usuario['email']}")
            return None

    except Exception as e:
        logger.error(f"Erro ao validar token de reset: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def redefinir_senha_com_token(token: str, nova_senha: str):
    """
    Redefine a senha de um usuário usando um token válido.
    """
    conn = None
    try:
        email = validar_token_reset(token)
        if not email:
            return False, "Token de redefinição de senha inválido ou expirado."

        # Importa redefinir_senha aqui para evitar importação circular
        from .user import redefinir_senha

        sucesso, mensagem = redefinir_senha(email, nova_senha)

        if sucesso:
            conn = conectar_db()
            cur = conn.cursor()
            # Limpa o token de reset após o uso
            cur.execute("UPDATE usuarios SET reset_password_token = NULL, reset_password_expires = NULL WHERE email = ?", (email,))
            conn.commit()
            logger.info(f"Senha redefinida com sucesso para {email} usando token.")
            return True, "Senha redefinida com sucesso. Você já pode fazer login."
        else:
            return False, f"Erro ao redefinir senha: {mensagem}"

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao redefinir senha com token: {e}", exc_info=True)
        return False, f"Erro interno ao redefinir senha: {e}"
    finally:
        if conn:
            conn.close()

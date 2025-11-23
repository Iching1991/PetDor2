# PETdor2/auth/user.py
import logging
from datetime import datetime
import os
from database.connection import conectar_db
from .security import hash_password, generate_email_token, verify_email_token, verify_password
from utils.email_sender import enviar_email_confirmacao
import uuid
import streamlit as st # Para exibir mensagens de erro

logger = logging.getLogger(__name__)

def criar_tabelas_se_nao_existir():
    # Esta função não é mais necessária se migrar_banco_completo() for usada no app principal
    # Mas se for mantida, deve usar a sintaxe PostgreSQL
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # Exemplo de query PostgreSQL
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT NOT NULL DEFAULT 'Brasil',
                email_confirm_token TEXT UNIQUE,
                email_confirmado BOOLEAN NOT NULL DEFAULT FALSE,
                ativo BOOLEAN NOT NULL DEFAULT TRUE,
                data_cadastro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                reset_password_token TEXT UNIQUE,
                reset_password_expires TIMESTAMPTZ
            );
        """)
        conn.commit()
        logger.info("Tabela 'usuarios' verificada/criada via user.py (se chamada).")
        return True
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao criar tabelas em user.py: {e}", exc_info=True)
        return False
    finally:
        if conn:
            conn.close()

def cadastrar_usuario(nome, email, senha, tipo_usuario="Tutor", pais="Brasil"):
    """
    Cadastra um novo usuário no banco de dados.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Verificar se o e-mail já existe
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            return False, "Erro ao cadastrar usuário: Este e-mail já está em uso."

        senha_hash = hash_password(senha)
        email_token = generate_email_token(email)

        cur.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
            (nome, email, senha_hash, tipo_usuario, pais, email_token)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        logger.info(f"Usuário {email} cadastrado com sucesso com ID {user_id}.")

        # Enviar e-mail de confirmação
        confirm_link = f"{os.getenv('STREAMLIT_APP_URL')}?action=confirm_email&token={email_token}"
        email_enviado, email_msg = enviar_email_confirmacao(email, nome, confirm_link)

        if email_enviado:
            logger.info(f"E-mail de confirmação enviado para {email}.")
            return True, "Cadastro realizado com sucesso! Verifique seu e-mail para confirmar sua conta."
        else:
            logger.error(f"Falha ao enviar e-mail de confirmação para {email}: {email_msg}")
            return True, "Cadastro realizado com sucesso, mas houve um problema ao enviar o e-mail de confirmação. Por favor, tente novamente mais tarde."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao cadastrar usuário {email}: {e}", exc_info=True)
        return False, f"Erro ao cadastrar usuário: {e}"
    finally:
        if conn:
            conn.close()

def verificar_credenciais(email, senha):
    """
    Verifica as credenciais do usuário.
    Retorna (True, dados_usuario) se as credenciais forem válidas, (False, mensagem_erro) caso contrário.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor(cursor_factory=RealDictCursor) # Usar RealDictCursor para retornar dicionários

        cur.execute("SELECT id, nome, email, senha_hash, email_confirmado, ativo, tipo_usuario FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "E-mail ou senha incorretos."

        if not verify_password(senha, usuario['senha_hash']):
            return False, "E-mail ou senha incorretos."

        if not usuario['email_confirmado']:
            return False, "Sua conta ainda não foi confirmada. Por favor, verifique seu e-mail."

        if not usuario['ativo']:
            return False, "Sua conta está inativa. Por favor, contate o suporte."

        logger.info(f"Login bem-sucedido para o usuário {email}.")
        return True, usuario # Retorna o dicionário completo do usuário

    except Exception as e:
        logger.error(f"Erro ao verificar credenciais para {email}: {e}", exc_info=True)
        return False, f"Erro interno ao verificar credenciais: {e}"
    finally:
        if conn:
            conn.close()

def buscar_usuario_por_email(email):
    """
    Busca um usuário pelo e-mail.
    Retorna os dados do usuário como um dicionário ou None.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id, nome, email, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()
        return usuario
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por e-mail {email}: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

def confirmar_email(token):
    """
    Confirma o e-mail de um usuário usando o token fornecido.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # 1. Verificar o token
        email_do_token = verify_email_token(token)
        if not email_do_token:
            return False, "Token de confirmação inválido ou expirado."

        # 2. Atualizar status de confirmação no banco de dados
        cur.execute(
            "UPDATE usuarios SET email_confirmado = TRUE, email_confirm_token = NULL WHERE email = %s AND email_confirm_token = %s",
            (email_do_token, token)
        )
        if cur.rowcount == 0:
            return False, "Token de confirmação inválido ou já utilizado."

        conn.commit()
        logger.info(f"E-mail {email_do_token} confirmado com sucesso.")
        return True, "Seu e-mail foi confirmado com sucesso! Você já pode fazer login."

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao confirmar e-mail com token {token}: {e}", exc_info=True)
        return False, f"Erro interno ao confirmar e-mail: {e}"
    finally:
        if conn:
            conn.close()

def atualizar_status_usuario(user_id, ativo):
    """Atualiza o status ativo/inativo de um usuário."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET ativo = %s WHERE id = %s", (ativo, user_id))
        conn.commit()
        logger.info(f"Status do usuário ID {user_id} atualizado para ativo={ativo}")
        return True, "Status atualizado com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao atualizar status do usuário ID {user_id}: {e}", exc_info=True)
        return False, f"Erro ao atualizar status: {e}"
    finally:
        if conn:
            conn.close()

def atualizar_tipo_usuario(user_id, tipo_usuario):
    """Atualiza o tipo de usuário."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET tipo_usuario = %s WHERE id = %s", (tipo_usuario, user_id))
        conn.commit()
        logger.info(f"Tipo do usuário ID {user_id} atualizado para {tipo_usuario}")
        return True, "Tipo de usuário atualizado com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao atualizar tipo do usuário ID {user_id}: {e}", exc_info=True)
        return False, f"Erro ao atualizar tipo de usuário: {e}"
    finally:
        if conn:
            conn.close()

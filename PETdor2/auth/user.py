# PETdor2/auth/user.py
import logging
from datetime import datetime
import os
from database.connection import conectar_db
from auth.security import hash_password, generate_email_token, verify_email_token, verify_password
from utils.email_sender import enviar_email_confirmacao 
import uuid
import streamlit as st # Para exibir mensagens de erro

logger = logging.getLogger(__name__)

def criar_tabelas_se_nao_existir():
    """Cria a tabela de usuários se não existir (para SQLite local ou como fallback)."""
    conn = conectar_db()
    cur = conn.cursor()
    # Nota: A lógica de criação de tabelas aqui ainda está dividida por DB_HOST.
    # Como estamos forçando SQLite, a parte do PostgreSQL não será executada.
    # Para o SQLite, os tipos de dados e defaults estão corretos.
    # A verificação de os.getenv("DB_HOST") é para o caso de um dia você voltar a usar Supabase.
    # Por enquanto, o conectar_db() sempre retorna uma conexão SQLite.
    if os.getenv("DB_HOST"): # Se estivesse no Supabase (PostgreSQL)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id BIGSERIAL PRIMARY KEY,
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
    else: # Para SQLite local (se ainda estiver usando)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT NOT NULL DEFAULT 'Brasil',
                email_confirm_token TEXT UNIQUE,
                email_confirmado BOOLEAN NOT NULL DEFAULT FALSE,
                ativo BOOLEAN NOT NULL DEFAULT TRUE,
                data_cadastro TEXT NOT NULL DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now')),
                reset_password_token TEXT UNIQUE,
                reset_password_expires TEXT
            );
        """)
    conn.commit()
    conn.close()

def cadastrar_usuario(nome, email, senha, tipo_usuario="Tutor", pais="Brasil"):
    """Cadastra um novo usuário no banco de dados."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        # Verificar se o e-mail já existe
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            return False, "Este e-mail já está cadastrado."

        senha_hash = hash_password(senha)
        email_confirm_token = generate_email_token(email)

        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute(
            """
            INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token)
        )
        conn.commit()
        logger.info(f"Usuário {email} cadastrado com sucesso.")

        # Enviar e-mail de confirmação
        confirm_link = f"{os.getenv('STREAMLIT_APP_URL')}?action=confirm_email&token={email_confirm_token}"
        email_enviado, email_msg = enviar_email_confirmacao(email, nome, confirm_link)

        if email_enviado:
            return True, "Cadastro realizado com sucesso! Um e-mail de confirmação foi enviado."
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
    """Verifica as credenciais do usuário e retorna os dados do usuário se forem válidas."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute("SELECT id, nome, email, senha_hash, tipo_usuario, email_confirmado, ativo FROM usuarios WHERE email = %s", (email,))
        usuario = cur.fetchone()

        if usuario:
            user_id, nome, email_db, senha_hash, tipo_usuario, email_confirmado, ativo = usuario
            if not ativo:
                return False, "Sua conta está desativada. Por favor, contate o suporte."
            if not email_confirmado:
                return False, "Por favor, confirme seu e-mail antes de fazer login."
            if verify_password(senha, senha_hash):
                logger.info(f"Login bem-sucedido para {email}.")
                return True, {'id': user_id, 'nome': nome, 'email': email_db, 'tipo_usuario': tipo_usuario}
            else:
                logger.warning(f"Tentativa de login falhou para {email}: senha incorreta.")
                return False, "E-mail ou senha incorretos."
        else:
            logger.warning(f"Tentativa de login falhou para {email}: e-mail não encontrado.")
            return False, "E-mail ou senha incorretos."
    except Exception as e:
        logger.error(f"Erro ao verificar credenciais para {email}: {e}", exc_info=True)
        return False, f"Erro interno ao verificar credenciais: {e}"
    finally:
        if conn:
            conn.close()

def buscar_usuario_por_email(email):
    """Busca um usuário pelo e-mail."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # CORREÇÃO: Usar %s para PostgreSQL
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
    """Confirma o e-mail de um usuário usando o token."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute("SELECT id, email_confirmado FROM usuarios WHERE email_confirm_token = %s", (token,))
        usuario = cur.fetchone()

        if not usuario:
            return False, "Token de confirmação inválido ou expirado."

        user_id, email_confirmado = usuario
        if email_confirmado:
            return False, "Seu e-mail já foi confirmado."

        # Atualizar status de confirmação e invalidar token
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute(
            "UPDATE usuarios SET email_confirmado = TRUE, email_confirm_token = NULL WHERE id = %s",
            (user_id,)
        )
        conn.commit()
        logger.info(f"E-mail do usuário ID {user_id} confirmado com sucesso.")
        return True, "Seu e-mail foi confirmado com sucesso!"

    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Erro ao confirmar e-mail com token {token}: {e}", exc_info=True)
        return False, f"Erro ao confirmar e-mail: {e}"
    finally:
        if conn:
            conn.close()

def redefinir_senha_direta(email, nova_senha):
    """Redefine a senha de um usuário diretamente (sem token, para uso interno ou admin)."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        senha_hash = hash_password(nova_senha)
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute("UPDATE usuarios SET senha_hash = %s WHERE email = %s", (senha_hash, email))
        conn.commit()
        return True, "Senha redefinida com sucesso."
    except Exception as e:
        if conn:
            conn.rollback()
        return False, f"Erro ao redefinir senha: {e}"
    finally:
        if conn:
            conn.close()

def buscar_todos_usuarios():
    """Retorna todos os usuários (para fins administrativos)."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor() # Pode usar RealDictCursor se preferir dicionários
        cur.execute("SELECT id, nome, email, tipo_usuario, pais, email_confirmado, ativo, data_cadastro FROM usuarios ORDER BY data_cadastro DESC")
        usuarios = cur.fetchall()
        return usuarios
    except Exception as e:
        logger.error(f"Erro ao buscar todos os usuários: {e}", exc_info=True)
        return []
    finally:
        if conn:
            conn.close()

def atualizar_status_usuario(user_id, ativo):
    """Ativa ou desativa um usuário."""
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        # CORREÇÃO: Usar %s para PostgreSQL
        cur.execute("UPDATE usuarios SET ativo = %s WHERE id = %s", (ativo, user_id)) # PostgreSQL usa TRUE/FALSE
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
        # CORREÇÃO: Usar %s para PostgreSQL
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

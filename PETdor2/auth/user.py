# PETdor2/auth/user.py

import logging
import os
from datetime import datetime

from PETdor2.database.connection import conectar_db
from PETdor2.auth.security import (
    hash_password,
    verify_password,
    generate_email_token,
)
from PETdor2.utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)

USING_POSTGRES = bool(os.getenv("DB_HOST"))


# ==========================================================
# Placeholder dinâmico (%s para PG / ? para SQLite)
# ==========================================================
def placeholder():
    return "%s" if USING_POSTGRES else "?"


# ==========================================================
# Criar tabela se não existir
# ==========================================================
def criar_tabelas_se_nao_existir():
    conn = conectar_db()
    cur = conn.cursor()

    if USING_POSTGRES:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id BIGSERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT DEFAULT 'Brasil',

                email_confirm_token TEXT UNIQUE,
                email_confirmado BOOLEAN NOT NULL DEFAULT FALSE,

                reset_password_token TEXT,
                reset_password_expires TIMESTAMPTZ,

                ativo BOOLEAN NOT NULL DEFAULT TRUE,
                criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
    else:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
                pais TEXT DEFAULT 'Brasil',

                email_confirm_token TEXT,
                email_confirmado INTEGER DEFAULT 0,

                reset_password_token TEXT,
                reset_password_expires TIMESTAMP,

                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    conn.commit()
    conn.close()


# ==========================================================
# Cadastro de usuário com token JWT de confirmação
# ==========================================================
def cadastrar_usuario(nome, email, senha, tipo_usuario="Tutor", pais="Brasil") -> tuple:
    conn = None
    email = email.lower()

    try:
        conn = conectar_db()
        cur = conn.cursor()

        senha_hash = hash_password(senha)
        token = generate_email_token(email)

        sql = f"""
            INSERT INTO usuarios (
                nome, email, senha_hash, tipo_usuario, pais,
                email_confirm_token, email_confirmado
            )
            VALUES ({placeholder()}, {placeholder()}, {placeholder()},
                    {placeholder()}, {placeholder()}, {placeholder()}, 0)
        """

        cur.execute(sql, (nome, email, senha_hash, tipo_usuario, pais, token))
        conn.commit()

        # Envia e-mail de confirmação
        if not enviar_email_confirmacao(email, nome, token):
            logger.error("Falha ao enviar e-mail de confirmação.")
            return True, "Conta criada, mas não foi possível enviar o e-mail de confirmação."

        return True, "Cadastro concluído! Verifique seu e-mail para ativar sua conta."

    except Exception as e:
        logger.error("Erro em cadastrar_usuario", exc_info=True)
        if conn:
            conn.rollback()

        if "UNIQUE" in str(e) or "duplicate" in str(e):
            return False, "Este e-mail já está cadastrado."

        return False, "Erro interno ao criar conta."

    finally:
        if conn:
            conn.close()


# ==========================================================
# Login / Verificação de credenciais
# ==========================================================
def verificar_credenciais(email, senha):
    conn = None
    email = email.lower()

    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql = f"SELECT * FROM usuarios WHERE email = {placeholder()}"
        cur.execute(sql, (email,))
        row = cur.fetchone()

        if not row:
            return False, "E-mail ou senha incorretos."

        # Adaptar para SQLite Row ou dict (PostgreSQL)
        is_dict = isinstance(row, dict)
        get = lambda k, idx: row[k] if is_dict else row[idx]

        confirmado = get("email_confirmado", 6)
        senha_hash = get("senha_hash", 3)
        ativo = get("ativo", 9)

        if not confirmado:
            return False, "Confirme seu e-mail antes de entrar."

        if not ativo:
            return False, "Conta desativada."

        if not verify_password(senha, senha_hash):
            return False, "E-mail ou senha incorretos."

        return True, row

    except Exception as e:
        logger.error("Erro em verificar_credenciais", exc_info=True)
        return False, "Erro interno no login."

    finally:
        if conn:
            conn.close()


# ==========================================================
# Buscar usuário por e-mail
# ==========================================================
def buscar_usuario_por_email(email):
    conn = conectar_db()
    cur = conn.cursor()

    sql = f"SELECT * FROM usuarios WHERE email = {placeholder()}"
    cur.execute(sql, (email.lower(),))
    row = cur.fetchone()

    conn.close()
    return row


# ==========================================================
# Confirmação de e-mail via JWT
# ==========================================================
def confirmar_email(token):
    from PETdor2.auth.email_confirmation import confirmar_email as confirmar_fn
    return confirmar_fn(token)


# ==========================================================
# Redefinir senha
# ==========================================================
def redefinir_senha(email, nova_senha):
    conn = None
    email = email.lower()

    try:
        conn = conectar_db()
        cur = conn.cursor()

        senha_hash = hash_password(nova_senha)

        sql = f"UPDATE usuarios SET senha_hash = {placeholder()} WHERE email = {placeholder()}"
        cur.execute(sql, (senha_hash, email))

        conn.commit()
        return True, "Senha atualizada com sucesso."

    except Exception:
        logger.error("Erro em redefinir_senha", exc_info=True)
        if conn:
            conn.rollback()
        return False, "Erro interno ao redefinir senha."

    finally:
        if conn:
            conn.close()


# ==========================================================
# Administração — listar usuários
# ==========================================================
def buscar_todos_usuarios():
    conn = conectar_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, nome, email, tipo_usuario, pais,
               email_confirmado, ativo, criado_em
        FROM usuarios
        ORDER BY criado_em DESC
    """)

    data = cur.fetchall()
    conn.close()
    return data


# ==========================================================
# Administração — ativar/desativar
# ==========================================================
def atualizar_status_usuario(user_id, ativo):
    conn = conectar_db()
    cur = conn.cursor()

    sql = f"UPDATE usuarios SET ativo = {placeholder()} WHERE id = {placeholder()}"
    cur.execute(sql, (1 if ativo else 0, user_id))

    conn.commit()
    conn.close()
    return True, "Status atualizado."


# ==========================================================
# Administração — atualizar tipo (Tutor / Veterinário)
# ==========================================================
def atualizar_tipo_usuario(user_id, tipo_usuario):
    conn = conectar_db()
    cur = conn.cursor()

    sql = f"UPDATE usuarios SET tipo_usuario = {placeholder()} WHERE id = {placeholder()}"
    cur.execute(sql, (tipo_usuario, user_id))

    conn.commit()
    conn.close()
    return True, "Tipo atualizado."

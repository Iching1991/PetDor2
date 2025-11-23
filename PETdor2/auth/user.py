# PETdor2/auth/user.py
import logging
import os
from datetime import datetime

from PETdor2.database.connection import conectar_db
from PETdor2.auth.security import hash_password, verify_password, generate_email_token
from PETdor2.utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)
USING_POSTGRES = bool(os.getenv("DB_HOST"))


def placeholder():
    return "%s" if USING_POSTGRES else "?"


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


def cadastrar_usuario(nome, email, senha, tipo_usuario="Tutor", pais="Brasil") -> tuple[bool, str]:
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        senha_hash = hash_password(senha)
        token = generate_email_token(email)  # JWT token for confirmation

        sql = f"""
            INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token, email_confirmado)
            VALUES ({placeholder()}, {placeholder()}, {placeholder()}, {placeholder()}, {placeholder()}, {placeholder()}, {placeholder()})
        """
        cur.execute(sql, (nome, email.lower(), senha_hash, tipo_usuario, pais, token, 0))
        conn.commit()

        enviado = enviar_email_confirmacao(email, nome, token)
        if not enviado:
            logger.error("Falha ao enviar e-mail de confirmação.")
            return True, "Cadastro feito, mas falha ao enviar e-mail de confirmação."

        return True, "Cadastro realizado com sucesso! Verifique o seu e-mail para confirmar a conta."
    except Exception as e:
        logger.error("Erro em cadastrar_usuario", exc_info=True)
        if conn:
            conn.rollback()
        msg = str(e)
        if "UNIQUE" in msg or "duplicate" in msg:
            return False, "Este e-mail já está cadastrado."
        return False, "Erro interno ao cadastrar usuário."
    finally:
        if conn:
            conn.close()


def verificar_credenciais(email, senha) -> tuple[bool, str | dict]:
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        sql = f"SELECT * FROM usuarios WHERE email = {placeholder()}"
        cur.execute(sql, (email.lower(),))
        usuario = cur.fetchone()
        if not usuario:
            return False, "E-mail ou senha incorretos."

        email_confirmado = usuario["email_confirmado"] if isinstance(usuario, dict) or hasattr(usuario, "keys") else usuario[ "email_confirmado" ] if isinstance(usuario, (list,tuple)) and len(usuario)>0 else usuario.get("email_confirmado", 0) if hasattr(usuario, "get") else usuario[0]
        # Simplify access: handle sqlite Row (dict-like) and tuple
        senha_hash = usuario["senha_hash"] if isinstance(usuario, dict) or hasattr(usuario, "keys") else usuario[3]

        if (email_confirmado in (0, False, "0", None)):
            return False, "Por favor confirme seu e-mail antes de entrar."

        if not verify_password(senha, senha_hash):
            return False, "E-mail ou senha incorretos."

        return True, usuario
    except Exception as e:
        logger.error("Erro em verificar_credenciais", exc_info=True)
        return False, "Erro interno ao verificar credenciais."
    finally:
        if conn:
            conn.close()


def buscar_usuario_por_email(email):
    conn = conectar_db()
    cur = conn.cursor()
    sql = f"SELECT * FROM usuarios WHERE email = {placeholder()}"
    cur.execute(sql, (email.lower(),))
    return cur.fetchone()


def confirmar_email(token: str) -> tuple[bool, str]:
    """
    Confirma e-mail usando token JWT (verificado por email_confirmation module).
    This simply delegates to email_confirmation.confirmar_email in practice.
    """
    from PETdor2.auth.email_confirmation import confirmar_email as confirmar_email_fn
    return confirmar_email_fn(token)


def redefinir_senha(email: str, nova_senha: str) -> tuple[bool, str]:
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()
        senha_hash = hash_password(nova_senha)
        sql = f"UPDATE usuarios SET senha_hash = {placeholder()} WHERE email = {placeholder()}"
        cur.execute(sql, (senha_hash, email.lower()))
        conn.commit()
        return True, "Senha redefinida com sucesso."
    except Exception as e:
        logger.error("Erro em redefinir_senha", exc_info=True)
        if conn:
            conn.rollback()
        return False, "Erro interno ao redefinir senha."
    finally:
        if conn:
            conn.close()


def buscar_todos_usuarios():
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, email, tipo_usuario, pais, email_confirmado, ativo, criado_em
        FROM usuarios
        ORDER BY criado_em DESC
    """)
    data = cur.fetchall()
    conn.close()
    return data


def atualizar_status_usuario(user_id, ativo):
    conn = conectar_db()
    cur = conn.cursor()
    sql = f"UPDATE usuarios SET ativo = {placeholder()} WHERE id = {placeholder()}"
    cur.execute(sql, (1 if ativo else 0, user_id))
    conn.commit()
    conn.close()
    return True, "Status atualizado."


def atualizar_tipo_usuario(user_id, tipo_usuario):
    conn = conectar_db()
    cur = conn.cursor()
    sql = f"UPDATE usuarios SET tipo_usuario = {placeholder()} WHERE id = {placeholder()}"
    cur.execute(sql, (tipo_usuario, user_id))
    conn.commit()
    conn.close()
    return True, "Tipo atualizado."

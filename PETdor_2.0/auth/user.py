# PetDor/auth/user.py
"""
Gerenciamento de usuários: cadastro, autenticação, atualização, confirmação de e-mail.
"""

import uuid
import bcrypt
import logging
from datetime import datetime
from database.connection import conectar_db
from utils.validators import validar_email, validar_senha
from utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)

# -------------------------
# Cadastrar usuário
# -------------------------
def cadastrar_usuario(nome: str, email: str, senha: str, confirmar: str,
                      tipo_usuario: str = "Tutor", pais: str = "Brasil"):
    try:
        nome = nome.strip()
        email = email.strip().lower()

        if not nome or not email or not senha:
            return False, "Preencha todos os campos obrigatórios."

        if senha != confirmar:
            return False, "As senhas não conferem."

        if not validar_email(email):
            return False, "E-mail inválido."

        # validação de senha (opcional — se quiser regras estritas)
        # if not validar_senha(senha):
        #     return False, "Senha não atende os requisitos de segurança."

        conn = conectar_db()
        cur = conn.cursor()

        # verifica duplicado
        cur.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cur.fetchone():
            conn.close()
            return False, "E-mail já cadastrado."

        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # gera token de confirmação
        token = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO usuarios (nome, email, senha_hash, tipo_usuario, pais, email_confirm_token, email_confirmado)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (nome, email, senha_hash, tipo_usuario, pais, token))

        conn.commit()
        user_id = cur.lastrowid
        conn.close()

        # tenta enviar e-mail de confirmação (não crítico)
        try:
            enviar_email_confirmacao(email, nome, token)
        except Exception as e:
            logger.warning(f"Falha ao enviar email de confirmação para {email}: {e}")

        return True, "Conta criada com sucesso. Verifique seu e-mail para confirmar."

    except Exception as e:
        logger.exception("Erro ao cadastrar usuário")
        return False, f"Erro ao criar conta: {e}"

# -------------------------
# Autenticar usuário
# -------------------------
def autenticar_usuario(email: str, senha: str):
    try:
        if not email or not senha:
            return False, "E-mail e senha são obrigatórios.", None

        email = email.strip().lower()
        conn = conectar_db()
        cur = conn.cursor()

        cur.execute("SELECT id, senha_hash, ativo, email_confirmado FROM usuarios WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()

        if not row:
            return False, "Usuário não encontrado.", None

        user_id, senha_hash, ativo, email_confirmado = row

        if not ativo:
            return False, "Conta desativada.", None

        # opcional: exigir confirmação de e-mail
        # if not email_confirmado:
        #     return False, "Confirme seu e-mail antes de entrar.", None

        if bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8")):
            return True, "Login efetuado com sucesso.", user_id
        else:
            return False, "E-mail ou senha incorretos.", None

    except Exception as e:
        logger.exception("Erro na autenticação")
        return False, "Erro ao autenticar.", None

# -------------------------
# Buscar usuário
# -------------------------
def buscar_usuario_por_id(user_id: int):
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, email, tipo_usuario, pais, email_confirmado, ativo FROM usuarios WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "tipo_usuario": row[3],
            "pais": row[4],
            "email_confirmado": bool(row[5]),
            "ativo": bool(row[6])
        }
    except Exception as e:
        logger.exception("Erro ao buscar usuário por id")
        return None

def buscar_usuario_por_email(email: str):
    try:
        email = email.strip().lower()
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, email, tipo_usuario, pais, email_confirmado, ativo FROM usuarios WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "tipo_usuario": row[3],
            "pais": row[4],
            "email_confirmado": bool(row[5]),
            "ativo": bool(row[6])
        }
    except Exception as e:
        logger.exception("Erro ao buscar usuário por email")
        return None

# -------------------------
# Atualizar usuário
# -------------------------
def atualizar_usuario(user_id: int, nome: str = None, email: str = None, tipo_usuario: str = None, pais: str = None):
    try:
        conn = conectar_db()
        cur = conn.cursor()
        updates = []
        params = []

        if nome:
            updates.append("nome = ?")
            params.append(nome.strip())
        if email:
            updates.append("email = ?")
            params.append(email.strip().lower())
        if tipo_usuario:
            updates.append("tipo_usuario = ?")
            params.append(tipo_usuario)
        if pais:
            updates.append("pais = ?")
            params.append(pais)

        if not updates:
            conn.close()
            return True

        params.append(user_id)
        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
        cur.execute(query, tuple(params))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.exception("Erro ao atualizar usuário")
        return False

# -------------------------
# Alterar senha (direto)
# -------------------------
def alterar_senha(user_id: int, nova_senha: str):
    try:
        senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (senha_hash, user_id))
        conn.commit()
        conn.close()
        return True, "Senha alterada com sucesso."
    except Exception as e:
        logger.exception("Erro ao alterar senha")
        return False, f"Erro ao alterar senha: {e}"

# -------------------------
# Deletar / desativar usuário
# -------------------------
def deletar_usuario(user_id: int):
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET ativo = 0 WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.exception("Erro ao desativar usuário")
        return False

# -------------------------
# Token de confirmação de e-mail
# -------------------------
def gerar_token_confirmacao_para_usuario(user_id: int):
    try:
        token = str(uuid.uuid4())
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET email_confirm_token = ? WHERE id = ?", (token, user_id))
        conn.commit()
        conn.close()
        return token
    except Exception as e:
        logger.exception("Erro ao gerar token de confirmação")
        return None

def confirmar_email(token: str):
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE email_confirm_token = ?", (token,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False
        user_id = row[0]
        cur.execute("UPDATE usuarios SET email_confirmado = 1, email_confirm_token = NULL WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.exception("Erro ao confirmar e-mail")
        return False

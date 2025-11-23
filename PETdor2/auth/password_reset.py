# PETdor2/auth/password_reset.py
import logging
import os
from datetime import datetime, timedelta

from PETdor2.database.connection import conectar_db
from PETdor2.utils.email_sender import enviar_email_reset_senha
from PETdor2.auth.security import generate_reset_token, verify_reset_token, hash_password

logger = logging.getLogger(__name__)
USING_POSTGRES = bool(os.getenv("DB_HOST"))


def solicitar_reset_senha(email: str) -> tuple[bool, str]:
    """
    Gera token JWT de reset, salva no DB e envia e-mail.
    Retorna (True,msg) sempre que possível para não vazar existência.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql_select = "SELECT id, nome, email FROM usuarios WHERE email = %s" if USING_POSTGRES else "SELECT id, nome, email FROM usuarios WHERE email = ?"
        cur.execute(sql_select, (email,))
        usuario = cur.fetchone()

        if not usuario:
            # Não revelar existência
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."

        usuario_id = usuario[0] if isinstance(usuario, (list, tuple)) else usuario["id"]
        nome = usuario[1] if isinstance(usuario, (list, tuple)) else usuario["nome"]
        email_db = usuario[2] if isinstance(usuario, (list, tuple)) else usuario["email"]

        token = generate_reset_token(email_db)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        sql_update = "UPDATE usuarios SET reset_password_token=%s, reset_password_expires=%s WHERE id=%s" if USING_POSTGRES else "UPDATE usuarios SET reset_password_token=?, reset_password_expires=? WHERE id=?"
        value_expires = expires_at if USING_POSTGRES else expires_at.strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(sql_update, (token, value_expires, usuario_id))
        conn.commit()

        enviado = enviar_email_reset_senha(email_db, nome, token)
        if enviado:
            return True, "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."
        else:
            return False, "Erro ao enviar e-mail de redefinição."
    except Exception as e:
        logger.error("Erro em solicitar_reset_senha", exc_info=True)
        return False, "Erro interno ao solicitar redefinição."
    finally:
        if conn:
            conn.close()


def validar_token_reset(token: str) -> str | None:
    """
    Verifica token JWT (via security) e também valida expiração registrada no banco.
    Retorna e-mail se válido, None caso contrário.
    """
    try:
        # Primeiro valida como JWT
        email = verify_reset_token(token)
        if not email:
            return None

        conn = conectar_db()
        cur = conn.cursor()
        sql = "SELECT email, reset_password_expires FROM usuarios WHERE reset_password_token = %s" if USING_POSTGRES else "SELECT email, reset_password_expires FROM usuarios WHERE reset_password_token = ?"
        cur.execute(sql, (token,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None

        email_db = row[0] if isinstance(row, (list, tuple)) else row["email"]
        expires = row[1] if isinstance(row, (list, tuple)) else row["reset_password_expires"]

        # Normalize expires to datetime
        if isinstance(expires, str):
            try:
                expires_dt = datetime.strptime(expires, "%Y-%m-%d %H:%M:%S")
            except Exception:
                # If can't parse, trust JWT expiry handled earlier
                return email_db
        else:
            expires_dt = expires

        if expires_dt < datetime.utcnow():
            return None

        return email_db
    except Exception as e:
        logger.error("Erro em validar_token_reset", exc_info=True)
        return None


def redefinir_senha_com_token(token: str, nova_senha: str) -> tuple[bool, str]:
    """
    Redefine senha se token válido; limpa token no DB.
    """
    conn = None
    try:
        email = validar_token_reset(token)
        if not email:
            return False, "Token inválido ou expirado."

        hashed = hash_password(nova_senha)

        conn = conectar_db()
        cur = conn.cursor()
        sql_update = "UPDATE usuarios SET senha_hash=%s, reset_password_token=NULL, reset_password_expires=NULL WHERE email=%s" if USING_POSTGRES else "UPDATE usuarios SET senha_hash=?, reset_password_token=NULL, reset_password_expires=NULL WHERE email=?"
        cur.execute(sql_update, (hashed, email))
        conn.commit()
        return True, "Senha redefinida com sucesso."
    except Exception as e:
        logger.error("Erro em redefinir_senha_com_token", exc_info=True)
        return False, "Erro interno ao redefinir senha."
    finally:
        if conn:
            conn.close()

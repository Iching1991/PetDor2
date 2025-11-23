# PETdor2/auth/email_confirmation.py
import logging
import os

from PETdor2.database.connection import conectar_db
from PETdor2.auth.security import verify_email_token, generate_email_token
from PETdor2.utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)
USING_POSTGRES = bool(os.getenv("DB_HOST"))


# ==========================================================
# Utilitário para pegar valor independentemente de dict/tuple
# ==========================================================
def get(row, key_or_index):
    """Permite acessar row['campo'] ou row[index] de forma segura."""
    if row is None:
        return None
    if isinstance(row, dict):
        return row.get(key_or_index)
    if isinstance(row, (list, tuple)):
        return row[key_or_index]
    return None


# ==========================================================
# CONFIRMAÇÃO DE EMAIL
# ==========================================================
def confirmar_email(token: str) -> tuple[bool, str]:
    """
    Valida token JWT e confirma o e-mail do usuário.
    Retorna (True, msg) ou (False, msg).
    """
    conn = None
    try:
        email = verify_email_token(token)
        if not email:
            return False, "Token inválido ou expirado."

        conn = conectar_db()
        cur = conn.cursor()

        sql = (
            "SELECT id FROM usuarios WHERE email = %s AND email_confirm_token = %s AND email_confirmado = FALSE"
            if USING_POSTGRES
            else "SELECT id FROM usuarios WHERE email = ? AND email_confirm_token = ? AND email_confirmado = 0"
        )
        cur.execute(sql, (email, token))
        row = cur.fetchone()

        if not row:
            return False, "Token já utilizado ou não corresponde a nenhum usuário."

        usuario_id = get(row, "id") if isinstance(row, dict) else row[0]

        sql_upd = (
            "UPDATE usuarios SET email_confirmado = TRUE, email_confirm_token = NULL WHERE id = %s"
            if USING_POSTGRES
            else "UPDATE usuarios SET email_confirmado = 1, email_confirm_token = NULL WHERE id = ?"
        )
        cur.execute(sql_upd, (usuario_id,))
        conn.commit()

        return True, "E-mail confirmado com sucesso."

    except Exception:
        logger.error("Erro em confirmar_email", exc_info=True)
        return False, "Erro interno ao confirmar e-mail."
    finally:
        if conn:
            conn.close()


# ==========================================================
# REENVIAR EMAIL DE CONFIRMAÇÃO
# ==========================================================
def reenviar_email_confirmacao(email: str) -> tuple[bool, str]:
    """
    Reenvia novo token para confirmação de e-mail.
    Nunca revela se o e-mail existe ou não.
    """
    conn = None
    try:
        conn = conectar_db()
        cur = conn.cursor()

        sql = (
            "SELECT id, nome, email_confirm_token, email_confirmado FROM usuarios WHERE email = %s"
            if USING_POSTGRES
            else "SELECT id, nome, email_confirm_token, email_confirmado FROM usuarios WHERE email = ?"
        )
        cur.execute(sql, (email.lower(),))
        row = cur.fetchone()

        # ✔ Não revela se existe ou não
        if not row:
            return True, "Se o e-mail estiver cadastrado, você receberá um link."

        usuario_id = get(row, "id") if isinstance(row, dict) else row[0]
        nome = get(row, "nome") if isinstance(row, dict) else row[1]
        confirmado = get(row, "email_confirmado") if isinstance(row, dict) else row[3]

        if confirmado in (True, 1):
            return True, "Conta já confirmada."

        # Gerar novo token JWT
        novo_token = generate_email_token(email)

        sql_upd = (
            "UPDATE usuarios SET email_confirm_token = %s WHERE id = %s"
            if USING_POSTGRES
            else "UPDATE usuarios SET email_confirm_token = ? WHERE id = ?"
        )
        cur.execute(sql_upd, (novo_token, usuario_id))
        conn.commit()

        envio_ok = enviar_email_confirmacao(email, nome, novo_token)

        if envio_ok:
            return True, "E-mail de confirmação reenviado."
        else:
            return False, "Erro ao enviar e-mail de confirmação."

    except Exception:
        logger.error("Erro em reenviar_email_confirmacao", exc_info=True)
        return False, "Erro interno ao reenviar e-mail."
    finally:
        if conn:
            conn.close()

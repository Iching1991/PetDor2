# PETdor2/auth/email_confirmation.py
import logging
import os
from PETdor2.database.connection import conectar_db
from PETdor2.auth.security import verify_email_token, generate_email_token
from PETdor2.utils.email_sender import enviar_email_confirmacao

logger = logging.getLogger(__name__)
USING_POSTGRES = bool(os.getenv("DB_HOST"))


def confirmar_email(token: str) -> tuple[bool, str]:
    """
    Confirma o e-mail do usuário validando o token JWT.
    Retorna (True, msg) ou (False, msg).
    """
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
            conn.close()
            return False, "Token não corresponde a nenhum usuário ou já foi utilizado."

        usuario_id = row[0] if isinstance(row, (list, tuple)) else row["id"]

        sql_upd = (
            "UPDATE usuarios SET email_confirmado = TRUE, email_confirm_token = NULL WHERE id = %s"
            if USING_POSTGRES
            else "UPDATE usuarios SET email_confirmado = 1, email_confirm_token = NULL WHERE id = ?"
        )
        cur.execute(sql_upd, (usuario_id,))
        conn.commit()
        conn.close()
        return True, "E-mail confirmado com sucesso."
    except Exception as e:
        logger.error("Erro em confirmar_email", exc_info=True)
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        return False, "Erro interno ao confirmar e-mail."


def reenviar_email_confirmacao(email: str) -> tuple[bool, str]:
    """
    Gera um novo token JWT (ou usa o existente se preferir) e reenvia o e-mail.
    Retorna (True,msg) pra não vazar existência do e-mail.
    """
    try:
        conn = conectar_db()
        cur = conn.cursor()
        sql = "SELECT id, nome, email_confirm_token, email_confirmado FROM usuarios WHERE email = %s" if USING_POSTGRES else "SELECT id, nome, email_confirm_token, email_confirmado FROM usuarios WHERE email = ?"
        cur.execute(sql, (email.lower(),))
        row = cur.fetchone()
        if not row:
            # Não revela se o e-mail existe
            if conn:
                conn.close()
            return True, "Se o e-mail estiver cadastrado, você receberá um link de confirmação."

        usuario_id = row[0] if isinstance(row, (list, tuple)) else row["id"]
        nome = row[1] if isinstance(row, (list, tuple)) else row["nome"]
        token_existente = row[2] if isinstance(row, (list, tuple)) else row["email_confirm_token"]
        confirmado = row[3] if isinstance(row, (list, tuple)) else row["email_confirmado"]

        if confirmado in (1, True):
            conn.close()
            return True, "Conta já confirmada."

        # Gere um novo token JWT e atualize no banco
        novo_token = generate_email_token(email)
        sql_upd = "UPDATE usuarios SET email_confirm_token = %s WHERE id = %s" if USING_POSTGRES else "UPDATE usuarios SET email_confirm_token = ? WHERE id = ?"
        cur.execute(sql_upd, (novo_token, usuario_id))
        conn.commit()
        conn.close()

        enviado = enviar_email_confirmacao(email, nome, novo_token)
        if enviado:
            return True, "E-mail de confirmação reenviado."
        else:
            return False, "Falha ao enviar e-mail de confirmação."
    except Exception as e:
        logger.error("Erro em reenviar_email_confirmacao", exc_info=True)
        try:
            if conn:
                conn.close()
        except Exception:
            pass
        return False, "Erro interno ao reenviar e-mail."

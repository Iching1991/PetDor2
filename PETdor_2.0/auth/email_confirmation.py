"""
Módulo de confirmação de e-mail do PETDor
"""
import logging
from database.connection import conectar_db
from utils.tokens import gerar_token_simples, validar_token_simples
from utils.email_sender import enviar_email

logger = logging.getLogger(__name__)


# ----------------------------------------------
# 1) Gerar token e enviar e-mail de confirmação
# ----------------------------------------------

def enviar_email_confirmacao(usuario_id, email, nome):
    """
    Gera um token, salva no banco e envia link de confirmação.
    """
    try:
        token = gerar_token_simples()

        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO email_confirmacoes (usuario_id, token)
            VALUES (?, ?)
        """, (usuario_id, token))

        conn.commit()
        conn.close()

        # link de verificação que será acessado por uma página Streamlit
        link = f"https://petdor.streamlit.app/confirmar_email?token={token}"

        assunto = "Confirme seu e-mail - PETDor"
        mensagem = f"""
Olá, {nome}!

Obrigado por se cadastrar no PETDor.

Para ativar sua conta, confirme seu e-mail clicando no link abaixo:

🔗 {link}

Se você não criou esta conta, apenas ignore este e-mail.

Equipe PETDor.
"""

        enviar_email(email, assunto, mensagem)
        return True

    except Exception as e:
        logger.error(f"Erro ao enviar email de confirmacao: {e}")
        return False


# ----------------------------------------------
# 2) Validar token e confirmar a conta
# ----------------------------------------------

def confirmar_email(token):
    """
    Valida o token e ativa a conta do usuário.
    """
    try:
        conn = conectar_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT usuario_id FROM email_confirmacoes
            WHERE token = ?
        """, (token,))
        row = cursor.fetchone()

        if not row:
            conn.close()
            return False, "Token inválido ou expirado."

        usuario_id = row[0]

        # valida formato do token (12 caracteres alfanuméricos)
        if not validar_token_simples(token):
            conn.close()
            return False, "Token inválido."

        # ativar usuário
        cursor.execute("""
            UPDATE usuarios
            SET ativo = 1
            WHERE id = ?
        """, (usuario_id,))

        # remover token da tabela
        cursor.execute("""
            DELETE FROM email_confirmacoes
            WHERE usuario_id = ?
        """, (usuario_id,))

        conn.commit()
        conn.close()
        return True, "E-mail confirmado com sucesso!"

    except Exception as e:
        logger.error(f"Erro ao confirmar o e-mail: {e}")
        return False, "Erro ao confirmar o e-mail."

# PETdor2/backend/auth/email_confirmation.py
"""
Módulo de confirmação de e-mail do PETDor.
Gerencia criação e validação de tokens, envio de e-mail e atualização do status no banco.
"""

import logging
from datetime import datetime
from typing import Tuple, Dict, Any

# Importações absolutas — evita import circular
from backend.database.supabase_client import (
    supabase_table_update,
    supabase_table_select,
)
from backend.auth.security import (
    gerar_token_confirmacao_email,
    validar_token_confirmacao_email,
)
from backend.auth.user import (
    marcar_email_como_confirmado,
    buscar_usuario_por_email,
)

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"


# ============================================================
# 1) GERAR TOKEN E ENVIAR E-MAIL DE CONFIRMAÇÃO
# ============================================================
def enviar_email_confirmacao(email: str, nome: str, user_id: int) -> Tuple[bool, str]:
    """
    Gera token JWT, salva no banco e envia link de confirmação para o usuário.
    """

    # Import tardio evita import circular com utils.email_sender
    from backend.utils.email_sender import enviar_email_confirmacao_generico
    from backend.utils.config import STREAMLIT_APP_URL

    try:
        # Gera token JWT único
        token = gerar_token_confirmacao_email(email=email, user_id=user_id)

        # Salva token no Supabase
        dados_update = {
            "email_confirm_token": token,
            "atualizado_em": datetime.now().isoformat(),
        }

        ok_update, msg_update = supabase_table_update(
            TABELA_USUARIOS, dados_update, {"id": user_id}
        )

        if not ok_update:
            logger.error(
                f"❌ Falha ao salvar token de confirmação para usuário {user_id}: {msg_update}"
            )
            return False, "Erro ao gerar link de confirmação."

        # Monta link de confirmação
        link = f"{STREAMLIT_APP_URL}?action=confirm_email&token={token}"

        assunto = "Confirme seu e-mail - PETDor"

        corpo_html = f"""
        <html>
        <body>
            <p>Olá, {nome}!</p>
            <p>Obrigado por se cadastrar no PETDor.</p>
            <p>Para ativar sua conta, clique no link abaixo:</p>
            <p><a href="{link}">🔗 Confirmar meu E-mail</a></p>
            <br/>
            <p>Se você não criou esta conta, ignore este e-mail.</p>
        </body>
        </html>
        """

        corpo_texto = f"""
Olá, {nome}!

Obrigado por se cadastrar no PETDor.

Para ativar sua conta, acesse o link abaixo:

🔗 {link}

Se você não criou esta conta, apenas ignore este e-mail.
"""

        # Enviar e-mail
        ok_email, msg_email = enviar_email_confirmacao_generico(
            destinatario_email=email,
            assunto=assunto,
            corpo_html=corpo_html,
            corpo_texto=corpo_texto,
        )

        if not ok_email:
            logger.error(f"❌ Erro ao enviar e-mail de confirmação para {email}: {msg_email}")
            return False, "Falha ao enviar o e-mail de confirmação."

        logger.info(f"✅ E-mail de confirmação enviado para {email} (user_id={user_id})")
        return True, "E-mail de confirmação enviado com sucesso."

    except Exception as e:
        logger.exception(f"Erro interno ao enviar e-mail de confirmação: {e}")
        return False, "Erro interno ao enviar e-mail de confirmação."


# ============================================================
# 2) VALIDAR TOKEN DE CONFIRMAÇÃO
# ============================================================
def confirmar_email_com_token(token: str) -> Tuple[bool, str]:
    """
    Valida o token JWT e confirma o e-mail do usuário no banco.
    """

    try:
        payload, msg_validacao = validar_token_confirmacao_email(token)

        if not payload:
            return False, msg_validacao

        email = payload.get("email")
        user_id = payload.get("user_id")

        if not email or not user_id:
            return False, "Token inválido ou incompleto."

        # Busca usuário
        ok_user, usuario = buscar_usuario_por_email(email)

        if not ok_user or not usuario:
            return False, "Usuário não encontrado."

        # Verifica se token do banco é igual ao recebido
        if usuario.get("email_confirm_token") != token:
            return False, "Token inválido ou já utilizado."

        # Marca o e-mail como confirmado
        ok_marcar, msg_marcar = marcar_email_como_confirmado(email)

        if not ok_marcar:
            logger.error(f"❌ Erro ao confirmar e-mail {email}: {msg_marcar}")
            return False, "Erro ao confirmar e-mail."

        logger.info(f"✅ E-mail confirmado com sucesso: {email} (user_id={user_id})")
        return True, "E-mail confirmado com sucesso! Você já pode fazer login."

    except Exception as e:
        logger.exception(f"Erro interno ao confirmar e-mail com token: {e}")
        return False, "Erro interno ao confirmar e-mail."

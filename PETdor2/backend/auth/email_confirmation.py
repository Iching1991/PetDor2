# PetDor2/backend/auth/email_confirmation.py
"""
Módulo de confirmação de e-mail do PETDor
Usa JWT para tokens e Supabase para armazenamento.
"""

import logging
from datetime import datetime
from typing import Tuple

# Importações absolutas a partir de 'backend'
from backend.database.supabase_client import supabase_table_update, supabase_table_select
from backend.utils.email_sender import enviar_email_confirmacao_generico # Renomeado para evitar conflito
from .security import gerar_token_confirmacao_email, validar_token_confirmacao_email
from .user import marcar_email_como_confirmado, buscar_usuario_por_email # Importa a função de user

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"

# ----------------------------------------------
# 1) Gerar token JWT e enviar e-mail de confirmação
# ----------------------------------------------
def enviar_email_confirmacao(email: str, nome: str, user_id: int) -> Tuple[bool, str]:
    """
    Gera token JWT, salva no banco e envia link de confirmação.
    """
    try:
        # Gera token JWT
        token = gerar_token_confirmacao_email(email, user_id)

        # Salva o token no Supabase na tabela de usuários
        dados_update = {
            "email_confirm_token": token,
            "atualizado_em": datetime.now().isoformat()
        }

        ok_update, _ = supabase_table_update(
            TABELA_USUARIOS,
            dados_update,
            {"id": user_id}
        )

        if not ok_update:
            logger.error(f"Erro ao salvar token de confirmação para usuário {user_id}")
            return False, "Erro ao gerar link de confirmação."

        # Link de verificação para Streamlit
        # Assumimos que STREAMLIT_APP_URL está configurado em utils.config
        from backend.utils.config import STREAMLIT_APP_URL
        link = f"{STREAMLIT_APP_URL}?action=confirm_email&token={token}"

        assunto = "Confirme seu e-mail - PETDor"
        mensagem_html = f"""
        <html>
        <body>
            <p>Olá, {nome}!</p>
            <p>Obrigado por se cadastrar no PETDor.</p>
            <p>Para ativar sua conta, confirme seu e-mail clicando no link abaixo:</p>
            <p><a href="{link}">🔗 Confirmar meu E-mail</a></p>
            <p>Se você não criou esta conta, apenas ignore este e-mail.</p>
            <p>Equipe PETDor.</p>
        </body>
        </html>
        """
        mensagem_texto = f"""
        Olá, {nome}!

        Obrigado por se cadastrar no PETDor.

        Para ativar sua conta, confirme seu e-mail clicando no link abaixo:

        🔗 {link}

        Se você não criou esta conta, apenas ignore este e-mail.

        Equipe PETDor.
        """

        # Envia e-mail usando a função genérica
        sucesso_email, msg_email = enviar_email_confirmacao_generico(
            destinatario_email=email,
            assunto=assunto,
            corpo_html=mensagem_html,
            corpo_texto=mensagem_texto
        )

        if sucesso_email:
            logger.info(f"✅ E-mail de confirmação enviado para {email} (usuário {user_id})")
            return True, "E-mail de confirmação enviado com sucesso."
        else:
            logger.error(f"❌ Falha ao enviar e-mail de confirmação para {email}: {msg_email}")
            return False, f"Falha ao enviar e-mail de confirmação: {msg_email}"

    except Exception as e:
        logger.exception(f"Erro ao enviar e-mail de confirmação para {email}")
        return False, f"Erro interno ao enviar e-mail de confirmação: {e}"

# ----------------------------------------------
# 2) Confirmar e-mail com token
# ----------------------------------------------
def confirmar_email_com_token(token: str) -> Tuple[bool, str]:
    """
    Valida o token de confirmação de e-mail e marca o e-mail como confirmado no banco.
    """
    try:
        payload, msg_validacao = validar_token_confirmacao_email(token)

        if not payload:
            return False, msg_validacao

        email_do_token = payload.get("email")
        user_id_do_token = payload.get("user_id")

        if not email_do_token or not user_id_do_token:
            return False, "Token de confirmação inválido ou incompleto."

        # Busca o usuário para garantir que o token ainda corresponde
        ok_user, usuario_db = buscar_usuario_por_email(email_do_token)
        if not ok_user or not usuario_db or usuario_db.get("id") != user_id_do_token:
            return False, "Usuário não encontrado ou token não corresponde."

        # Verifica se o token no banco ainda é o mesmo (evita reuso de tokens antigos)
        if usuario_db.get("email_confirm_token") != token:
            return False, "Token de confirmação já utilizado ou inválido."

        # Marca o e-mail como confirmado usando a função de auth.user
        sucesso_marcar, msg_marcar = marcar_email_como_confirmado(email_do_token)

        if sucesso_marcar:
            logger.info(f"✅ E-mail {email_do_token} confirmado com sucesso para usuário {user_id_do_token}.")
            return True, "Seu e-mail foi confirmado com sucesso! Você já pode fazer login."
        else:
            logger.error(f"❌ Falha ao marcar e-mail {email_do_token} como confirmado: {msg_marcar}")
            return False, f"Erro ao confirmar e-mail: {msg_marcar}"

    except Exception as e:
        logger.exception(f"Erro ao confirmar e-mail com token {token}")
        return False, f"Erro interno ao confirmar e-mail: {e}"


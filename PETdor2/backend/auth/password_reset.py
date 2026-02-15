"""
Reset de senha via Supabase Auth — PETDor2
Versão simples, mas com tratamento de 429 / email rate limit.
"""

import streamlit as st
import logging
import re
from typing import Tuple

from backend.database.supabase_client import supabase

logger = logging.getLogger(__name__)


# ==========================================================
# 📧 SOLICITAR RESET DE SENHA
# ==========================================================
def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Envia e-mail de redefinição de senha via Supabase Auth.

    Returns:
        (sucesso: bool, mensagem: str)
    """
    try:
        email = email.strip().lower()

        if not email or "@" not in email:
            return False, "Informe um e-mail válido."

        redirect_url = (
            st.secrets["app"]["STREAMLIT_APP_URL"]
            + "/redefinir_senha"
        )

        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": redirect_url
            },
        )

        logger.info(f"📧 Reset de senha solicitado para: {email}")

        # Mensagem genérica (não revelar se e-mail existe ou não)
        return True, (
            "Se o e-mail estiver cadastrado, você receberá "
            "um link para redefinir sua senha em alguns instantes."
        )

    except Exception as e:
        logger.exception("❌ Erro ao solicitar reset de senha")

        error_msg = str(e).lower()

        # 429 genérico
        if "429" in error_msg or "too many requests" in error_msg:
            # tenta extrair segundos
            try:
                match = re.search(r'after (\d+) seconds', error_msg)
                if match:
                    segundos = match.group(1)
                    return False, (
                        f"⏱️ Muitas tentativas de recuperação. "
                        f"Aguarde {segundos} segundos e tente novamente."
                    )
            except Exception:
                pass

            return False, (
                "⏱️ Limite de solicitações atingido. "
                "Aguarde alguns minutos antes de tentar novamente."
            )

        # Limite de envio de e-mail
        if "email rate limit exceeded" in error_msg:
            return False, (
                "⏱️ Limite de e-mails de recuperação atingido. "
                "Aguarde alguns minutos antes de tentar novamente. "
                "Se o problema persistir, entre em contato com o suporte."
            )

        # erro genérico
        return False, "Erro ao solicitar recuperação. Tente novamente mais tarde."


# ==========================================================
# 🔐 REDEFINIR SENHA
# ==========================================================
def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine a senha do usuário autenticado via token do Supabase.

    Returns:
        (sucesso: bool, mensagem: str)
    """
    try:
        if not nova_senha:
            return False, "Informe a nova senha."

        if len(nova_senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        session = supabase.auth.get_session()

        if not session or not session.user:
            return False, (
                "Sessão inválida ou expirada. "
                "Solicite um novo link de redefinição."
            )

        supabase.auth.update_user({
            "password": nova_senha
        })

        logger.info(f"✅ Senha redefinida para user_id={session.user.id}")

        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.exception("❌ Erro ao redefinir senha")

        error_msg = str(e).lower()

        if "weak password" in error_msg or "password" in error_msg:
            return False, (
                "Senha não atende aos requisitos de segurança. "
                "Use pelo menos 6 caracteres com letras e números."
            )

        if "429" in error_msg or "too many requests" in error_msg:
            return False, (
                "⏱️ Muitas tentativas de redefinição. "
                "Aguarde um pouco antes de tentar novamente."
            )

        return False, "Erro ao redefinir senha. Tente novamente mais tarde."


__all__ = ["solicitar_reset_senha", "redefinir_senha"]


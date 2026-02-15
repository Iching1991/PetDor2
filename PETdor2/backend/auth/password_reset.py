"""
Reset de senha via Supabase Auth — PETDor2
✅ Proteção contra 429 e email rate limit
"""

import streamlit as st
import logging
import re
from typing import Tuple

from backend.database.supabase_client import supabase
from backend.auth.rate_limiter import (
    verificar_rate_limit,
    registrar_tentativa,
    registrar_erro_429,
    limpar_historico,
)

logger = logging.getLogger(__name__)


# ==========================================================
# 📧 SOLICITAR RESET
# ==========================================================
def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Envia e-mail de recuperação.

    Returns:
        (sucesso: bool, mensagem: str)
    """

    try:
        email = email.strip().lower()

        if not email or "@" not in email:
            return False, "Informe um e-mail válido."

        # Verificar rate limit LOCAL
        pode, msg = verificar_rate_limit("recuperacao_senha", email)
        if not pode:
            return False, msg

        # Registrar tentativa
        registrar_tentativa("recuperacao_senha", email)

        logger.info(f"🔄 Reset solicitado: {email}")

        # Enviar e-mail
        redirect_url = (
            st.secrets["app"]["STREAMLIT_APP_URL"] + "/redefinir_senha"
        )

        supabase.auth.reset_password_email(
            email,
            options={"redirect_to": redirect_url}
        )

        logger.info(f"✅ E-mail enviado: {email}")

        # Limpar histórico após sucesso
        limpar_historico("recuperacao_senha", email)

        return True, (
            "Se o e-mail estiver cadastrado, você receberá "
            "um link para redefinir sua senha em alguns instantes."
        )

    except Exception as e:
        logger.exception(f"❌ Erro reset: {email}")

        error_msg = str(e).lower()

        # DETECTAR 429
        if "429" in error_msg or "too many requests" in error_msg:
            registrar_erro_429("recuperacao_senha", email)

            # Tentar extrair segundos
            try:
                match = re.search(r'after (\d+) seconds', error_msg)
                if match:
                    seg = match.group(1)
                    return False, (
                        f"⏱️ Muitas tentativas. "
                        f"Aguarde {seg} segundos."
                    )
            except:
                pass

            return False, (
                "⏱️ Limite atingido. "
                "Aguarde alguns minutos."
            )

        # DETECTAR EMAIL RATE LIMIT
        if "email rate limit exceeded" in error_msg:
            registrar_erro_429("recuperacao_senha", email)
            return False, (
                "⏱️ Limite de e-mails atingido. "
                "Aguarde 15 minutos antes de tentar novamente."
            )

        return False, "Erro ao solicitar recuperação."


# ==========================================================
# 🔐 REDEFINIR SENHA
# ==========================================================
def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine senha do usuário autenticado.

    Returns:
        (sucesso: bool, mensagem: str)
    """

    try:
        if not nova_senha:
            return False, "Informe a nova senha."

        if len(nova_senha) < 6:
            return False, "Mínimo de 6 caracteres."

        # Verificar rate limit
        pode, msg = verificar_rate_limit("redefinir_senha")
        if not pode:
            return False, msg

        # Registrar tentativa
        registrar_tentativa("redefinir_senha")

        # Verificar sessão
        session = supabase.auth.get_session()

        if not session or not session.user:
            return False, (
                "Sessão inválida. "
                "Solicite um novo link."
            )

        # Atualizar senha
        supabase.auth.update_user({
            "password": nova_senha
        })

        logger.info(f"✅ Senha redefinida: {session.user.id}")

        # Limpar histórico
        limpar_historico("redefinir_senha")

        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.exception("❌ Erro redefinir")

        error_msg = str(e).lower()

        if "429" in error_msg:
            registrar_erro_429("redefinir_senha")
            return False, "⏱️ Aguarde antes de tentar."

        if "weak password" in error_msg:
            return False, "Senha muito fraca."

        return False, "Erro ao redefinir senha."


__all__ = ["solicitar_reset_senha", "redefinir_senha"]



__all__ = ["solicitar_reset_senha", "redefinir_senha"]



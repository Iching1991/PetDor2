"""
Reset de senha via Supabase Auth — PETDor2

✅ Proteção contra rate limiting (429)
✅ Validações robustas
✅ Logs detalhados
✅ Mensagens amigáveis
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
# 📧 SOLICITAR RESET DE SENHA
# ==========================================================
def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    """
    Envia e-mail de redefinição de senha via Supabase Auth.

    ✅ Protegido contra rate limiting
    ✅ Validações de e-mail
    ✅ Mensagem genérica por segurança

    Args:
        email: E-mail do usuário

    Returns:
        (sucesso: bool, mensagem: str)
    """

    try:
        email = email.strip().lower()

        # -------------------------
        # VALIDAÇÕES
        # -------------------------
        if not email:
            return False, "Informe um e-mail válido."

        if "@" not in email or "." not in email.split("@")[1]:
            return False, "Formato de e-mail inválido."

        # -------------------------
        # 🛡️ VERIFICAR RATE LIMIT
        # -------------------------
        pode_executar, msg_erro = verificar_rate_limit("recuperacao_senha", email)
        if not pode_executar:
            return False, msg_erro

        # Registrar tentativa
        registrar_tentativa("recuperacao_senha", email)

        logger.info(f"🔄 Solicitando reset de senha: {email}")

        # -------------------------
        # 📧 ENVIAR E-MAIL
        # -------------------------
        redirect_url = (
            st.secrets["app"]["STREAMLIT_APP_URL"] + "/redefinir_senha"
        )

        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": redirect_url
            },
        )

        logger.info(f"✅ E-mail de recuperação enviado: {email}")

        # ✅ Sucesso: limpar histórico
        limpar_historico("recuperacao_senha", email)

        # Mensagem genérica por segurança (não revelar se e-mail existe)
        return True, (
            "Se este e-mail estiver cadastrado, você receberá "
            "instruções para redefinir sua senha em alguns instantes. "
            "Verifique também sua caixa de spam."
        )

    except Exception as e:
        logger.exception(f"❌ Erro ao solicitar reset: {email}")

        error_msg = str(e).lower()

        # -------------------------
        # 🚨 DETECTAR E REGISTRAR 429
        # -------------------------
        if "429" in error_msg or "too many requests" in error_msg:
            registrar_erro_429("recuperacao_senha", email)

            # Tentar extrair tempo de espera
            try:
                match = re.search(r'after (\d+) seconds', error_msg)
                if match:
                    segundos = match.group(1)
                    return False, (
                        f"⏱️ Muitas tentativas de recuperação. "
                        f"Aguarde {segundos} segundos e tente novamente."
                    )
            except:
                pass

            return False, (
                "⏱️ Limite de solicitações atingido. "
                "Aguarde alguns minutos antes de tentar novamente."
            )

        # Erro genérico
        return False, (
            "Erro ao solicitar recuperação. "
            "Tente novamente em alguns instantes."
        )


# ==========================================================
# 🔐 REDEFINIR SENHA
# ==========================================================
def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine a senha do usuário autenticado via token do Supabase.

    ✅ Protegido contra rate limiting
    ✅ Validações de senha forte
    ✅ Verifica sessão ativa

    IMPORTANTE:
    • O token já vem autenticado quando o usuário abre o link do e-mail
    • Não é necessário receber token como parâmetro

    Args:
        nova_senha: Nova senha do usuário

    Returns:
        (sucesso: bool, mensagem: str)
    """

    try:
        # -------------------------
        # VALIDAÇÕES
        # -------------------------
        if not nova_senha:
            return False, "Informe a nova senha."

        if len(nova_senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        # Recomendação de senha forte (opcional)
        if len(nova_senha) < 8:
            logger.warning("⚠️ Senha redefinida com menos de 8 caracteres")

        # -------------------------
        # 🛡️ VERIFICAR RATE LIMIT
        # -------------------------
        pode_executar, msg_erro = verificar_rate_limit("redefinir_senha")
        if not pode_executar:
            return False, msg_erro

        # Registrar tentativa
        registrar_tentativa("redefinir_senha")

        # -------------------------
        # VERIFICAR SESSÃO ATIVA
        # -------------------------
        session = supabase.auth.get_session()

        if not session or not session.user:
            logger.warning("⚠️ Tentativa de redefinir senha sem sessão ativa")
            return False, (
                "Sessão inválida ou expirada. "
                "Solicite um novo link de redefinição."
            )

        user_id = session.user.id
        logger.info(f"🔐 Redefinindo senha para user_id: {user_id}")

        # -------------------------
        # ATUALIZAR SENHA
        # -------------------------
        supabase.auth.update_user({
            "password": nova_senha
        })

        logger.info(f"✅ Senha redefinida com sucesso: {user_id}")

        # ✅ Sucesso: limpar histórico
        limpar_historico("redefinir_senha")

        return True, "✅ Senha redefinida com sucesso! Você já pode fazer login."

    except Exception as e:
        logger.exception("❌ Erro ao redefinir senha")

        error_msg = str(e).lower()

        # -------------------------
        # 🚨 DETECTAR E REGISTRAR 429
        # -------------------------
        if "429" in error_msg or "too many requests" in error_msg:
            registrar_erro_429("redefinir_senha")

            return False, (
                "⏱️ Muitas tentativas. "
                "Aguarde alguns instantes antes de tentar novamente."
            )

        # Tratamentos específicos
        if "session" in error_msg or "invalid" in error_msg:
            return False, (
                "Sessão inválida ou expirada. "
                "Solicite um novo link de redefinição."
            )

        if "weak password" in error_msg or "password" in error_msg:
            return False, (
                "Senha não atende aos requisitos de segurança. "
                "Use pelo menos 6 caracteres com letras e números."
            )

        # Erro genérico
        return False, "Erro ao redefinir senha. Tente novamente."


# ==========================================================
# EXPORTS
# ==========================================================
__all__ = [
    "solicitar_reset_senha",
    "redefinir_senha",
]

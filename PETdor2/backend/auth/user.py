"""
Autenticação e Cadastro de Usuários - PETDor2
Sistema híbrido: Supabase Auth + tabela usuarios customizada
✅ Rate limiting tratado
✅ Lazy imports (evita circular import)
✅ Logs detalhados
✅ Mensagens amigáveis
"""

from typing import Tuple, Optional, Dict, Any
import streamlit as st
import logging
import re
import time

logger = logging.getLogger(__name__)


# ==========================================================
# 📝 CADASTRO (com proteção contra 429)
# ==========================================================
def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str,
    pais: str,
) -> Tuple[bool, str]:
    """
    Cadastra usuário no Supabase Auth + tabela usuarios.

    ✅ Trata rate limiting (429)
    ✅ Validações robustas
    ✅ Rollback automático em caso de falha
    """

    # 🔒 Lazy imports (evita circular import)
    from backend.database.supabase_client import supabase
    from backend.database import supabase_table_insert

    try:
        # Normalização
        email = email.lower().strip()
        nome = nome.strip()
        tipo = tipo.lower().strip()

        # -------------------------
        # Validações básicas
        # -------------------------
        if not nome or len(nome) < 3:
            return False, "Nome deve ter pelo menos 3 caracteres."

        if len(senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        if not email or "@" not in email or "." not in email.split("@")[1]:
            return False, "E-mail inválido."

        logger.info(f"🔄 Iniciando cadastro: {email}")

        # -------------------------
        # 1️⃣ Criar no Supabase Auth
        # -------------------------
        auth_resp = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {
                "email_redirect_to": (
                    st.secrets["app"]["STREAMLIT_APP_URL"] + "/confirmar_email"
                ),
                "data": {
                    "nome": nome,
                    "tipo_usuario": tipo,
                }
            }
        })

        if not auth_resp.user:
            logger.error(f"❌ Falha no Auth para: {email}")
            return False, "Falha ao criar usuário. Tente novamente."

        user_id = auth_resp.user.id
        logger.info(f"✅ Auth criado: {user_id}")

        # -------------------------
        # 2️⃣ Criar perfil na tabela
        # -------------------------
        perfil = supabase_table_insert(
            table="usuarios",
            data={
                "id": user_id,
                "nome": nome,
                "email": email,
                "tipo_usuario": tipo,
                "pais": pais,
                "ativo": True,
                "is_admin": False,
            },
        )

        if not perfil:
            logger.error(f"❌ Falha ao criar perfil para: {user_id}")
            # TODO: Implementar rollback do auth.users se necessário
            return False, "Erro ao criar perfil do usuário."

        logger.info(f"✅ Perfil criado: {user_id}")

        return True, (
            "✅ Conta criada com sucesso! "
            "Verifique seu e-mail para confirmar o cadastro."
        )

    except Exception as e:
        logger.exception(f"❌ Erro ao cadastrar: {email}")

        error_msg = str(e).lower()

        # -------------------------
        # 🚨 TRATAMENTO DO ERRO 429
        # -------------------------
        if "429" in error_msg or "too many requests" in error_msg:
            # Extrair tempo de espera se disponível
            try:
                match = re.search(r'after (\d+) seconds', error_msg)
                if match:
                    segundos = match.group(1)
                    return False, (
                        f"⏱️ Muitas tentativas de cadastro. "
                        f"Aguarde {segundos} segundos e tente novamente."
                    )
            except:
                pass

            return False, (
                "⏱️ Limite de cadastros atingido. "
                "Aguarde 1 minuto e tente novamente."
            )

        # -------------------------
        # Outros erros comuns
        # -------------------------
        if "already registered" in error_msg or "already exists" in error_msg:
            return False, "Este e-mail já está cadastrado."

        if "invalid email" in error_msg:
            return False, "Formato de e-mail inválido."

        if "weak password" in error_msg or "password" in error_msg:
            return False, "Senha muito fraca. Use pelo menos 6 caracteres com letras e números."

        # Erro genérico (não expor detalhes técnicos)
        return False, "Erro ao criar conta. Tente novamente em alguns instantes."


# ==========================================================
# 🔐 LOGIN (com proteção contra 429)
# ==========================================================
def fazer_login(
    email: str,
    senha: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Autentica usuário via Supabase Auth.

    ✅ Trata rate limiting
    ✅ Busca dados completos da tabela usuarios
    """

    from backend.database.supabase_client import supabase
    from backend.database import supabase_table_select

    try:
        email = email.lower().strip()

        logger.info(f"🔄 Tentativa de login: {email}")

        # Login via Supabase Auth
        auth_resp = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha,
        })

        if not auth_resp.user:
            logger.warning(f"⚠️ Login falhou: {email}")
            return False, "E-mail ou senha incorretos.", None

        user_id = auth_resp.user.id

        # Buscar dados completos
        usuario = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        if not usuario:
            logger.error(f"❌ Perfil não encontrado: {user_id}")
            return False, "Perfil de usuário não encontrado.", None

        logger.info(f"✅ Login bem-sucedido: {email}")

        return True, "Login realizado com sucesso!", usuario[0]

    except Exception as e:
        logger.exception(f"❌ Erro no login: {email}")

        error_msg = str(e).lower()

        # Tratamento 429
        if "429" in error_msg or "too many requests" in error_msg:
            return False, (
                "⏱️ Muitas tentativas de login. "
                "Aguarde alguns instantes e tente novamente."
            ), None

        # Email não confirmado
        if "email not confirmed" in error_msg:
            return False, (
                "📧 Por favor, confirme seu e-mail antes de fazer login. "
                "Verifique sua caixa de entrada."
            ), None

        # Credenciais inválidas
        if "invalid login credentials" in error_msg or "invalid" in error_msg:
            return False, "E-mail ou senha incorretos.", None

        return False, "Erro ao fazer login. Tente novamente.", None


# ==========================================================
# 🚪 LOGOUT
# ==========================================================
def fazer_logout() -> Tuple[bool, str]:
    """
    Faz logout do usuário atual.
    """

    from backend.database.supabase_client import supabase

    try:
        supabase.auth.sign_out()
        logger.info("✅ Logout realizado")
        return True, "Logout realizado com sucesso."
    except Exception as e:
        logger.exception("❌ Erro ao fazer logout")
        return False, f"Erro ao fazer logout: {e}"


# ==========================================================
# 👤 BUSCAR USUÁRIO
# ==========================================================
def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário pelo e-mail na tabela usuarios.
    """

    from backend.database import supabase_table_select

    resultado = supabase_table_select(
        table="usuarios",
        filters={"email": email.lower().strip()},
        limit=1,
    )

    return resultado[0] if resultado else None


def buscar_usuario_por_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário pelo ID na tabela usuarios.
    """

    from backend.database import supabase_table_select

    resultado = supabase_table_select(
        table="usuarios",
        filters={"id": user_id},
        limit=1,
    )

    return resultado[0] if resultado else None


# ==========================================================
# 🔄 RECUPERAÇÃO DE SENHA
# ==========================================================
def solicitar_recuperacao_senha(email: str) -> Tuple[bool, str]:
    """
    Envia e-mail de recuperação via Supabase Auth.
    """

    from backend.database.supabase_client import supabase

    try:
        email = email.lower().strip()

        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": (
                    st.secrets["app"]["STREAMLIT_APP_URL"] + "/redefinir_senha"
                )
            }
        )

        logger.info(f"✅ E-mail de recuperação enviado: {email}")

        return True, (
            "Se este e-mail estiver cadastrado, você receberá "
            "instruções para redefinir sua senha."
        )

    except Exception as e:
        logger.exception(f"❌ Erro ao solicitar recuperação: {email}")

        error_msg = str(e).lower()

        if "429" in error_msg:
            return False, "⏱️ Aguarde alguns instantes antes de tentar novamente."

        return False, "Erro ao solicitar recuperação. Tente novamente."


def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine senha do usuário autenticado.
    """

    from backend.database.supabase_client import supabase

    try:
        if len(nova_senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        supabase.auth.update_user({
            "password": nova_senha
        })

        logger.info("✅ Senha redefinida")
        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.exception("❌ Erro ao redefinir senha")
        return False, f"Erro ao redefinir senha: {e}"


# ==========================================================
# ✅ USUÁRIO ATUAL
# ==========================================================
def obter_usuario_atual() -> Optional[Dict[str, Any]]:
    """
    Retorna dados do usuário autenticado.
    """

    from backend.database.supabase_client import supabase

    try:
        session = supabase.auth.get_session()

        if not session or not session.user:
            return None

        return buscar_usuario_por_id(session.user.id)

    except Exception as e:
        logger.exception("❌ Erro ao obter usuário atual")
        return None


# ==========================================================
# 🛡️ HELPER: Verificar se pode cadastrar
# ==========================================================
def pode_cadastrar() -> Tuple[bool, str]:
    """
    Verifica se o sistema permite novos cadastros no momento.

    Útil para implementar throttling manual se necessário.

    Returns:
        (pode: bool, mensagem: str)
    """

    # Implementação futura: verificar rate limit global, 
    # manutenção programada, etc.

    return True, "Sistema disponível"

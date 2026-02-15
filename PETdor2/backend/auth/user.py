"""
Autenticação e Cadastro de Usuários - PETDor2
Sistema híbrido: Supabase Auth + tabela usuarios customizada

✅ Proteção contra duplicatas
✅ Rate limiting tratado (429)
✅ Email rate limit tratado
✅ Lazy imports (evita circular import)
✅ Logs detalhados
✅ Mensagens amigáveis
✅ Validações robustas

Autor: Inner AI + Agnaldo
Data: 2026-02-15
"""

from typing import Tuple, Optional, Dict, Any
import streamlit as st
import logging
import re

logger = logging.getLogger(__name__)


# ==========================================================
# 📝 CADASTRO (proteção total)
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

    ✅ Verifica duplicatas antes de criar
    ✅ Trata 429 e email rate limit
    ✅ Mensagens amigáveis

    Args:
        nome: Nome completo (mín. 3 caracteres)
        email: E-mail válido
        senha: Senha (mín. 6 caracteres)
        tipo: Tipo de usuário (veterinario, tutor, etc)
        pais: País do usuário

    Returns:
        (sucesso: bool, mensagem: str)
    """

    # 🔒 Lazy imports (evita circular import)
    from backend.database.supabase_client import supabase
    from backend.database import supabase_table_insert, supabase_table_select

    try:
        # -------------------------
        # 1️⃣ NORMALIZAÇÃO
        # -------------------------
        email = email.lower().strip()
        nome = nome.strip()
        tipo = tipo.lower().strip()
        pais = pais.strip()

        # -------------------------
        # 2️⃣ VALIDAÇÕES BÁSICAS
        # -------------------------
        if not nome or len(nome) < 3:
            return False, "❌ Nome deve ter pelo menos 3 caracteres."

        if len(senha) < 6:
            return False, "❌ A senha deve ter pelo menos 6 caracteres."

        if not email or "@" not in email:
            return False, "❌ E-mail inválido."

        # Validação extra de e-mail
        if "." not in email.split("@")[1]:
            return False, "❌ E-mail inválido (domínio sem extensão)."

        logger.info(f"🔄 Iniciando cadastro: {email}")

        # -------------------------
        # 3️⃣ VERIFICAR DUPLICATA (e-mail)
        # -------------------------
        usuario_existente = supabase_table_select(
            table="usuarios",
            filters={"email": email},
            limit=1,
        )

        if usuario_existente:
            logger.warning(f"⚠️ E-mail já cadastrado: {email}")
            return False, (
                "Este e-mail já está cadastrado. "
                "Tente fazer login ou recuperar sua senha."
            )

        # -------------------------
        # 4️⃣ CRIAR NO SUPABASE AUTH
        # -------------------------
        try:
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
        except Exception as auth_error:
            # Tratar erros específicos do Auth
            error_msg = str(auth_error).lower()

            if "user already registered" in error_msg:
                return False, (
                    "Este e-mail já está cadastrado no sistema de autenticação. "
                    "Tente fazer login."
                )

            # Re-lançar para tratamento geral
            raise

        if not auth_resp.user:
            logger.error(f"❌ Falha no Auth para: {email}")
            return False, "Falha ao criar usuário. Tente novamente."

        user_id = auth_resp.user.id
        logger.info(f"✅ Usuário criado no Auth: {user_id}")

        # -------------------------
        # 5️⃣ VERIFICAR DUPLICATA (ID)
        # -------------------------
        # Dupla verificação: às vezes o Auth retorna um user existente
        perfil_existente = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        if perfil_existente:
            logger.warning(f"⚠️ Perfil já existe para user_id: {user_id}")
            return False, (
                "Este e-mail já possui cadastro. "
                "Tente fazer login ou recuperar sua senha."
            )

        # -------------------------
        # 6️⃣ CRIAR PERFIL NA TABELA
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
            return False, (
                "Erro ao criar perfil do usuário. "
                "Entre em contato com o suporte."
            )

        logger.info(f"✅ Perfil criado com sucesso: {user_id}")

        return True, (
            "✅ Conta criada com sucesso! "
            "Verifique seu e-mail para confirmar o cadastro."
        )

    except Exception as e:
        logger.exception(f"❌ Erro ao cadastrar: {email}")

        error_msg = str(e).lower()

        # -------------------------
        # 🚨 TRATAMENTO DE ERROS
        # -------------------------

        # Rate limiting (429)
        if "429" in error_msg or "too many requests" in error_msg:
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
                "Aguarde alguns minutos antes de tentar novamente."
            )

        # Email rate limit (específico do Supabase)
        if "email rate limit exceeded" in error_msg:
            return False, (
                "⏱️ Limite de envio de e-mails atingido. "
                "Aguarde 15 minutos antes de tentar novamente. "
                "Se o problema persistir, entre em contato com o suporte."
            )

        # Duplicata (23505 - PostgreSQL)
        if "23505" in error_msg or "duplicate key" in error_msg or "already exists" in error_msg:
            return False, (
                "Este e-mail já está cadastrado. "
                "Tente fazer login ou recuperar sua senha."
            )

        # E-mail já registrado
        if "already registered" in error_msg:
            return False, "Este e-mail já está cadastrado."

        # E-mail inválido
        if "invalid email" in error_msg:
            return False, "Formato de e-mail inválido."

        # Senha fraca
        if "weak password" in error_msg or "password" in error_msg:
            return False, (
                "Senha muito fraca. "
                "Use pelo menos 6 caracteres com letras e números."
            )

        # Erro genérico (não expor detalhes técnicos)
        return False, (
            "Erro ao criar conta. "
            "Tente novamente em alguns instantes ou entre em contato com o suporte."
        )


# ==========================================================
# 🔐 LOGIN (proteção contra rate limiting)
# ==========================================================
def fazer_login(
    email: str,
    senha: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Autentica usuário via Supabase Auth.

    Args:
        email: E-mail do usuário
        senha: Senha do usuário

    Returns:
        (sucesso: bool, mensagem: str, dados_usuario: dict | None)
    """

    from backend.database.supabase_client import supabase
    from backend.database import supabase_table_select

    try:
        email = email.lower().strip()

        logger.info(f"🔄 Tentativa de login: {email}")

        # Autenticar no Auth
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
            return False, (
                "Perfil de usuário não encontrado. "
                "Entre em contato com o suporte."
            ), None

        # Verificar se usuário está ativo
        if not usuario[0].get("ativo", True):
            logger.warning(f"⚠️ Tentativa de login com conta inativa: {email}")
            return False, (
                "Sua conta está inativa. "
                "Entre em contato com o suporte."
            ), None

        logger.info(f"✅ Login bem-sucedido: {email}")

        return True, "Login realizado com sucesso!", usuario[0]

    except Exception as e:
        logger.exception(f"❌ Erro no login: {email}")

        error_msg = str(e).lower()

        # Rate limiting
        if "429" in error_msg or "too many requests" in error_msg:
            return False, (
                "⏱️ Muitas tentativas de login. "
                "Aguarde alguns instantes e tente novamente."
            ), None

        # Email não confirmado
        if "email not confirmed" in error_msg:
            return False, (
                "📧 Por favor, confirme seu e-mail antes de fazer login. "
                "Verifique sua caixa de entrada e spam."
            ), None

        # Credenciais inválidas
        if "invalid login credentials" in error_msg or "invalid" in error_msg:
            return False, "E-mail ou senha incorretos.", None

        # Erro genérico
        return False, (
            "Erro ao fazer login. "
            "Tente novamente em alguns instantes."
        ), None


# ==========================================================
# 🚪 LOGOUT
# ==========================================================
def fazer_logout() -> Tuple[bool, str]:
    """
    Faz logout do usuário atual.

    Returns:
        (sucesso: bool, mensagem: str)
    """

    from backend.database.supabase_client import supabase

    try:
        supabase.auth.sign_out()
        logger.info("✅ Logout realizado")
        return True, "Logout realizado com sucesso."

    except Exception as e:
        logger.exception("❌ Erro ao fazer logout")
        return False, "Erro ao fazer logout. Tente novamente."


# ==========================================================
# 👤 BUSCAR USUÁRIO
# ==========================================================
def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário pelo e-mail na tabela usuarios.

    Args:
        email: E-mail do usuário

    Returns:
        Dados do usuário ou None se não encontrado
    """

    from backend.database import supabase_table_select

    try:
        resultado = supabase_table_select(
            table="usuarios",
            filters={"email": email.lower().strip()},
            limit=1,
        )

        return resultado[0] if resultado else None

    except Exception as e:
        logger.exception(f"❌ Erro ao buscar usuário por e-mail: {email}")
        return None


def buscar_usuario_por_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário pelo ID na tabela usuarios.

    Args:
        user_id: UUID do usuário

    Returns:
        Dados do usuário ou None se não encontrado
    """

    from backend.database import supabase_table_select

    try:
        resultado = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        return resultado[0] if resultado else None

    except Exception as e:
        logger.exception(f"❌ Erro ao buscar usuário por ID: {user_id}")
        return None


# ==========================================================
# 🔄 RECUPERAÇÃO DE SENHA
# ==========================================================
def solicitar_recuperacao_senha(email: str) -> Tuple[bool, str]:
    """
    Envia e-mail de recuperação de senha via Supabase Auth.

    Args:
        email: E-mail do usuário

    Returns:
        (sucesso: bool, mensagem: str)
    """

    from backend.database.supabase_client import supabase

    try:
        email = email.lower().strip()

        if not email or "@" not in email:
            return False, "E-mail inválido."

        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": (
                    st.secrets["app"]["STREAMLIT_APP_URL"] + "/redefinir_senha"
                )
            }
        )

        logger.info(f"✅ E-mail de recuperação enviado: {email}")

        # Mensagem genérica por segurança
        return True, (
            "Se este e-mail estiver cadastrado, você receberá "
            "instruções para redefinir sua senha em alguns instantes."
        )

    except Exception as e:
        logger.exception(f"❌ Erro ao solicitar recuperação: {email}")

        error_msg = str(e).lower()

        # Rate limiting
        if "429" in error_msg or "too many requests" in error_msg:
            try:
                match = re.search(r'after (\d+) seconds', error_msg)
                if match:
                    segundos = match.group(1)
                    return False, (
                        f"⏱️ Muitas tentativas de recuperação. "
                        f"Aguarde {segundos} segundos."
                    )
            except:
                pass

            return False, (
                "⏱️ Limite atingido. "
                "Aguarde alguns minutos."
            )

        # Email rate limit
        if "email rate limit exceeded" in error_msg:
            return False, (
                "⏱️ Limite de e-mails atingido. "
                "Aguarde 15 minutos antes de tentar novamente."
            )

        return False, (
            "Erro ao solicitar recuperação. "
            "Tente novamente em alguns instantes."
        )


def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine senha do usuário autenticado.

    Args:
        nova_senha: Nova senha (mín. 6 caracteres)

    Returns:
        (sucesso: bool, mensagem: str)
    """

    from backend.database.supabase_client import supabase

    try:
        if len(nova_senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        supabase.auth.update_user({
            "password": nova_senha
        })

        logger.info("✅ Senha redefinida com sucesso")
        return True, "✅ Senha redefinida com sucesso!"

    except Exception as e:
        logger.exception("❌ Erro ao redefinir senha")

        error_msg = str(e).lower()

        if "weak password" in error_msg or "password" in error_msg:
            return False, (
                "Senha muito fraca. "
                "Use pelo menos 6 caracteres com letras e números."
            )

        return False, "Erro ao redefinir senha. Tente novamente."


# ==========================================================
# ✅ USUÁRIO ATUAL
# ==========================================================
def obter_usuario_atual() -> Optional[Dict[str, Any]]:
    """
    Retorna dados do usuário atualmente autenticado.

    Returns:
        Dados do usuário ou None se não autenticado
    """

    from backend.database.supabase_client import supabase

    try:
        session = supabase.auth.get_session()

        if not session or not session.user:
            return None

        # Buscar dados completos
        usuario = buscar_usuario_por_id(session.user.id)

        if not usuario:
            logger.warning(
                f"⚠️ Sessão ativa mas perfil não encontrado: {session.user.id}"
            )
            return None

        # Verificar se está ativo
        if not usuario.get("ativo", True):
            logger.warning(
                f"⚠️ Sessão ativa mas conta inativa: {session.user.email}"
            )
            return None

        return usuario

    except Exception as e:
        logger.exception("❌ Erro ao obter usuário atual")
        return None


# ==========================================================
# 🔍 VERIFICAR SE USUÁRIO ESTÁ AUTENTICADO
# ==========================================================
def esta_autenticado() -> bool:
    """
    Verifica se há um usuário autenticado.

    Returns:
        True se autenticado, False caso contrário
    """

    usuario = obter_usuario_atual()
    return usuario is not None


# ==========================================================
# 👑 VERIFICAR SE É ADMIN
# ==========================================================
def e_admin() -> bool:
    """
    Verifica se o usuário atual é administrador.

    Returns:
        True se admin, False caso contrário
    """

    usuario = obter_usuario_atual()

    if not usuario:
        return False

    return usuario.get("is_admin", False) is True


# ==========================================================
# EXPORTS
# ==========================================================
__all__ = [
    "cadastrar_usuario",
    "fazer_login",
    "fazer_logout",
    "buscar_usuario_por_email",
    "buscar_usuario_por_id",
    "solicitar_recuperacao_senha",
    "redefinir_senha",
    "obter_usuario_atual",
    "esta_autenticado",
    "e_admin",
]

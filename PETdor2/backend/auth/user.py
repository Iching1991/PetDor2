"""
Autenticação e Cadastro de Usuários - PETDor2
Sistema híbrido: Supabase Auth + tabela usuarios customizada
"""
from typing import Tuple, Optional, Dict, Any
import streamlit as st
import logging


from backend.database.supabase_client import supabase
from backend.database import supabase_table_select, supabase_table_insert

logger = logging.getLogger(__name__)


# ==========================================================
# 📝 CADASTRO
# ==========================================================
def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str,
    pais: str,
) -> Tuple[bool, str]:
    """
    Cadastra um novo usuário usando Supabase Auth + tabela usuarios.

    Args:
        nome: Nome completo do usuário
        email: E-mail (será normalizado para lowercase)
        senha: Senha (mínimo 6 caracteres recomendado)
        tipo: Tipo de usuário (ex: "veterinario", "tutor")
        pais: País do usuário

    Returns:
        (sucesso: bool, mensagem: str)
    """
    try:
        email = email.lower().strip()
        nome = nome.strip()

        # Validações básicas
        if len(senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        if not email or "@" not in email:
            return False, "E-mail inválido."

        logger.info(f"🔄 Iniciando cadastro para: {email}")

        # 1️⃣ Criar usuário no Supabase Auth
        auth_resp = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {
                "email_redirect_to": st.secrets["app"]["STREAMLIT_APP_URL"] + "/confirmar_email",
                "data": {
                    "nome": nome,
                    "tipo_usuario": tipo.lower(),
                }
            }
        })

        if not auth_resp.user:
            logger.error(f"❌ Falha ao criar usuário no Auth: {email}")
            return False, "Falha ao criar usuário. Tente novamente."

        user_id = auth_resp.user.id
        logger.info(f"✅ Usuário criado no Auth: {user_id}")

        # 2️⃣ Criar perfil na tabela usuarios
        usuario = supabase_table_insert(
            table="usuarios",
            data={
                "id": user_id,  # mesmo ID do auth.users
                "nome": nome,
                "email": email,
                "tipo_usuario": tipo.lower(),
                "pais": pais,
                "ativo": True,
                "is_admin": False,
            },
        )

        if not usuario:
            logger.error(f"❌ Falha ao criar perfil na tabela usuarios: {user_id}")
            # Tentar reverter (opcional - depende da sua lógica)
            return False, "Erro ao criar perfil do usuário."

        logger.info(f"✅ Perfil criado na tabela usuarios: {user_id}")

        return True, (
            "✅ Conta criada com sucesso! "
            "Verifique seu e-mail para confirmar o cadastro."
        )

    except Exception as e:
        logger.exception(f"❌ Erro ao cadastrar usuário: {email}")

        # Mensagens de erro mais amigáveis
        error_msg = str(e).lower()
        if "already registered" in error_msg or "already exists" in error_msg:
            return False, "Este e-mail já está cadastrado."
        elif "invalid email" in error_msg:
            return False, "E-mail inválido."
        elif "password" in error_msg:
            return False, "Senha muito fraca. Use pelo menos 6 caracteres."
        else:
            return False, f"Erro ao cadastrar: {e}"


# ==========================================================
# 🔐 LOGIN
# ==========================================================
def fazer_login(email: str, senha: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Autentica um usuário via Supabase Auth.

    Args:
        email: E-mail do usuário
        senha: Senha do usuário

    Returns:
        (sucesso: bool, mensagem: str, dados_usuario: dict | None)
    """
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

        # Buscar dados extras da tabela usuarios
        usuario = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        if not usuario:
            logger.error(f"❌ Perfil não encontrado para user_id: {user_id}")
            return False, "Perfil de usuário não encontrado.", None

        logger.info(f"✅ Login bem-sucedido: {email}")

        return True, "Login realizado com sucesso!", usuario[0]

    except Exception as e:
        logger.exception(f"❌ Erro ao fazer login: {email}")

        error_msg = str(e).lower()
        if "invalid login credentials" in error_msg:
            return False, "E-mail ou senha incorretos.", None
        elif "email not confirmed" in error_msg:
            return False, "Por favor, confirme seu e-mail antes de fazer login.", None
        else:
            return False, f"Erro ao fazer login: {e}", None


# ==========================================================
# 🚪 LOGOUT
# ==========================================================
def fazer_logout() -> Tuple[bool, str]:
    """
    Faz logout do usuário atual.

    Returns:
        (sucesso: bool, mensagem: str)
    """
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
    Busca um usuário pelo e-mail na tabela usuarios.

    Args:
        email: E-mail do usuário

    Returns:
        Dados do usuário ou None se não encontrado
    """
    resultado = supabase_table_select(
        table="usuarios",
        filters={"email": email.lower().strip()},
        limit=1,
    )
    return resultado[0] if resultado else None


def buscar_usuario_por_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Busca um usuário pelo ID na tabela usuarios.

    Args:
        user_id: UUID do usuário

    Returns:
        Dados do usuário ou None se não encontrado
    """
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
    Envia e-mail de recuperação de senha via Supabase Auth.

    Args:
        email: E-mail do usuário

    Returns:
        (sucesso: bool, mensagem: str)
    """
    try:
        email = email.lower().strip()

        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": st.secrets["app"]["STREAMLIT_APP_URL"] + "/redefinir_senha"
            }
        )

        logger.info(f"✅ E-mail de recuperação enviado para: {email}")

        return True, (
            "Se este e-mail estiver cadastrado, você receberá "
            "instruções para redefinir sua senha."
        )

    except Exception as e:
        logger.exception(f"❌ Erro ao solicitar recuperação de senha: {email}")
        return False, f"Erro ao solicitar recuperação: {e}"


def redefinir_senha(nova_senha: str) -> Tuple[bool, str]:
    """
    Redefine a senha do usuário autenticado.

    Args:
        nova_senha: Nova senha (mínimo 6 caracteres)

    Returns:
        (sucesso: bool, mensagem: str)
    """
    try:
        if len(nova_senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        supabase.auth.update_user({
            "password": nova_senha
        })

        logger.info("✅ Senha redefinida com sucesso")
        return True, "Senha redefinida com sucesso!"

    except Exception as e:
        logger.exception("❌ Erro ao redefinir senha")
        return False, f"Erro ao redefinir senha: {e}"


# ==========================================================
# ✅ VERIFICAR SESSÃO ATIVA
# ==========================================================
def obter_usuario_atual() -> Optional[Dict[str, Any]]:
    """
    Retorna os dados do usuário atualmente autenticado.

    Returns:
        Dados do usuário ou None se não autenticado
    """
    try:
        session = supabase.auth.get_session()

        if not session or not session.user:
            return None

        # Buscar dados completos da tabela usuarios
        return buscar_usuario_por_id(session.user.id)

    except Exception as e:
        logger.exception("❌ Erro ao obter usuário atual")
        return None


"""
Autenticação e Cadastro de Usuários - PETDor2
Sistema híbrido: Supabase Auth + tabela usuarios customizada
IMPORT SAFE (sem circular import)
"""

from typing import Tuple, Optional, Dict, Any
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# 📝 CADASTRO
# ==========================================================
def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str,
    pais: str,
) -> Tuple[bool, str]:
    """
    Cria usuário no Supabase Auth + perfil na tabela usuarios
    """

    # 🔒 Lazy imports (evita circular import)
    from backend.database.supabase_client import supabase
    from backend.database import supabase_table_insert

    try:
        email = email.lower().strip()
        nome = nome.strip()
        tipo = tipo.lower().strip()

        # -------------------------
        # Validações básicas
        # -------------------------
        if len(senha) < 6:
            return False, "A senha deve ter pelo menos 6 caracteres."

        if not email or "@" not in email:
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
                    st.secrets["app"]["STREAMLIT_APP_URL"]
                    + "/confirmar_email"
                ),
                "data": {
                    "nome": nome,
                    "tipo_usuario": tipo,
                }
            }
        })

        if not auth_resp.user:
            logger.error("❌ Falha no Auth")
            return False, "Falha ao criar usuário."

        user_id = auth_resp.user.id
        logger.info(f"✅ Auth criado: {user_id}")

        # -------------------------
        # 2️⃣ Criar perfil
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
            logger.error("❌ Falha ao criar perfil")
            return False, "Erro ao criar perfil do usuário."

        logger.info("✅ Perfil criado")

        return True, (
            "Conta criada com sucesso! "
            "Verifique seu e-mail para confirmar."
        )

    except Exception as e:
        logger.exception("Erro no cadastro")

        error_msg = str(e).lower()

        if "already registered" in error_msg:
            return False, "Este e-mail já está cadastrado."

        return False, f"Erro ao cadastrar: {e}"


# ==========================================================
# 🔐 LOGIN
# ==========================================================
def fazer_login(
    email: str,
    senha: str
) -> Tuple[bool, str, Optional[Dict[str, Any]]]:

    from backend.database.supabase_client import supabase
    from backend.database import supabase_table_select

    try:
        email = email.lower().strip()

        logger.info(f"🔄 Login: {email}")

        auth_resp = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha,
        })

        if not auth_resp.user:
            return False, "E-mail ou senha incorretos.", None

        user_id = auth_resp.user.id

        usuario = supabase_table_select(
            table="usuarios",
            filters={"id": user_id},
            limit=1,
        )

        if not usuario:
            return False, "Perfil não encontrado.", None

        return True, "Login realizado.", usuario[0]

    except Exception as e:
        logger.exception("Erro no login")

        error_msg = str(e).lower()

        if "email not confirmed" in error_msg:
            return False, "Confirme seu e-mail primeiro.", None

        return False, f"Erro ao logar: {e}", None


# ==========================================================
# 🚪 LOGOUT
# ==========================================================
def fazer_logout() -> Tuple[bool, str]:

    from backend.database.supabase_client import supabase

    try:
        supabase.auth.sign_out()
        return True, "Logout realizado."
    except Exception as e:
        return False, f"Erro ao sair: {e}"


# ==========================================================
# 👤 BUSCAR USUÁRIO
# ==========================================================
def buscar_usuario_por_email(email: str):

    from backend.database import supabase_table_select

    resultado = supabase_table_select(
        table="usuarios",
        filters={"email": email.lower()},
        limit=1,
    )

    return resultado[0] if resultado else None


def buscar_usuario_por_id(user_id: str):

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
def solicitar_recuperacao_senha(email: str):

    from backend.database.supabase_client import supabase

    try:
        email = email.lower().strip()

        supabase.auth.reset_password_email(
            email,
            options={
                "redirect_to": (
                    st.secrets["app"]["STREAMLIT_APP_URL"]
                    + "/redefinir_senha"
                )
            }
        )

        return True, (
            "Se o e-mail existir, enviaremos instruções."
        )

    except Exception as e:
        logger.exception("Erro reset senha")
        return False, f"Erro: {e}"


# ==========================================================
# 🔑 REDEFINIR SENHA (logado via token)
# ==========================================================
def redefinir_senha(nova_senha: str):

    from backend.database.supabase_client import supabase

    try:
        if len(nova_senha) < 6:
            return False, "Senha muito curta."

        supabase.auth.update_user({
            "password": nova_senha
        })

        return True, "Senha redefinida."

    except Exception as e:
        logger.exception("Erro redefinir senha")
        return False, f"Erro: {e}"


# ==========================================================
# ✅ USUÁRIO ATUAL
# ==========================================================
def obter_usuario_atual():

    from backend.database.supabase_client import supabase

    try:
        session = supabase.auth.get_session()

        if not session or not session.user:
            return None

        return buscar_usuario_por_id(session.user.id)

    except Exception:
        logger.exception("Erro sessão")
        return None

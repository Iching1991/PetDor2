# PETdor2/backend/auth/user.py
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Importações absolutas a partir do pacote 'backend'
from database.supabase_client import get_supabase
from auth.security import hash_password, verify_password # Assumindo que hash_password e verify_password estão em auth.security

logger = logging.getLogger(__name__)

# ==========================================================
# LOGIN / AUTENTICAÇÃO
# ==========================================================
def verificar_credenciais(email: str, senha: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Verifica as credenciais do usuário (email e senha) no Supabase.
    Retorna (True, dados_usuario) em caso de sucesso, ou (False, {"erro": mensagem}) em caso de falha.
    """
    try:
        supabase = get_supabase()
        response = supabase.from_("usuarios").select("*").eq("email", email.lower()).single().execute()
        usuario = response.data

        if not usuario:
            logger.warning(f"Tentativa de login falhou: Usuário não encontrado para {email}")
            return False, {"erro": "Usuário não encontrado."}

        # Verifica se o e-mail foi confirmado
        if not usuario.get("email_confirmado", False):
            logger.warning(f"Tentativa de login falhou: E-mail não confirmado para {email}")
            return False, {"erro": "Seu e-mail ainda não foi confirmado. Por favor, verifique sua caixa de entrada."}

        # Verifica se o usuário está ativo
        if not usuario.get("ativo", True): # Assume ativo=True se não especificado
            logger.warning(f"Tentativa de login falhou: Usuário inativo para {email}")
            return False, {"erro": "Sua conta está inativa. Entre em contato com o suporte."}

        if not verify_password(senha, usuario.get("senha_hash", "")):
            logger.warning(f"Tentativa de login falhou: Senha incorreta para {email}")
            return False, {"erro": "Senha incorreta."}

        logger.info(f"✅ Login bem-sucedido para {email}")
        return True, usuario
    except Exception as e:
        logger.error(f"Erro ao verificar credenciais para {email}: {e}", exc_info=True)
        return False, {"erro": f"Erro ao verificar credenciais: {str(e)}"}

# ==========================================================
# BUSCA DE USUÁRIO
# ==========================================================
def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca um usuário pelo email no Supabase.
    Retorna os dados do usuário em caso de sucesso, ou None se não encontrado ou em caso de erro.
    """
    try:
        supabase = get_supabase()
        response = supabase.from_("usuarios").select("*").eq("email", email.lower()).single().execute()
        return response.data if response.data else None
    except Exception as e:
        # Supabase client levanta exceção se 'single()' não encontra nada,
        # o que é esperado para usuários não existentes.
        # Logamos apenas erros inesperados.
        if "No rows found" not in str(e):
            logger.error(f"Erro inesperado ao buscar usuário por email '{email}': {e}", exc_info=True)
        logger.warning(f"Usuário não encontrado: {email}")
        return None

# ==========================================================
# CADASTRO
# ==========================================================
def cadastrar_usuario(nome: str, email: str, senha: str, tipo: str = "Tutor", pais: str = "Brasil") -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Cadastra um novo usuário no Supabase.
    Retorna (True, mensagem_sucesso, dados_usuario) ou (False, mensagem_erro, None).
    """
    try:
        supabase = get_supabase()
        if buscar_usuario_por_email(email):
            return False, "❌ Este e-mail já está cadastrado.", None
        if len(senha) < 6:
            return False, "❌ A senha deve ter pelo menos 6 caracteres.", None

        senha_hash = hash_password(senha)
        payload = {
            "nome": nome,
            "email": email.lower(),
            "senha_hash": senha_hash,
            "tipo_usuario": tipo, # Renomeado para 'tipo_usuario' para consistência
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": False,
            "criado_em": datetime.utcnow().isoformat(),
        }
        response = supabase.from_("usuarios").insert(payload).execute()

        if not response.data:
            logger.error(f"Erro ao inserir usuário: {email}. Resposta: {response.data}")
            return False, "❌ Erro ao cadastrar. Tente novamente.", None

        logger.info(f"✅ Usuário {email} cadastrado com sucesso (pendente de confirmação).")
        return True, "✅ Cadastro realizado com sucesso! Verifique seu e-mail para confirmar a conta.", response.data[0]
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}", exc_info=True)
        return False, f"❌ Erro ao cadastrar: {str(e)}", None

# ==========================================================
# ATUALIZAÇÃO DE USUÁRIO
# ==========================================================
def atualizar_tipo_usuario(user_id: int, novo_tipo: str) -> bool:
    """
    Atualiza o tipo de usuário (ex: 'Tutor', 'Veterinário', 'Admin') no Supabase.
    Retorna True em caso de sucesso, False em caso de falha.
    """
    try:
        supabase = get_supabase()
        data_to_update = {"tipo_usuario": novo_tipo}
        response = supabase.from_("usuarios").update(data_to_update).eq("id", user_id).execute()

        if not response.data:
            logger.error(f"Falha ao atualizar tipo de usuário para ID {user_id}. Resposta: {response.data}")
            return False
        logger.info(f"✅ Tipo de usuário para ID {user_id} atualizado para '{novo_tipo}'.")
        return True
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar tipo de usuário para ID {user_id}: {e}", exc_info=True)
        return False

def atualizar_status_usuario(user_id: int, novo_status: str) -> bool:
    """
    Atualiza o status do usuário (ex: 'ativo', 'inativo', 'pendente_confirmacao') no Supabase.
    Retorna True em caso de sucesso, False em caso de falha.
    """
    try:
        supabase = get_supabase()
        data_to_update = {"status": novo_status} # Assumindo que você tem uma coluna 'status'
        response = supabase.from_("usuarios").update(data_to_update).eq("id", user_id).execute()

        if not response.data:
            logger.error(f"Falha ao atualizar status de usuário para ID {user_id}. Resposta: {response.data}")
            return False
        logger.info(f"✅ Status de usuário para ID {user_id} atualizado para '{novo_status}'.")
        return True
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar status de usuário para ID {user_id}: {e}", exc_info=True)
        return False

def atualizar_email_confirmado(user_id: int, confirmado: bool = True) -> bool:
    """
    Atualiza o status de confirmação de e-mail do usuário.
    Retorna True em caso de sucesso, False em caso de falha.
    """
    try:
        supabase = get_supabase()
        data_to_update = {"email_confirmado": confirmado}
        response = supabase.from_("usuarios").update(data_to_update).eq("id", user_id).execute()

        if not response.data:
            logger.error(f"Falha ao atualizar status de confirmação de e-mail para ID {user_id}. Resposta: {response.data}")
            return False
        logger.info(f"✅ Status de confirmação de e-mail para ID {user_id} atualizado para '{confirmado}'.")
        return True
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar status de confirmação de e-mail para ID {user_id}: {e}", exc_info=True)
        return False

def redefinir_senha(user_id: int, nova_senha: str) -> bool:
    """
    Redefine a senha de um usuário no Supabase.
    Retorna True em caso de sucesso, False em caso de falha.
    """
    try:
        supabase = get_supabase()
        nova_senha_hash = hash_password(nova_senha)
        data_to_update = {"senha_hash": nova_senha_hash}
        response = supabase.from_("usuarios").update(data_to_update).eq("id", user_id).execute()

        if not response.data:
            logger.error(f"Falha ao redefinir senha para ID {user_id}. Resposta: {response.data}")
            return False
        logger.info(f"✅ Senha para ID {user_id} redefinida com sucesso.")
        return True
    except Exception as e:
        logger.error(f"Erro inesperado ao redefinir senha para ID {user_id}: {e}", exc_info=True)
        return False

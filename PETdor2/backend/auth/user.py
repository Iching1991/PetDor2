# PETdor2/backend/auth/user.py
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Importações absolutas a partir do pacote 'backend'
from database.supabase_client import get_supabase # Importa get_supabase diretamente
from auth.security import hash_password, verify_password # Importa as funções de hash e verificação de senha

logger = logging.getLogger(__name__)

# ==========================================================
# VERIFICAÇÃO DE CREDENCIAIS
# ==========================================================
def verificar_credenciais(email: str, senha: str) -> Tuple[bool, Dict[str, Any]]:
    """Verifica as credenciais do usuário (email e senha) no Supabase."""
    try:
        supabase = get_supabase()
        response = supabase.from_("usuarios").select("*").eq("email", email.lower()).single().execute()
        usuario = response.data

        if not usuario:
            logger.warning(f"Tentativa de login com email não encontrado: {email}")
            return False, {"erro": "Usuário não encontrado."}

        # Verifica se a senha fornecida corresponde ao hash armazenado
        if not verify_password(senha, usuario.get("senha_hash", "")):
            logger.warning(f"Tentativa de login com senha incorreta para {email}")
            return False, {"erro": "Senha incorreta."}

        # Verifica se o e-mail foi confirmado
        if not usuario.get("email_confirmado", False):
            logger.warning(f"Tentativa de login com email não confirmado para {email}")
            return False, {"erro": "Seu e-mail ainda não foi confirmado. Por favor, verifique sua caixa de entrada."}

        # Verifica se o usuário está ativo
        if not usuario.get("ativo", False):
            logger.warning(f"Tentativa de login com usuário inativo: {email}")
            return False, {"erro": "Sua conta está inativa. Entre em contato com o suporte."}

        logger.info(f"✅ Login bem-sucedido para {email}")
        return True, usuario
    except Exception as e:
        logger.error(f"Erro ao verificar credenciais para {email}: {e}", exc_info=True)
        return False, {"erro": f"Erro interno ao verificar credenciais: {str(e)}"}

# ==========================================================
# BUSCA DE USUÁRIO
# ==========================================================
def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca um usuário pelo email no Supabase."""
    try:
        supabase = get_supabase()
        response = supabase.from_("usuarios").select("*").eq("email", email.lower()).single().execute()
        return response.data if response.data else None
    except Exception as e:
        # Captura exceções como PostgrestAPIError se o single() não encontrar nada
        # ou outras exceções de rede/Supabase.
        # Não é necessariamente um erro se o usuário não for encontrado, apenas um warning.
        logger.debug(f"Usuário '{email}' não encontrado ou erro na busca: {e}")
        return None

# ==========================================================
# CADASTRO
# ==========================================================
def cadastrar_usuario(nome: str, email: str, senha: str, tipo: str = "Tutor", pais: str = "Brasil") -> Tuple[bool, str]:
    """Cadastra um novo usuário no Supabase."""
    try:
        supabase = get_supabase()
        if buscar_usuario_por_email(email):
            return False, "❌ Este e-mail já está cadastrado."
        if len(senha) < 6:
            return False, "❌ A senha deve ter pelo menos 6 caracteres."

        senha_hash = hash_password(senha) # Hasheia a senha
        payload = {
            "nome": nome,
            "email": email.lower(),
            "senha_hash": senha_hash,
            "tipo": tipo, # 'Tutor', 'Veterinario', 'Admin', 'Clinica'
            "pais": pais,
            "email_confirmado": False, # Padrão: e-mail não confirmado
            "ativo": True, # Padrão: usuário ativo, mas pendente de confirmação de e-mail
            "is_admin": False, # Padrão: não é admin
            "criado_em": datetime.utcnow().isoformat(),
        }
        response = supabase.from_("usuarios").insert(payload).execute()

        if not response.data:
            logger.error(f"Erro ao inserir usuário {email}: {response.status_code} - {response.text}")
            return False, "❌ Erro ao cadastrar. Tente novamente."

        logger.info(f"✅ Usuário {email} cadastrado com sucesso (pendente de confirmação de e-mail).")
        return True, "✅ Cadastro realizado com sucesso! Verifique seu e-mail para confirmar a conta."
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário {email}: {e}", exc_info=True)
        return False, f"❌ Erro ao cadastrar: {str(e)}"

# ==========================================================
# ATUALIZAÇÃO DE USUÁRIO (Adicionadas para o streamlit_app.py)
# ==========================================================
def atualizar_tipo_usuario(user_id: int, novo_tipo: str) -> bool:
    """Atualiza o tipo de usuário (Tutor, Veterinario, Admin, Clinica) no Supabase."""
    try:
        supabase = get_supabase()
        data_to_update = {"tipo": novo_tipo} # O nome da coluna é 'tipo', não 'tipo_usuario'
        response = supabase.from_("usuarios").update(data_to_update).eq("id", user_id).execute()
        if response.data:
            logger.info(f"Tipo de usuário para ID {user_id} atualizado para '{novo_tipo}'.")
            return True
        logger.error(f"Falha ao atualizar tipo de usuário para ID {user_id}: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar tipo de usuário para ID {user_id}: {e}", exc_info=True)
        return False

def atualizar_status_usuario(user_id: int, novo_status: str) -> bool:
    """Atualiza o status do usuário (ex: 'ativo', 'inativo', 'pendente_confirmacao') no Supabase."""
    try:
        supabase = get_supabase()
        data_to_update = {"status": novo_status} # Assumindo que você tem uma coluna 'status'
        response = supabase.from_("usuarios").update(data_to_update).eq("id", user_id).execute()
        if response.data:
            logger.info(f"Status de usuário para ID {user_id} atualizado para '{novo_status}'.")
            return True
        logger.error(f"Falha ao atualizar status de usuário para ID {user_id}: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar status de usuário para ID {user_id}: {e}", exc_info=True)
        return False

# Nota: As funções de redefinir_senha não estão aqui, elas devem estar em auth.password_reset.py

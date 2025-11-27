# PETdor2/backend/auth/user.py
import sys
import os
import logging
from datetime import datetime

# --- Ajuste do sys.path para imports absolutos ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", ".."))  # raiz PETdor2
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim ajuste ---

from auth.security import hash_password, verify_password
from database.supabase_client import get_supabase  # agora absoluto

logger = logging.getLogger(__name__)

# ==========================================================
# LOGIN / AUTENTICAÇÃO
# ==========================================================
def verificar_credenciais(email: str, senha: str) -> tuple[bool, dict]:
    try:
        supabase = get_supabase()
        response = supabase.from_("usuarios").select("*").eq("email", email).single().execute()
        usuario = response.data
        if not usuario:
            return False, {"erro": "Usuário não encontrado"}
        if not verify_password(senha, usuario.get("senha_hash", "")):
            return False, {"erro": "Senha incorreta"}
        logger.info(f"✅ Login bem-sucedido para {email}")
        return True, usuario
    except Exception as e:
        logger.error(f"Erro ao verificar credenciais: {e}", exc_info=True)
        return False, {"erro": str(e)}

# ==========================================================
# BUSCA DE USUÁRIO
# ==========================================================
def buscar_usuario_por_email(email: str) -> dict | None:
    try:
        supabase = get_supabase()
        response = supabase.from_("usuarios").select("*").eq("email", email).single().execute()
        return response.data if response.data else None
    except Exception:
        logger.warning(f"Usuário não encontrado: {email}")
        return None

# ==========================================================
# CADASTRO
# ==========================================================
def cadastrar_usuario(nome: str, email: str, senha: str, tipo: str = "tutor", pais: str = "Brasil") -> tuple[bool, str]:
    try:
        supabase = get_supabase()
        if buscar_usuario_por_email(email):
            return False, "❌ Este e-mail já está cadastrado."
        if len(senha) < 6:
            return False, "❌ A senha deve ter pelo menos 6 caracteres."
        senha_hash = hash_password(senha)
        payload = {
            "nome": nome,
            "email": email.lower(),
            "senha_hash": senha_hash,
            "tipo": tipo,
            "pais": pais,
            "email_confirmado": False,
            "ativo": True,
            "is_admin": False,
            "criado_em": datetime.utcnow().isoformat(),
        }
        response = supabase.from_("usuarios").insert(payload).execute()
        if not response.data:
            logger.error(f"Erro ao inserir usuário: {email}")
            return False, "❌ Erro ao cadastrar. Tente novamente."
        logger.info(f"✅ Usuário {email} cadastrado com sucesso")
        return True, "✅ Cadastro realizado com sucesso! Verifique seu e-mail."
    except Exception as e:
        logger.error(f"Erro ao cadastrar usuário: {e}", exc_info=True)
        return False, f"❌ Erro ao cadastrar: {str(e)}"

# ==========================================================
# RESTANTE DAS FUNÇÕES (redefinir_senha, atualizar_tipo_usuario, atualizar_status_usuario)
# mantém-se igual, apenas imports já ajustados

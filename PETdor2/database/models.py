# PETdor2/database/models.py
from .supabase_client import supabase  # importação relativa corrigida
import logging

logger = logging.getLogger(__name__)

def buscar_usuario_por_email(email: str):
    try:
        resp = supabase.table("usuarios").select("*").eq("email", email).execute()
        if resp.data:
            return resp.data[0]  # retorna o dicionário do usuário
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar usuário por email {email}: {e}")
        return None

# PETdor2/database/supabase_client.py
import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Variáveis SUPABASE_URL e SUPABASE_KEY não definidas!")
    raise EnvironmentError("Supabase URL ou KEY não definidas nas variáveis de ambiente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def testar_conexao() -> bool:
    """Testa se a conexão com o Supabase está funcionando corretamente."""
    try:
        response = supabase.table("usuarios").select("*").limit(1).execute()
        if response.error:
            logger.error(f"Erro ao testar Supabase: {response.error.message}")
            return False
        return True
    except Exception as e:
        logger.error(f"Erro inesperado ao testar Supabase: {e}", exc_info=True)
        return False

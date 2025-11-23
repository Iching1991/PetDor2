# PETdor2/database/supabase_client.py
import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client | None = None

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("SUPABASE_URL ou SUPABASE_KEY não definidas. Supabase não será inicializado.")
else:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Cliente Supabase inicializado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao criar cliente Supabase: {e}")
        supabase = None

def testar_conexao() -> bool:
    """Testa se a conexão com Supabase está ativa."""
    if supabase is None:
        logger.warning("Supabase não inicializado. Conexão não pode ser testada.")
        return False
    try:
        response = supabase.table("usuarios").select("*").limit(1).execute()
        if response.error:
            logger.error(f"Erro ao testar Supabase: {response.error.message}")
        return response.error is None
    except Exception as e:
        logger.error(f"Erro inesperado ao testar Supabase: {e}")
        return False

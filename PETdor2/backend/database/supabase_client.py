"""
Cliente Supabase centralizado - PETDor2
Singleton com cache para evitar múltiplas instâncias
"""
import streamlit as st
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)


@st.cache_resource
def get_supabase_client() -> Client:
    """
    Retorna o cliente Supabase (singleton com cache).
    Usa a publishable key para operações seguras do lado do cliente.
    """
    try:
        url = st.secrets["supabase"]["SUPABASE_URL"]
        key = st.secrets["supabase"]["SUPABASE_KEY"]  # publishable key

        logger.info(f"✅ Conectando ao Supabase: {url}")
        client = create_client(url, key)
        logger.info("✅ Cliente Supabase inicializado com sucesso")

        return client

    except KeyError as e:
        logger.critical(f"❌ Secrets do Supabase não encontradas: {e}")
        raise RuntimeError(
            "Configuração do Supabase incompleta. "
            "Verifique SUPABASE_URL e SUPABASE_KEY em secrets.toml"
        ) from e
    except Exception as e:
        logger.critical(f"❌ Erro ao criar cliente Supabase: {e}", exc_info=True)
        raise


# Cliente global (inicializado sob demanda)
supabase = get_supabase_client()

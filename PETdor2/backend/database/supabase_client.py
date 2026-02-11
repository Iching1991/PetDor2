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

"""
Cliente Supabase centralizado - PETDor2
SDK + REST helpers + Admin client
"""

import streamlit as st
import logging
from supabase import create_client, Client
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# ==========================================================
# CLIENTES
# ==========================================================

@st.cache_resource
def get_supabase_client() -> Client:
    """Cliente público (RLS ativo)."""
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_KEY"]

    logger.info("🔗 Inicializando Supabase (public client)")
    return create_client(url, key)


@st.cache_resource
def get_supabase_admin_client() -> Client:
    """Cliente admin (bypass RLS)."""
    url = st.secrets["supabase"]["SUPABASE_URL"]
    key = st.secrets["supabase"]["SUPABASE_SECRET_KEY"]

    logger.warning("🔐 Inicializando Supabase ADMIN client")
    return create_client(url, key)


# Instâncias globais
supabase: Client = get_supabase_client()
supabase_admin: Client = get_supabase_admin_client()

# ==========================================================
# SELECT
# ==========================================================

def supabase_table_select(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    select: str = "*",
    order: Optional[str] = None,
    limit: Optional[int] = None,
) -> Optional[List[Dict[str, Any]]]:

    try:
        query = supabase.table(table).select(select)

        if filters:
            for k, v in filters.items():
                query = query.eq(k, v)

        if order:
            col, direction = order.split(".")
            query = query.order(col, desc=(direction == "desc"))

        if limit:
            query = query.limit(limit)

        response = query.execute()
        return response.data

    except Exception as e:
        logger.error(f"❌ SELECT erro: {e}", exc_info=True)
        return None


# ==========================================================
# INSERT (ADMIN → evita RLS no cadastro)
# ==========================================================

def supabase_table_insert(
    table: str,
    data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:

    try:
        response = supabase_admin.table(table).insert(data).execute()

        if response.data:
            return response.data[0]

        return None

    except Exception as e:
        logger.error(
            f"❌ INSERT erro | Tabela={table} | Payload={data} | Erro={e}",
            exc_info=True,
        )
        return None


# ==========================================================
# UPDATE
# ==========================================================

def supabase_table_update(
    table: str,
    filters: Dict[str, Any],
    data: Dict[str, Any],
) -> Optional[List[Dict[str, Any]]]:

    try:
        query = supabase_admin.table(table).update(data)

        for k, v in filters.items():
            query = query.eq(k, v)

        response = query.execute()
        return response.data

    except Exception as e:
        logger.error(f"❌ UPDATE erro: {e}", exc_info=True)
        return None


# ==========================================================
# DELETE
# ==========================================================

def supabase_table_delete(
    table: str,
    filters: Dict[str, Any],
) -> bool:

    try:
        query = supabase_admin.table(table).delete()

        for k, v in filters.items():
            query = query.eq(k, v)

        query.execute()
        return True

    except Exception as e:
        logger.error(f"❌ DELETE erro: {e}", exc_info=True)
        return False


# ==========================================================
# TESTE
# ==========================================================

def testar_conexao() -> bool:
    try:
        supabase.table("usuarios").select("id").limit(1).execute()
        logger.info("✅ Conexão Supabase OK")
        return True
    except Exception as e:
        logger.error(f"❌ Falha conexão Supabase: {e}")
        return False


__all__ = [
    "supabase",
    "supabase_admin",
    "supabase_table_select",
    "supabase_table_insert",
    "supabase_table_update",
    "supabase_table_delete",
    "testar_conexao",
]

# PETdor2/backend/database/supabase_client.py

import os
import streamlit as st
from supabase import create_client, Client
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# -----------------------------------
# 1 — Criar cliente Supabase
# -----------------------------------
def get_supabase() -> Client:
    try:
        # Streamlit Cloud usa secrets
        if "streamlit" in os.environ.get("STREAMLIT_VERSION", ""):
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
        else:
            # Local usa .env
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "SUPABASE_URL ou SUPABASE_ANON_KEY não configurados."
            )

        return create_client(supabase_url, supabase_key)

    except Exception as e:
        st.error(f"Erro ao conectar com Supabase: {e}")
        raise


# -----------------------------------
# 2 — Função de teste de conexão
# -----------------------------------
def testar_conexao() -> bool:
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()

        st.success("✅ Conexão com Supabase OK")
        return True

    except Exception as e:
        st.error(f"❌ Falha ao testar conexão: {e}")
        return False


# -----------------------------------
# 3 — SELECT genérico
# -----------------------------------
def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False
) -> Tuple[bool, Any]:
    try:
        client = get_supabase()
        query = client.table(tabela).select(colunas)

        if filtros:
            for coluna, valor in filtros.items():
                query = query.eq(coluna, valor)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        response = query.execute()

        return True, response.data

    except Exception as e:
        logger.error(f"Erro no SELECT em '{tabela}': {e}")
        return False, str(e)


# -----------------------------------
# 4 — INSERT genérico
# -----------------------------------
def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, Any]:

    try:
        client = get_supabase()
        response = client.table(tabela).insert(dados).execute()

        return True, response.data

    except Exception as e:
        logger.error(f"Erro INSERT em '{tabela}': {e}")
        return False, str(e)


# -----------------------------------
# 5 — UPDATE genérico
# -----------------------------------
def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, Any]:

    try:
        client = get_supabase()
        query = client.table(tabela).update(dados_update)

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response = query.execute()
        return True, response.data

    except Exception as e:
        logger.error(f"Erro UPDATE em '{tabela}': {e}")
        return False, str(e)


# -----------------------------------
# 6 — DELETE genérico
# -----------------------------------
def supabase_table_delete(
    tabela: str,
    filtros: Dict[str, Any]
) -> Tuple[bool, int]:

    try:
        client = get_supabase()
        query = client.table(tabela).delete()

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response = query.execute()

        deletados = len(response.data) if response.data else 0
        return True, deletados

    except Exception as e:
        logger.error(f"Erro DELETE em '{tabela}': {e}")
        return False, 0

# PETdor2/backend/database/supabase_client.py

import os
import streamlit as st
from typing import Any, Dict, List, Optional, Tuple, Union
from supabase import create_client, Client

# ======================================================
# SUPABASE - Inicialização Segura
# ======================================================

_supabase_client: Optional[Client] = None


def get_supabase() -> Client:
    """Retorna instância única do cliente Supabase."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    try:
        # Se estiver no Streamlit Cloud, usar st.secrets
        if "streamlit" in os.environ.get("STREAMLIT_VERSION", "").lower():
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
        else:
            # Ambiente local
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "❌ SUPABASE_URL ou SUPABASE_ANON_KEY não configurados."
            )

        _supabase_client = create_client(supabase_url, supabase_key)
        return _supabase_client

    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {e}")
        raise


# ======================================================
# TESTE DE CONEXÃO
# ======================================================

def testar_conexao() -> bool:
    """Tenta um select vazio para verificar conexão."""
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()
        st.success("✅ Conexão com Supabase OK!")
        return True

    except Exception as e:
        st.error(f"❌ Falha ao testar conexão com Supabase: {e}")
        return False


# ======================================================
# SELECT
# ======================================================

def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False,
) -> Tuple[bool, Union[List[Dict[str, Any]], Dict[str, Any], str]]:
    """
    SELECT genérico para qualquer tabela.
    """
    try:
        client = get_supabase()
        query = client.table(tabela).select(colunas)

        if filtros:
            for coluna, valor in filtros.items():
                query = query.eq(coluna, valor)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            data = query.single().execute()
        else:
            data = query.execute()

        return True, data.data if data.data else ([] if not single else {})

    except Exception as e:
        return False, f"Erro ao buscar dados em {tabela}: {e}"


# ======================================================
# INSERT
# ======================================================

def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any],
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """INSERT genérico."""
    try:
        client = get_supabase()
        resp = client.table(tabela).insert(dados).execute()
        return True, resp.data

    except Exception as e:
        return False, f"Erro ao inserir em {tabela}: {e}"


# ==================================================

# PETdor2/backend/database/supabase_client.py

import os
import streamlit as st
from typing import Any, Dict, List, Optional, Tuple, Union
from supabase import create_client, Client

# ============================================================
# 1. Criar cliente Supabase (Streamlit Cloud + Local .env)
# ============================================================

def get_supabase() -> Client:
    try:
        # Prioriza secrets no deploy
        if "streamlit" in os.environ.get("STREAMLIT_VERSION", ""):
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
        else:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError("❌ Supabase não configurado corretamente.")

        return create_client(supabase_url, supabase_key)

    except Exception as e:
        st.error(f"⚠️ Erro ao criar cliente Supabase: {e}")
        raise

# ============================================================
# 2. Testar conexão
# ============================================================

def testar_conexao() -> bool:
    """
    Faz uma consulta simples no Supabase para validar a conexão.
    """
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()
        st.success("✅ Conexão com Supabase estabelecida!")
        return True
    except Exception as e:
        st.error(f"❌ Falha ao testar conexão com Supabase: {e}")
        return False

# ============================================================
# 3. SELECT genérico
# ============================================================

def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False
) -> Tuple[bool, Union[List[Dict[str, Any]], Dict[str, Any], str]]:

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

        return True, response.data if response.data else ([] if not single else {})

    except Exception as e:
        return False, f"Erro ao buscar dados: {e}"

# ============================================================
# 4. INSERT genérico
# ============================================================

def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:

    try:
        client = get_supabase()
        response = client.table(tabela).insert(dados).execute()

        if response.data:
            return True, response.data

        return False, "Falha ao inserir ou nenhum retorno."

    except Exception as e:
        return False, f"Erro ao inserir: {e}"

# ============================================================
# 5. UPDATE genérico
# ============================================================

def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:

    try:
        client = get_supabase()
        query = client.table(tabela).update(dados_update)

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response = query.execute()

        if response.data:
            return True, response.data

        return False, "Nenhum registro atualizado."

    except Exception as e:
        return False, f"Erro ao atualizar: {e}"

# ============================================================
# 6. DELETE genérico
# ============================================================

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
        return False, 0

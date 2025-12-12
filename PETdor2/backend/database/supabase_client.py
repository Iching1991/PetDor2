# PETdor2/backend/database/supabase_client.py

import os
import streamlit as st
from supabase import create_client, Client
from typing import Any, Dict, Optional, Tuple, List


# =========================================================
# Criar instância do Supabase
# =========================================================
def get_supabase() -> Client:
    try:
        # Prioriza st.secrets no Streamlit Cloud
        if "supabase" in st.secrets:
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
        else:
            # Local (.env)
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError("SUPABASE_URL ou SUPABASE_KEY não configurados.")

        return create_client(supabase_url, supabase_key)

    except Exception as e:
        st.error(f"❌ Erro ao inicializar Supabase: {e}")
        raise


# =========================================================
# Teste simples de conexão
# =========================================================
def testar_conexao() -> bool:
    try:
        client = get_supabase()
        # Consulta mínima na tabela "usuarios"
        client.table("usuarios").select("*").limit(1).execute()
        st.success("✅ Conexão com Supabase OK!")
        return True

    except Exception as e:
        st.error(f"❌ Falha ao testar conexão com Supabase: {e}")
        return False


# =========================================================
# SELECT genérico
# =========================================================
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
            result = query.single().execute()
        else:
            result = query.execute()

        return True, result.data

    except Exception as e:
        return False, f"Erro ao buscar dados ({tabela}): {e}"


# =========================================================
# INSERT genérico
# =========================================================
def supabase_table_insert(tabela: str, dados: Dict[str, Any]):
    try:
        client = get_supabase()
        result = client.table(tabela).insert(dados).execute()
        return True, result.data

    except Exception as e:
        return False, f"Erro ao inserir ({tabela}): {e}"


# =========================================================
# UPDATE genérico
# =========================================================
def supabase_table_update(tabela: str, dados_update: Dict[str, Any], filtros: Dict[str, Any]):
    try:
        client = get_supabase()
        query = client.table(tabela).update(dados_update)

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        result = query.execute()
        return True, result.data

    except Exception as e:
        return False, f"Erro ao atualizar ({tabela}): {e}"


# =========================================================
# DELETE genérico
# =========================================================
def supabase_table_delete(tabela: str, filtros: Dict[str, Any]):
    try:
        client = get_supabase()
        query = client.table(tabela).delete()

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        result = query.execute()
        return True, len(result.data or [])

    except Exception as e:
        return False, f"Erro ao deletar ({tabela}): {e}"

# PETdor2/backend/database/supabase_client.py

import os
import streamlit as st
from typing import Any, Dict, List, Optional, Tuple, Union

from supabase import create_client, Client
from supabase.lib.client import APIResponse

import logging

# Configura logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# =========================================================
#              CONEXÃO COM SUPABASE (REFATORADO)
# =========================================================
def get_supabase() -> Client:
    """
    Retorna cliente Supabase usando:
      - st.secrets no Streamlit Cloud
      - variáveis de ambiente no local
    """
    try:
        # Detecta Streamlit Cloud
        usando_streamlit_cloud = "streamlit" in os.environ.get("STREAMLIT_VERSION", "")

        if usando_streamlit_cloud:
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
        else:
            # Local
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError(
                "SUPABASE_URL ou SUPABASE_ANON_KEY ausentes. "
                "Verifique .env ou st.secrets."
            )

        return create_client(supabase_url, supabase_key)

    except Exception as e:
        logger.error(f"Erro ao inicializar Supabase: {e}", exc_info=True)
        st.error(f"Erro ao conectar com Supabase: {e}")
        raise


# =========================================================
#                    TESTAR CONEXÃO
# =========================================================
def testar_conexao() -> bool:
    """
    Teste simples tentando listar tabela 'usuarios'
    """
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()

        st.success("✅ Conexão com Supabase estabelecida!")
        return True

    except Exception as e:
        st.error(f"❌ Falha ao testar conexão com Supabase: {e}")
        logger.error("Falha ao testar conexão", exc_info=True)
        return False


# =========================================================
#                    SELECT GENÉRICO
# =========================================================
def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False
) -> Tuple[bool, Union[List[Dict[str, Any]], Dict[str, Any], str]]:
    """
    SELECT genérico no Supabase.
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
            query = query.single()

        response: APIResponse = query.execute()

        # Corrige casos onde não há data
        if response.data is None:
            return True, {} if single else []

        return True, response.data

    except Exception as e:
        logger.error(f"Erro no SELECT em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao buscar dados: {e}"


# =========================================================
#                    INSERT GENÉRICO
# =========================================================
def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    INSERT genérico.
    """
    try:
        client = get_supabase()
        response: APIResponse = client.table(tabela).insert(dados).execute()

        if response.data:
            logger.info(f"Insert em {tabela}: {response.data}")
            return True, response.data

        return False, "Falha ao inserir ou nenhum dado retornado."

    except Exception as e:
        logger.error(f"Erro no INSERT em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao inserir dados: {e}"


# =========================================================
#                    UPDATE GENÉRICO
# =========================================================
def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    UPDATE genérico.
    """
    try:
        client = get_supabase()

        query = client.table(tabela).update(dados_update)

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response: APIResponse = query.execute()

        if response.data:
            logger.info(f"Update em {tabela}: {response.data}")
            return True, response.data

        return False, "Nenhum registro atualizado."

    except Exception as e:
        logger.error(f"Erro no UPDATE em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao atualizar dados: {e}"


# =========================================================
#                    DELETE GENÉRICO
# =========================================================
def supabase_table_delete(
    tabela: str,
    filtros: Dict[str, Any]
) -> Tuple[bool, int]:
    """
    DELETE genérico.
    """
    try:
        client = get_supabase()
        query = client.table(tabela).delete()

        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)

        response: APIResponse = query.execute()

        deletados = len(response.data) if response.data else 0

        if deletados > 0:
            logger.info(f"Delete em {tabela}: {deletados} registro(s)")
            return True, deletados

        return False, 0

    except Exception as e:
        logger.error(f"Erro no DELETE em {tabela}: {e}", exc_info=True)
        return False, 0

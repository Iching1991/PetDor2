# PETdor2/backend/database/supabase_client.py
"""
Cliente Supabase centralizado e utilitários de acesso.

Uso:
    from backend.database.supabase_client import (
        get_supabase,
        testar_conexao,
        supabase_table_select,
        supabase_table_insert,
        supabase_table_update,
        supabase_table_delete,
    )
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional, Tuple, Union

# Import lazy - só importamos streamlit se estivermos rodando no Streamlit.
try:
    import streamlit as st  # type: ignore
except Exception:
    st = None  # type: ignore

from supabase import create_client  # supabase==2.x

logger = logging.getLogger(__name__)

# Singleton do cliente Supabase
_supabase_client = None  # type: ignore

# Nomes esperados nas secrets/env vars
KEYS = {
    "secrets_section": ("supabase", "SUPABASE_URL", "SUPABASE_KEY"),
    "env_url": "SUPABASE_URL",
    "env_key": "SUPABASE_ANON_KEY",  # nome comum usado no projeto
}


def _read_secrets() -> Tuple[Optional[str], Optional[str]]:
    """
    Tenta ler st.secrets (Streamlit Cloud) e em seguida variáveis de ambiente.
    Retorna (url, key), podendo ser (None, None) se não configurado.
    """
    # 1) Streamlit secrets (se disponível)
    if st is not None:
        try:
            sec = st.secrets.get("supabase", None)
            if sec:
                url = sec.get("SUPABASE_URL") or sec.get("url")
                key = sec.get("SUPABASE_KEY") or sec.get("SUPABASE_ANON_KEY") or sec.get("anon_key")
                if url and key:
                    return url, key
        except Exception:
            # não fatal — tenta env vars abaixo
            logger.debug("st.secrets presente mas não continha chaves válidas para Supabase.")

    # 2) Fallback: variáveis de ambiente (útil para desenvolvimento local)
    url = os.getenv(KEYS["env_url"]) or os.getenv("SUPABASE_URL")
    key = os.getenv(KEYS["env_key"]) or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    return url, key


def get_supabase() -> Any:
    """
    Retorna a instância singleton do cliente Supabase.
    Raise RuntimeError se as credenciais não estiverem configuradas.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    url, key = _read_secrets()
    if not url or not key:
        # Mensagem clara para o ambiente Streamlit
        msg = "SUPABASE_URL e/ou SUPABASE_KEY não configurados (st.secrets ou variáveis de ambiente)."
        logger.error(msg)
        if st is not None:
            st.error(msg)
        raise RuntimeError(msg)

    try:
        # Nota: usar create_client(url, key) simples — evita passar kwargs que causaram erro 'proxy'
        _supabase_client = create_client(url, key)
        logger.info("✅ Cliente Supabase inicializado com sucesso.")
        return _supabase_client
    except TypeError as te:
        # Caso surja problema por incompatibilidade de versão do SDK
        logger.exception("Erro ao inicializar cliente Supabase (TypeError). Certifique-se da versão correta do pacote 'supabase'.")
        raise
    except Exception as e:
        logger.exception(f"Erro ao inicializar cliente Supabase: {e}")
        raise


def testar_conexao() -> bool:
    """
    Testa a conexão com o Supabase fazendo um SELECT simples.
    Retorna True em caso de sucesso, False caso contrário.
    Não levanta exceções (apenas loga e, se em Streamlit, mostra mensagem).
    """
    try:
        client = get_supabase()
        # Try a minimal request to validate credentials and connectivity
        response = client.from_("usuarios").select("id").limit(1).execute()
        # A API do supabase devolve obj com .data; se não for None = ok
        if getattr(response, "data", None) is not None:
            logger.info("✅ Conexão Supabase testada com sucesso.")
            return True
        # Ainda consideramos como ok (cliente inicializado) — mas logamos
        logger.warning("Conexão Supabase inicializada, mas select não retornou dados (tabela 'usuarios' vazia?).")
        return True
    except Exception as e:
        mensagem = f"Falha ao testar conexão com Supabase: {e}"
        logger.error(mensagem, exc_info=True)
        if st is not None:
            st.error("❌ Erro ao conectar ao Supabase: " + str(e))
        return False


# --------------------------
# Operações genéricas
# --------------------------
def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    limit: Optional[int] = None,
    single: bool = False,
) -> Tuple[bool, Union[List[Dict[str, Any]], Dict[str, Any], str]]:
    """
    SELECT genérico.
    Retorna (True, dados) ou (False, mensagem_erro).
    - se single=True, retorna um dict (ou {} caso vazio)
    - se single=False, retorna uma lista (ou [] caso vazio)
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).select(colunas)

        if filtros:
            for coluna, valor in filtros.items():
                # suporte a igualdade simples; se o valor for dict, permitirá operadores futuros
                if isinstance(valor, dict):
                    # exemplo: {"idade": {"gt": 5}} -> query = query.gt("idade", 5)
                    for op, v in valor.items():
                        # map simple ops
                        if op == "eq":
                            query = query.eq(coluna, v)
                        elif op == "gt":
                            query = query.gt(coluna, v)
                        elif op == "lt":
                            query = query.lt(coluna, v)
                        elif op == "neq":
                            query = query.neq(coluna, v)
                        else:
                            # fallback to eq
                            query = query.eq(coluna, v)
                else:
                    query = query.eq(coluna, valor)

        if order_by:
            # supabase-py v2: order(column, desc=True/False)
            query = query.order(order_by, desc=desc)

        if limit is not None:
            query = query.limit(limit)

        if single:
            query = query.single()

        resp = query.execute()
        data = getattr(resp, "data", None)

        if data is None:
            return True, {} if single else []
        return True, data
    except Exception as e:
        logger.exception(f"Erro no supabase_table_select({tabela}): {e}")
        return False, f"Erro ao buscar dados: {e}"


def supabase_table_insert(tabela: str, dados: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    INSERT genérico.
    Retorna (True, dados_inseridos) ou (False, mensagem_erro).
    """
    try:
        client = get_supabase()
        resp = client.from_(tabela).insert(dados).execute()
        data = getattr(resp, "data", None)
        if data:
            logger.info(f"✅ Inserido em {tabela}: {data}")
            return True, data
        logger.warning(f"Insert em {tabela} não retornou dados.")
        return False, "Falha ao inserir dados (nenhum dado retornado)."
    except Exception as e:
        logger.exception(f"Erro no supabase_table_insert({tabela}): {e}")
        return False, f"Erro ao inserir dados: {e}"


def supabase_table_update(tabela: str, dados_update: Dict[str, Any], filtros: Dict[str, Any]) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    UPDATE genérico.
    Retorna (True, dados_atualizados) ou (False, mensagem_erro).
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).update(dados_update)
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        resp = query.execute()
        data = getattr(resp, "data", None)
        if data:
            logger.info(f"✅ Atualizado em {tabela}: {data}")
            return True, data
        logger.warning(f"Atualização em {tabela} não afetou registros.")
        return False, "Nenhum registro atualizado."
    except Exception as e:
        logger.exception(f"Erro no supabase_table_update({tabela}): {e}")
        return False, f"Erro ao atualizar dados: {e}"


def supabase_table_delete(tabela: str, filtros: Dict[str, Any]) -> Tuple[bool, Union[int, str]]:
    """
    DELETE genérico.
    Retorna (True, numero_de_registros_deletados) ou (False, mensagem_erro).
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).delete()
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        resp = query.execute()
        data = getattr(resp, "data", None)
        deleted = len(data) if data else 0
        if deleted > 0:
            logger.info(f"✅ Deletado em {tabela}: {deleted} registros")
            return True, deleted
        logger.warning(f"Deleção em {tabela} não afetou registros.")
        return False, 0
    except Exception as e:
        logger.exception(f"Erro no supabase_table_delete({tabela}): {e}")
        return False, f"Erro ao deletar dados: {e}"


# Conveniência de exportação
__all__ = [
    "get_supabase",
    "testar_conexao",
    "supabase_table_select",
    "supabase_table_insert",
    "supabase_table_update",
    "supabase_table_delete",
]

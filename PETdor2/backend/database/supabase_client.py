"""
Cliente REST do Supabase para o PETDor2
Backend-only (sem UI)
Versão refatorada com logs e tratamento de erro explícito
"""

import requests
import streamlit as st
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# ==========================================================
# 🔐 Credenciais
# ==========================================================

def _get_supabase_config() -> Dict[str, str]:
    try:
        return {
            "url": st.secrets["supabase"]["SUPABASE_URL"],
            "key": st.secrets["supabase"]["SUPABASE_KEY"],
        }
    except Exception as e:
        logger.critical("❌ Supabase secrets não encontrados", exc_info=True)
        raise RuntimeError("Supabase não configurado corretamente") from e


def _get_headers() -> Dict[str, str]:
    cfg = _get_supabase_config()
    return {
        "apikey": cfg["key"],
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


# ==========================================================
# 🔎 SELECT
# ==========================================================

def supabase_table_select(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    select: str = "*",
    order: Optional[str] = None,
    limit: Optional[int] = None,
) -> Optional[List[Dict[str, Any]]]:

    cfg = _get_supabase_config()
    url = f"{cfg['url']}/rest/v1/{table}"
    params: Dict[str, str] = {"select": select}

    if filters:
        for k, v in filters.items():
            params[k] = f"eq.{v}"

    if order:
        params["order"] = order

    if limit:
        params["limit"] = str(limit)

    try:
        r = requests.get(url, headers=_get_headers(), params=params, timeout=10)

        if r.status_code >= 400:
            logger.error(
                f"❌ ERRO SELECT Supabase | Tabela={table} | Status={r.status_code} | Resposta={r.text}"
            )
            return None

        return r.json()

    except Exception:
        logger.exception(f"❌ EXCEÇÃO SELECT Supabase | Tabela={table}")
        return None


# ==========================================================
# ➕ INSERT
# ==========================================================

def supabase_table_insert(
    table: str,
    data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:

    cfg = _get_supabase_config()
    url = f"{cfg['url']}/rest/v1/{table}"

    try:
        r = requests.post(
            url,
            headers=_get_headers(),
            json=data,
            timeout=10,
        )

        if r.status_code >= 400:
            logger.error(
                f"❌ ERRO INSERT Supabase | Tabela={table} | Status={r.status_code}"
            )
            logger.error(f"Resposta Supabase: {r.text}")
            logger.error(f"Payload enviado: {data}")
            return None

        res = r.json()
        return res[0] if res else None

    except Exception:
        logger.exception(f"❌ EXCEÇÃO INSERT Supabase | Tabela={table}")
        return None


# ==========================================================
# ✏️ UPDATE
# ==========================================================

def supabase_table_update(
    table: str,
    filters: Dict[str, Any],
    data: Dict[str, Any],
) -> Optional[List[Dict[str, Any]]]:

    cfg = _get_supabase_config()
    url = f"{cfg['url']}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in filters.items()}

    try:
        r = requests.patch(
            url,
            headers=_get_headers(),
            params=params,
            json=data,
            timeout=10,
        )

        if r.status_code >= 400:
            logger.error(
                f"❌ ERRO UPDATE Supabase | Tabela={table} | Status={r.status_code}"
            )
            logger.error(f"Resposta Supabase: {r.text}")
            logger.error(f"Filtro: {filters}")
            logger.error(f"Payload: {data}")
            return None

        return r.json()

    except Exception:
        logger.exception(f"❌ EXCEÇÃO UPDATE Supabase | Tabela={table}")
        return None


# ==========================================================
# 🗑️ DELETE
# ==========================================================

def supabase_table_delete(
    table: str,
    filters: Dict[str, Any],
) -> bool:

    cfg = _get_supabase_config()
    url = f"{cfg['url']}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in filters.items()}

    try:
        r = requests.delete(
            url,
            headers=_get_headers(),
            params=params,
            timeout=10,
        )

        if r.status_code >= 400:
            logger.error(
                f"❌ ERRO DELETE Supabase | Tabela={table} | Status={r.status_code}"
            )
            logger.error(f"Resposta Supabase: {r.text}")
            logger.error(f"Filtro: {filters}")
            return False

        return True

    except Exception:
        logger.exception(f"❌ EXCEÇÃO DELETE Supabase | Tabela={table}")
        return False


# ==========================================================
# 🔌 Teste de conexão
# ==========================================================

def testar_conexao() -> bool:
    """
    Testa conexão simples com a tabela usuarios.
    """
    resultado = supabase_table_select("usuarios", limit=1)
    if resultado is None:
        logger.error("❌ Falha ao conectar ao Supabase (SELECT usuarios)")
        return False

    logger.info("✅ Conexão com Supabase OK")
    return True

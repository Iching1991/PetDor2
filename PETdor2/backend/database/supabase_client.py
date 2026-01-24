# backend/database/supabase_client.py
"""
Cliente REST do Supabase para o PETDor2
Backend-only (sem UI)
"""

import requests
import streamlit as st
from typing import Optional, Dict, Any, List


# ==========================================================
# Credenciais
# ==========================================================

def _get_supabase_config() -> Dict[str, str]:
    return {
        "url": st.secrets["supabase"]["SUPABASE_URL"],
        "key": st.secrets["supabase"]["SUPABASE_KEY"],
    }


def _get_headers() -> Dict[str, str]:
    cfg = _get_supabase_config()
    return {
        "apikey": cfg["key"],
        "Authorization": f"Bearer {cfg['key']}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


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
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ==========================================================
# INSERT
# ==========================================================

def supabase_table_insert(
    table: str,
    data: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    cfg = _get_supabase_config()
    url = f"{cfg['url']}/rest/v1/{table}"

    try:
        r = requests.post(url, headers=_get_headers(), json=data, timeout=10)
        r.raise_for_status()
        res = r.json()
        return res[0] if res else None
    except Exception:
        return None


# ==========================================================
# UPDATE
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
        r = requests.patch(url, headers=_get_headers(), params=params, json=data, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ==========================================================
# DELETE
# ==========================================================

def supabase_table_delete(
    table: str,
    filters: Dict[str, Any],
) -> bool:
    cfg = _get_supabase_config()
    url = f"{cfg['url']}/rest/v1/{table}"
    params = {k: f"eq.{v}" for k, v in filters.items()}

    try:
        r = requests.delete(url, headers=_get_headers(), params=params, timeout=10)
        r.raise_for_status()
        return True
    except Exception:
        return False


# ==========================================================
# Teste de conexão
# ==========================================================

def testar_conexao() -> bool:
    return supabase_table_select("usuarios", limit=1) is not None

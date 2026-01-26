# backend/database/__init__.py

from .supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
    testar_conexao,
)

__all__ = [
    "supabase_table_select",
    "supabase_table_insert",
    "supabase_table_update",
    "supabase_table_delete",
    "testar_conexao",
]

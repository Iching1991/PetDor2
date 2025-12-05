# PetDor2/backend/database/__init__.py
"""
Pacote de acesso ao banco de dados Supabase.
Reexporta funções do supabase_client para facilitar importações no projeto.
"""

from .supabase_client import (
    get_supabase,
    testar_conexao,
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

__all__ = [
    "get_supabase",
    "testar_conexao",
    "supabase_table_select",
    "supabase_table_insert",
    "supabase_table_update",
    "supabase_table_delete",
]

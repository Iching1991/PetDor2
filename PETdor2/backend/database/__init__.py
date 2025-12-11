# PETdor2/backend/database/__init__.py

"""
Inicializa e exporta funcionalidades do módulo de banco de dados.
Este arquivo garante que funções importantes fiquem disponíveis
para importações no restante do projeto.
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

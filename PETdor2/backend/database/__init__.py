"""
Exports do módulo de banco de dados — PETDor2
Centraliza acesso ao Supabase.
Evita circular imports.
"""

# ==========================================================
# Cliente Supabase
# ==========================================================

from .supabase_client import (
    supabase,          # Client padrão (publishable key)
    supabase_admin,   # Client admin (service role)
    get_supabase_client,
)

# ==========================================================
# Operações REST helper
# ==========================================================

from .supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
    testar_conexao,
)

# ==========================================================
# Export público
# ==========================================================

__all__ = [
    # Clients
    "supabase",
    "supabase_admin",
    "get_supabase_client",

    # Helpers REST
    "supabase_table_select",
    "supabase_table_insert",
    "supabase_table_update",
    "supabase_table_delete",
    "testar_conexao",
]

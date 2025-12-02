# PetDor2/backend/database/__init__.py
"""
Módulo de banco de dados do PETDor.
Centraliza o cliente Supabase e funções helper.
"""
# Importa as funções do cliente Supabase
from .supabase_client import ( # Importação relativa dentro do pacote 'database'
    get_supabase,
    testar_conexao,
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

# Define quais funções serão expostas quando alguém fizer 'from database import ...'
__all__ = [
    "get_supabase",
    "testar_conexao",
    "supabase_table_select",
    "supabase_table_insert",
    "supabase_table_update",
    "supabase_table_delete",
]

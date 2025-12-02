# PetDor2/backend/database/__init__.py
"""
Pacote de acesso ao banco de dados Supabase.
Expõe funções do supabase_client para importação simplificada.
"""
# Importa as funções diretamente do módulo supabase_client
from .supabase_client import (
    get_supabase,
    testar_conexao,
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)

# Define quais funções serão expostas quando o pacote 'database' for importado
__all__ = [
    "get_supabase",
    "testar_conexao",
    "supabase_table_select",
    "supabase_table_insert",
    "supabase_table_update",
    "supabase_table_delete",
]

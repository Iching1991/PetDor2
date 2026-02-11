"""
Backend PETDor2
Inicialização leve (sem imports circulares)
"""
from .supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
    testar_conexao,
)

# Não importar módulos inteiros aqui
# Apenas expor namespaces se necessário

__all__ = [
    "auth",
    "database",
    "utils",
    "especies",
]


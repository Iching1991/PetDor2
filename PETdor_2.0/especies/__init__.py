# PETdor_2.0/especies/__init__.py
...
from .index import ( # <-- Importa diretamente de index
    EspecieConfig,
    Pergunta,
    listar_especies,
    buscar_especie_por_id, # This is the one!
    get_especies_nomes
)
...
__all__ = [
    "EspecieConfig",
    "Pergunta",
    "listar_especies",
    "buscar_especie_por_id",
    "get_especies_nomes"
]

# PETdor_2.0/especies/__init__.py

"""
Pacote para gerenciamento de configurações de espécies.
Define as estruturas de dados para perguntas e configurações de espécies,
e gerencia o registro e acesso a essas configurações.
"""

from .index import ( # <-- Importa diretamente de index
    EspecieConfig,
    Pergunta,
    listar_especies,
    buscar_especie_por_id, # <-- CORREÇÃO: Importa buscar_especie_por_id
    get_especies_nomes
)

# Opcional: definir __all__ para controle de importação
__all__ = [
    "EspecieConfig",
    "Pergunta",
    "listar_especies",
    "buscar_especie_por_id", # <-- CORREÇÃO: Expõe buscar_especie_por_id
    "get_especies_nomes"
]

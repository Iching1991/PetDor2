# PETdor2/backend/especies/loader.py

"""
Módulo para carregar e gerenciar dados de espécies.
Camada de acesso (facade) para o backend.
"""

from .index import (
    listar_especies as _listar_especies,
    get_especies_nomes,
    get_especies_ids,
    buscar_especie_por_id,
)


def listar_especies():
    """
    Retorna a lista completa de espécies (configs).
    """
    return _listar_especies()


def listar_nomes_especies():
    """
    Retorna apenas os nomes das espécies (para selects simples).
    """
    return get_especies_nomes()


def listar_ids_especies():
    """
    Retorna apenas os IDs das espécies.
    """
    return get_especies_ids()


def obter_especie(especie_id: str):
    """
    Retorna a configuração completa de uma espécie.
    """
    return buscar_especie_por_id(especie_id)


__all__ = [
    "listar_especies",
    "listar_nomes_especies",
    "listar_ids_especies",
    "obter_especie",
]

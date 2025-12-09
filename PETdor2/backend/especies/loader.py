# PETdor2/backend/especies/loader.py

"""
Módulo para carregar e gerenciar dados de espécies.
"""
# -------------------------------------------------------------------
# A importação de .index está correta, pois get_especies_nomes reside lá.
# O importante é garantir que o index.py seja executado (importado)
# em algum ponto do app para que as espécies sejam registradas.
# -------------------------------------------------------------------
from .index import get_especies_nomes


def listar_especies():
    """
    Retorna uma lista de nomes de espécies disponíveis para seleção.
    """
    return get_especies_nomes()

# Exemplo de uso (opcional, para testes)
if __name__ == "__main__":
    # Para que este teste funcione, o index.py precisa ter sido executado
    # e registrado as espécies. Em um ambiente de app, a importação
    # do pacote backend.especies já cuidaria disso.
    print("Espécies listadas pelo loader:", listar_especies())

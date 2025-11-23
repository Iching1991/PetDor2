# PETdor2/especies/index.py

"""
Sistema central de registro e consulta das espécies e suas configurações.
Cada espécie deve fornecer um dicionário com a estrutura:

{
    "id": "cao",
    "nome": "Cães",
    "categorias": [
        {
            "nome": "Comportamento",
            "perguntas": [
                { "texto": "Está ativo?", "escala": "0-3" }
            ]
        }
    ]
}
"""

from typing import Dict, List, Optional

# Onde todas as espécies são armazenadas
_ESPECIES_REGISTRADAS: Dict[str, dict] = {}


# ==========================================================
# Funções de registro e busca
# ==========================================================
def registrar_especie(config: dict):
    """
    Registra a configuração de uma espécie.
    A configuração DEVE conter:
        - id (str)
        - nome (str)
        - categorias (list)
    """
    especie_id = config.get("id")

    if not especie_id:
        raise ValueError("Configuração de espécie inválida: falta o campo 'id'.")

    if especie_id in _ESPECIES_REGISTRADAS:
        raise ValueError(f"Espécie com ID '{especie_id}' já registrada.")

    _ESPECIES_REGISTRADAS[especie_id] = config


def buscar_especie_por_id(especie_id: str) -> Optional[dict]:
    """Retorna a configuração completa da espécie."""
    return _ESPECIES_REGISTRADAS.get(especie_id)


def listar_especies() -> List[dict]:
    """Lista todas as espécies registradas."""
    return list(_ESPECIES_REGISTRADAS.values())


def get_especies_nomes() -> List[str]:
    """Retorna somente os nomes das espécies registradas."""
    return [config["nome"] for config in _ESPECIES_REGISTRADAS.values()]


def get_escala_labels(escala: str) -> List[str]:
    """
    Retorna os labels de uma escala.
    Exemplo:
        "0-3" → ["0", "1", "2", "3"]
        "sim-nao" → ["Sim", "Não"]
    """

    escala = escala.lower().strip()

    if escala == "sim-nao":
        return ["Sim", "Não"]

    if "-" in escala:
        inicio, fim = escala.split("-")
        return [str(i) for i in range(int(inicio), int(fim) + 1)]

    raise ValueError(f"Escala desconhecida: {escala}")


# ==========================================================
# Importar e registrar automaticamente todas as espécies
# ==========================================================

from .cao import CONFIG_CAES
from .gato import CONFIG_GATOS
from .coelho import CONFIG_COELHO
from .porquinho import CONFIG_PORQUINHO
from .aves import CONFIG_AVES
from .repteis import CONFIG_REPTEIS

registrar_especie(CONFIG_CAES)
registrar_especie(CONFIG_GATOS)
registrar_especie(CONFIG_COELHO)
registrar_especie(CONFIG_PORQUINHO)
registrar_especie(CONFIG_AVES)
registrar_especie(CONFIG_REPTEIS)

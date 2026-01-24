"""
Sistema central de registro e consulta das espécies.
Modelo COMPLETO (categorias + perguntas).
"""

import logging
from typing import Dict, List, Optional, Union
from importlib import import_module

from .base import EspecieConfig, Categoria, Pergunta

logger = logging.getLogger(__name__)

# ==========================================================
# Registro interno
# ==========================================================

_ESPECIES_REGISTRADAS: Dict[str, dict] = {}

# ==========================================================
# Registro e consulta
# ==========================================================

def registrar_especie(config: Union[EspecieConfig, dict]) -> None:
    if isinstance(config, EspecieConfig):
        config = config.to_dict()

    especie_id = config.get("id")
    nome = config.get("nome")
    categorias = config.get("categorias")

    if not especie_id or not nome or not categorias:
        raise ValueError(
            "Configuração de espécie inválida. "
            "Campos obrigatórios: id, nome, categorias."
        )

    if especie_id in _ESPECIES_REGISTRADAS:
        logger.warning(f"⚠️ Espécie '{especie_id}' já registrada. Atualizando...")

    _ESPECIES_REGISTRADAS[especie_id] = config
    logger.info(f"✅ Espécie '{nome}' registrada com sucesso")


def buscar_especie_por_id(especie_id: str) -> Optional[dict]:
    return _ESPECIES_REGISTRADAS.get(especie_id)


def listar_especies() -> List[dict]:
    return list(_ESPECIES_REGISTRADAS.values())


def get_especies_nomes() -> List[str]:
    return [config["nome"] for config in _ESPECIES_REGISTRADAS.values()]


def get_especies_ids() -> List[str]:
    return list(_ESPECIES_REGISTRADAS.keys())


# ==========================================================
# Escalas
# ==========================================================

def get_escala_labels(escala: str) -> List[str]:
    escala = escala.lower().strip()

    if escala == "sim-nao":
        return ["Não", "Sim"]

    if "-" in escala:
        inicio, fim = escala.split("-")
        return [str(i) for i in range(int(inicio), int(fim) + 1)]

    raise ValueError(f"Escala desconhecida: {escala}")


# ==========================================================
# Streamlit helper
# ==========================================================

def carregar_especies() -> List[dict]:
    return listar_especies()


# ==========================================================
# Importação automática das espécies
# ==========================================================

ESPECIES_IMPORTS = {
    "cao": "CONFIG_CAES",
    "gato": "CONFIG_GATOS",
    "coelho": "CONFIG_COELHO",
    "porquinho_da_india": "CONFIG_PORQUINHO_DA_INDIA",
    "aves": "CONFIG_AVES",
    "repteis": "CONFIG_REPTEIS",
}

for modulo, attr in ESPECIES_IMPORTS.items():
    try:
        mod = import_module(f"backend.especies.{modulo}")
        registrar_especie(getattr(mod, attr))
    except Exception as e:
        logger.error(f"❌ Erro ao registrar espécie '{modulo}': {e}")

logger.info(f"✅ Total de espécies registradas: {len(_ESPECIES_REGISTRADAS)}")

__all__ = [
    "EspecieConfig",
    "Categoria",
    "Pergunta",
    "registrar_especie",
    "buscar_especie_por_id",
    "listar_especies",
    "get_especies_nomes",
    "get_especies_ids",
    "get_escala_labels",
    "carregar_especies",
]

"""
Sistema central de registro e consulta das espécies e suas configurações.
Compatível com MODELO COMPLETO (categorias + perguntas).
"""

import logging
from typing import Dict, List, Optional, Union
from .base import EspecieConfig, Categoria, Pergunta

logger = logging.getLogger(__name__)

# ==========================================================
# Registro interno
# ==========================================================
_ESPECIES_REGISTRADAS: Dict[str, dict] = {}

# ==========================================================
# Funções de registro e busca
# ==========================================================

def registrar_especie(config: Union[EspecieConfig, dict]) -> None:
    """
    Registra a configuração de uma espécie.
    Aceita EspecieConfig (dataclass) ou dict já normalizado.
    """
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
    """Retorna a configuração completa da espécie."""
    return _ESPECIES_REGISTRADAS.get(especie_id)


def listar_especies() -> List[dict]:
    """Lista todas as espécies registradas."""
    return list(_ESPECIES_REGISTRADAS.values())


def get_especies_nomes() -> List[str]:
    """Retorna somente os nomes das espécies registradas."""
    return [config["nome"] for config in _ESPECIES_REGISTRADAS.values()]


def get_especies_ids() -> List[str]:
    """Retorna somente os IDs das espécies registradas."""
    return list(_ESPECIES_REGISTRADAS.keys())


# ==========================================================
# Escalas
# ==========================================================

def get_escala_labels(escala: str) -> List[str]:
    """
    Retorna os labels de uma escala.
    Exemplo:
        "0-7" → ["0", "1", ..., "7"]
        "sim-nao" → ["Não", "Sim"]
    """
    escala = escala.lower().strip()

    if escala == "sim-nao":
        return ["Não", "Sim"]

    if "-" in escala:
        try:
            inicio, fim = escala.split("-")
            return [str(i) for i in range(int(inicio), int(fim) + 1)]
        except ValueError:
            logger.error(f"Escala inválida: {escala}")
            raise ValueError(f"Escala inválida: {escala}")

    raise ValueError(f"Escala desconhecida: {escala}")


# ==========================================================
# Função para Streamlit
# ==========================================================

def carregar_especies() -> List[dict]:
    """Retorna todas as espécies registradas (para UI)."""
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

for modulo, config_attr in ESPECIES_IMPORTS.items():
    try:
        mod = __import__(f".{modulo}", globals(), locals(), [config_attr])
        registrar_especie(getattr(mod, config_attr))
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

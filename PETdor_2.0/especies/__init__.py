from .index import get_especies_nomes, get_especie_config

# Importa configurações individuais das espécies
from .gato import CONFIG_GATOS
from .coelho import CONFIG_COELHO
from .porquinho_india import CONFIG_PORQUINHO
from .aves import CONFIG_AVES
from .repteis import CONFIG_REPTEIS

__all__ = [
    "get_especies_nomes",
    "get_especie_config",
    "CONFIG_GATOS",
    "CONFIG_COELHO",
    "CONFIG_PORQUINHO",
    "CONFIG_AVES",
    "CONFIG_REPTEIS",
]

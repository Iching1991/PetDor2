# PETdor_2.0/especies/index.py

"""
Sistema de registro e gerenciamento das espécies utilizadas no PETdor.
Substitui totalmente o antigo base.py
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

# -----------------------------
# 🧩 Estruturas de dados
# -----------------------------

@dataclass
class Pergunta:
    texto: str
    invertida: bool = False
    peso: float = 1.0


@dataclass
class EspecieConfig:
    nome: str
    especie_id: str # Adicionei especie_id para ser consistente com o que você usa em cao.py
    descricao: str
    opcoes_escala: List[str]
    perguntas: List[Pergunta]


# -----------------------------
# 📦 Registro global de espécies
# -----------------------------
_ESPECIES: Dict[str, EspecieConfig] = {}


def registrar_especie(config: EspecieConfig):
    """Registra uma espécie no sistema."""
    nome_normalizado = config.nome.strip().lower()
    _ESPECIES[nome_normalizado] = config


def get_especies_nomes() -> List[str]:
    """Retorna lista de nomes das espécies disponíveis."""
    return [config.nome for config in _ESPECIES.values()]


def get_especie_config(nome: str) -> Optional[EspecieConfig]:
    """Obtém uma configuração de espécie pelo nome."""
    return _ESPECIES.get(nome.strip().lower())


# -----------------------------
# 🔄 Importa e registra automaticamente todas as espécies
# -----------------------------
from .gato import CONFIG_GATOS
from .cao import CONFIG_CAES # <-- Adicionado: Importa a configuração de cães
from .coelho import CONFIG_COELHO
from .porquinho_india import CONFIG_PORQUINHO
from .aves import CONFIG_AVES
from .repteis import CONFIG_REPTEIS

registrar_especie(CONFIG_GATOS)
registrar_especie(CONFIG_CAES) # <-- Adicionado: Registra a configuração de cães
registrar_especie(CONFIG_COELHO)
registrar_especie(CONFIG_PORQUINHO)
registrar_especie(CONFIG_AVES)
registrar_especie(CONFIG_REPTEIS)

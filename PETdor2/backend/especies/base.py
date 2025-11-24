# PETdor2/especies/base.py
"""
Definições base para configuração de espécies e perguntas.
"""
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class Pergunta:
    """Representa uma pergunta na avaliação de dor."""
    texto: str
    invertida: bool = False
    peso: float = 1.0
    escala: str = "0-7"

    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return asdict(self)

@dataclass
class EspecieConfig:
    """Configuração de uma espécie com suas categorias e perguntas."""
    nome: str
    especie_id: str
    descricao: str
    opcoes_escala: List[str]
    perguntas: List[Pergunta]

    def to_dict(self) -> dict:
        """Converte para dicionário compatível com o sistema de registro."""
        return {
            "id": self.especie_id,
            "nome": self.nome,
            "descricao": self.descricao,
            "opcoes_escala": self.opcoes_escala,
            "perguntas": [p.to_dict() for p in self.perguntas],
        }

__all__ = ["Pergunta", "EspecieConfig"]

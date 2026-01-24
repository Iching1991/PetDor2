# backend/especies/base.py

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Pergunta:
    id: str
    texto: str
    escala: str
    peso: float = 1.0


@dataclass
class Categoria:
    id: str
    nome: str
    perguntas: List[Pergunta]


@dataclass
class EspecieConfig:
    id: str
    nome: str
    categorias: List[Categoria]
    limites_dor: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "categorias": [
                {
                    "id": c.id,
                    "nome": c.nome,
                    "perguntas": [p.__dict__ for p in c.perguntas],
                }
                for c in self.categorias
            ],
            "limites_dor": self.limites_dor,
        }


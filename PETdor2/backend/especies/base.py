from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Pergunta:
    id: str
    texto: str
    escala: str        # Ex: "0-7", "sim-nao"
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

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "categorias": [
                {
                    "id": c.id,
                    "nome": c.nome,
                    "perguntas": [
                        {
                            "id": p.id,
                            "texto": p.texto,
                            "escala": p.escala,
                            "peso": p.peso,
                        }
                        for p in c.perguntas
                    ],
                }
                for c in self.categorias
            ],
            "limites_dor": self.limites_dor,
        }

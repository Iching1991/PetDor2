# PETdor2/backend/especies/repteis.py

"""
🦎 Configuração de avaliação para RÉPTEIS
⚠ Avaliação ainda em desenvolvimento
Compatível com MODELO COMPLETO (Opção A)
"""

from .base import EspecieConfig, Categoria, Pergunta


CONFIG_REPTEIS = EspecieConfig(
    id="repteis",
    nome="Répteis",
    categorias=[
        Categoria(
            id="em_desenvolvimento",
            nome="Avaliação em desenvolvimento",
            perguntas=[
                Pergunta(
                    id="avaliacao_indisponivel",
                    texto="A avaliação de dor para répteis ainda está em desenvolvimento.",
                    escala="0-0",
                    peso=0.0,
                )
            ],
        )
    ],
)

__all__ = ["CONFIG_REPTEIS"]

# PETdor2/backend/especies/aves.py

"""
🦜 Configuração de avaliação para AVES.
Escala: 0 a 7 — baseada em observação comportamental geral.
"""

from .base import EspecieConfig, Categoria, Pergunta


CONFIG_AVES = EspecieConfig(
    id="aves",
    nome="Aves",
    categorias=[
        Categoria(
            id="postura_mobilidade",
            nome="Postura e Mobilidade",
            perguntas=[
                Pergunta(
                    id="postura_anormal",
                    texto="Minha ave está com postura anormal (arrepiada, encolhida)?",
                    escala="0-7",
                ),
                Pergunta(
                    id="reduziu_movimento",
                    texto="Minha ave reduziu a movimentação ou não voa mais?",
                    escala="0-7",
                ),
            ],
        ),
        Categoria(
            id="alimentacao",
            nome="Alimentação e Hábito",
            perguntas=[
                Pergunta(
                    id="come_menos",
                    texto="Minha ave está comendo menos?",
                    escala="0-7",
                ),
                Pergunta(
                    id="bebe_menos",
                    texto="Minha ave bebe menos água?",
                    escala="0-7",
                ),
            ],
        ),
        Categoria(
            id="comportamento",
            nome="Comportamento",
            perguntas=[
                Pergunta(
                    id="vocalizacao_alterada",
                    texto="Minha ave vocaliza menos ou de forma diferente?",
                    escala="0-7",
                ),
                Pergunta(
                    id="agressividade",
                    texto="Minha ave evita contato ou fica mais agressiva?",
                    escala="0-7",
                ),
            ],
        ),
        Categoria(
            id="aparencia",
            nome="Aparência",
            perguntas=[
                Pergunta(
                    id="penas_eriçadas",
                    texto="Minha ave está com penas eriçadas ou desalinhadas?",
                    escala="0-7",
                ),
                Pergunta(
                    id="inatividade",
                    texto="Minha ave fica muito tempo parada no mesmo lugar?",
                    escala="0-7",
                ),
            ],
        ),
    ],
)

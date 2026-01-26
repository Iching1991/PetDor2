# PETdor2/backend/especies/porquinho_da_india.py

"""
🐹 Configuração de avaliação de dor para PORQUINHOS-DA-ÍNDIA
Escala: 0 a 7 — baseada em sinais comportamentais e clínicos.
"""

from .base import EspecieConfig, Categoria, Pergunta


CONFIG_PORQUINHO_DA_INDIA = EspecieConfig(
    id="porquinho_da_india",
    nome="Porquinho-da-Índia",
    categorias=[
        # --------------------------------------------------
        # Postura e Movimentação
        # --------------------------------------------------
        Categoria(
            id="postura_movimento",
            nome="Postura e Movimentação",
            perguntas=[
                Pergunta(
                    id="curvado_imovel",
                    texto="Meu porquinho-da-índia está curvado ou imóvel por longos períodos",
                    escala="0-7",
                ),
                Pergunta(
                    id="atividade_reduzida",
                    texto="Meu porquinho-da-índia reduziu suas atividades diárias",
                    escala="0-7",
                ),
                Pergunta(
                    id="evita_explorar",
                    texto="Meu porquinho-da-índia evita correr ou explorar o ambiente",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Alimentação
        # --------------------------------------------------
        Categoria(
            id="alimentacao",
            nome="Alimentação",
            perguntas=[
                Pergunta(
                    id="apetite_reduzido",
                    texto="O apetite diminuiu ou ele está comendo mais devagar",
                    escala="0-7",
                ),
                Pergunta(
                    id="agua_reduzida",
                    texto="O consumo de água diminuiu",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Vocalização e Comportamento
        # --------------------------------------------------
        Categoria(
            id="vocalizacao_comportamento",
            nome="Vocalização e Comportamento",
            perguntas=[
                Pergunta(
                    id="vocalizacao_diferente",
                    texto="Ele vocaliza de forma diferente (gritos, chiados ou sons incomuns)",
                    escala="0-7",
                ),
                Pergunta(
                    id="dor_ao_toque",
                    texto="Ele reage com dor ao toque ou à manipulação",
                    escala="0-7",
                ),
                Pergunta(
                    id="se_esconde",
                    texto="Ele se esconde mais do que o habitual",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Aparência Geral
        # --------------------------------------------------
        Categoria(
            id="aparencia_geral",
            nome="Aparência Geral",
            perguntas=[
                Pergunta(
                    id="pelo_desalinhado",
                    texto="Ele está menos limpo ou com os pelos arrepiados",
                    escala="0-7",
                ),
                Pergunta(
                    id="respiracao_alterada",
                    texto="A respiração parece mais rápida ou difícil",
                    escala="0-7",
                ),
            ],
        ),
    ],
)

__all__ = ["CONFIG_PORQUINHO_DA_INDIA"]

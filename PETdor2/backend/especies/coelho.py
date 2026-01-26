# PETdor2/backend/especies/coelho.py

"""
🐇 Configuração de avaliação para COELHOS
Escala: 0 a 7 — baseada no Rabbit Grimace Scale e parâmetros comportamentais.
"""

from .base import EspecieConfig, Categoria, Pergunta


CONFIG_COELHO = EspecieConfig(
    id="coelho",
    nome="Coelho",
    categorias=[
        # --------------------------------------------------
        # Postura e Movimentação
        # --------------------------------------------------
        Categoria(
            id="postura_movimentacao",
            nome="Postura e Movimentação",
            perguntas=[
                Pergunta(
                    id="postura_anormal",
                    texto="Meu coelho está com postura anormal (curvado ou imóvel)?",
                    escala="0-7",
                ),
                Pergunta(
                    id="menos_ativo",
                    texto="Meu coelho está menos ativo ou se movimenta pouco?",
                    escala="0-7",
                ),
                Pergunta(
                    id="evita_saltar",
                    texto="Meu coelho evita saltar ou explorar o ambiente?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Expressão Facial
        # --------------------------------------------------
        Categoria(
            id="expressao_facial",
            nome="Expressão Facial",
            perguntas=[
                Pergunta(
                    id="olhos_semicerrados",
                    texto="Meu coelho apresenta olhos semicerrados ou expressão tensa?",
                    escala="0-7",
                ),
                Pergunta(
                    id="tensao_facial",
                    texto="As bochechas ou o nariz parecem tensos ou retraídos?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Alimentação e Higiene
        # --------------------------------------------------
        Categoria(
            id="alimentacao_higiene",
            nome="Alimentação e Higiene",
            perguntas=[
                Pergunta(
                    id="apetite_reduzido",
                    texto="O apetite do meu coelho reduziu?",
                    escala="0-7",
                ),
                Pergunta(
                    id="menos_agua",
                    texto="Meu coelho reduziu a ingestão de água?",
                    escala="0-7",
                ),
                Pergunta(
                    id="menos_higiene",
                    texto="Meu coelho está menos limpo ou parou de se lamber?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Comportamento e Interação
        # --------------------------------------------------
        Categoria(
            id="comportamento_interacao",
            nome="Comportamento e Interação",
            perguntas=[
                Pergunta(
                    id="se_esconde",
                    texto="Meu coelho se esconde mais do que o normal?",
                    escala="0-7",
                ),
                Pergunta(
                    id="reage_dor_toque",
                    texto="Meu coelho reage com dor quando é tocado?",
                    escala="0-7",
                ),
            ],
        ),
    ],
)

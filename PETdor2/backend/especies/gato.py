# PETdor2/backend/especies/gato.py

"""
🐈 Configuração de avaliação de dor para GATOS.
Escala: 0 a 7 — baseada em escalas de dor felina.
"""

from .base import EspecieConfig, Categoria, Pergunta


CONFIG_GATOS = EspecieConfig(
    id="gato",
    nome="Gato",
    categorias=[
        # --------------------------------------------------
        # Comportamento Geral
        # --------------------------------------------------
        Categoria(
            id="comportamento_geral",
            nome="Comportamento Geral",
            perguntas=[
                Pergunta(
                    id="menos_ativo",
                    texto="O gato está mais quieto ou menos ativo?",
                    escala="0-7",
                ),
                Pergunta(
                    id="mudanca_apetite",
                    texto="Há mudanças no apetite ou no consumo de água?",
                    escala="0-7",
                ),
                Pergunta(
                    id="evita_interacao",
                    texto="O gato está se escondendo ou evitando interação?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Mobilidade
        # --------------------------------------------------
        Categoria(
            id="mobilidade",
            nome="Mobilidade",
            perguntas=[
                Pergunta(
                    id="dificuldade_pular",
                    texto="Há dificuldade para pular, subir ou se mover?",
                    escala="0-7",
                ),
                Pergunta(
                    id="lambe_dor",
                    texto="O gato está lambendo ou mordendo excessivamente alguma parte do corpo?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Postura e Expressão Facial
        # --------------------------------------------------
        Categoria(
            id="postura_expressao",
            nome="Postura e Expressão Facial",
            perguntas=[
                Pergunta(
                    id="postura_anormal",
                    texto="Há alterações na postura (ex: encurvado ou cabeça baixa)?",
                    escala="0-7",
                ),
                Pergunta(
                    id="expressao_tensa",
                    texto="O gato está com os olhos semicerrados ou com a face tensa?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Vocalização
        # --------------------------------------------------
        Categoria(
            id="vocalizacao",
            nome="Vocalização",
            perguntas=[
                Pergunta(
                    id="mudanca_vocalizacao",
                    texto="O gato está vocalizando mais ou menos do que o habitual?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Higiene
        # --------------------------------------------------
        Categoria(
            id="higiene",
            nome="Higiene",
            perguntas=[
                Pergunta(
                    id="higiene_alterada",
                    texto="Há mudanças nos hábitos de higiene (ex: pelo desgrenhado)?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Sono
        # --------------------------------------------------
        Categoria(
            id="sono",
            nome="Sono",
            perguntas=[
                Pergunta(
                    id="sono_alterado",
                    texto="O gato está dormindo mais ou em posições incomuns?",
                    escala="0-7",
                ),
            ],
        ),
    ],
)

# PETdor2/backend/especies/cao.py

"""
🐕 Configuração de avaliação para CÃES.
Escala: 0 a 7 (baseada em CBPI e Glasgow Composite Pain Scale).
"""

from .base import EspecieConfig, Categoria, Pergunta


CONFIG_CAES = EspecieConfig(
    id="cao",
    nome="Cachorro",
    categorias=[
        # --------------------------------------------------
        # Energia e Atividade
        # --------------------------------------------------
        Categoria(
            id="energia_atividade",
            nome="Energia e Atividade",
            perguntas=[
                Pergunta(
                    id="pouca_energia",
                    texto="Meu cão teve pouca energia?",
                    escala="0-7",
                ),
                Pergunta(
                    id="brincalhao",
                    texto="Meu cão foi brincalhão?",
                    escala="0-7",
                ),
                Pergunta(
                    id="atividades_favoritas",
                    texto="Meu cão fez as suas atividades favoritas?",
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
                    texto="O apetite do meu cão reduziu?",
                    escala="0-7",
                ),
                Pergunta(
                    id="comeu_normalmente",
                    texto="Meu cão comeu normalmente a sua comida favorita?",
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
                    id="reluta_levantar",
                    texto="Meu cão reluta para levantar?",
                    escala="0-7",
                ),
                Pergunta(
                    id="dificuldade_levantar_deitar",
                    texto="Meu cão teve problemas para levantar-se ou deitar-se?",
                    escala="0-7",
                ),
                Pergunta(
                    id="dificuldade_caminhar",
                    texto="Meu cão teve problemas para caminhar?",
                    escala="0-7",
                ),
                Pergunta(
                    id="perda_equilibrio",
                    texto="Meu cão caiu ou perdeu o equilíbrio?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Comportamento Social
        # --------------------------------------------------
        Categoria(
            id="comportamento_social",
            nome="Comportamento Social",
            perguntas=[
                Pergunta(
                    id="gosta_proximidade",
                    texto="Meu cão gosta de estar perto de mim?",
                    escala="0-7",
                ),
                Pergunta(
                    id="afeto_normal",
                    texto="Meu cão mostrou uma quantidade normal de afeto?",
                    escala="0-7",
                ),
                Pergunta(
                    id="aceita_toque",
                    texto="Meu cão gostou de ser tocado ou acariciado?",
                    escala="0-7",
                ),
            ],
        ),

        # --------------------------------------------------
        # Comportamento Geral
        # --------------------------------------------------
        Categoria(
            id="comportamento_geral",
            nome="Comportamento Geral",
            perguntas=[
                Pergunta(
                    id="comportamento_normal",
                    texto="Meu cão agiu normalmente?",
                    escala="0-7",
                ),
                Pergunta(
                    id="desconforto",
                    texto="Meu cão teve problemas para ficar confortável?",
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
                    id="sono_noturno",
                    texto="Meu cão dormiu bem durante a noite?",
                    escala="0-7",
                ),
            ],
        ),
    ],
)

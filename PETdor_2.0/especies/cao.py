"""
🐕 Configuração de Avaliação — CÃES
Escala: 0 a 7
Baseada na CBPI e Glasgow Composite Pain Scale.
"""

from especies.index import EspecieConfig, Pergunta

CONFIG_CAES = EspecieConfig(
    nome="Cachorro",
    especie_id="cao",
    descricao="Escala comportamental para avaliação de dor em cães (0 = nunca, 7 = sempre).",

    opcoes_escala=[
        "0 - Nunca",
        "1 - Raramente",
        "2 - Às vezes",
        "3 - Frequentemente",
        "4 - Quase Sempre",
        "5 - Sempre",
        "6 - Muito Frequente",
        "7 - Constante",
    ],

    perguntas=[

        # ------------------------------
        # Energia e Atividade
        # ------------------------------

        # 1 — Energia baixa = MAIS DOR → alto valor = pior → NÃO inverte
        Pergunta(
            texto="Meu cão apresentou pouca energia",
            invertida=False,
            peso=1.0
        ),

        # 2 — Brincalhão = comportamento positivo → baixo valor = pior → inverter
        Pergunta(
            texto="Meu cão foi brincalhão",
            invertida=True,
            peso=1.0
        ),

        # 3 — Atividades favoritas = positivo → baixo valor = pior → inverter
        Pergunta(
            texto="Meu cão realizou suas atividades favoritas",
            invertida=True,
            peso=1.0
        ),

        # ------------------------------
        # Alimentação
        # ------------------------------

        # 4 — Redução de apetite = dor → alto = pior → NÃO inverte
        Pergunta(
            texto="O apetite do meu cão reduziu",
            invertida=False,
            peso=1.0
        ),

        # 5 — Comer normalmente é positivo → baixo = pior → inverter
        Pergunta(
            texto="Meu cão comeu normalmente sua comida favorita",
            invertida=True,
            peso=1.0
        ),

        # ------------------------------
        # Mobilidade
        # ------------------------------

        Pergunta(
            texto="Meu cão relutou ao tentar se levantar",
            invertida=False,
            peso=1.0
        ),
        Pergunta(
            texto="Meu cão teve dificuldade para levantar-se ou deitar-se",
            invertida=False,
            peso=1.0
        ),
        Pergunta(
            texto="Meu cão apresentou dificuldade para caminhar",
            invertida=False,
            peso=1.0
        ),
        Pergunta(
            texto="Meu cão caiu ou perdeu o equilíbrio",
            invertida=False,
            peso=1.0
        ),

        # ------------------------------
        # Comportamento Social
        # ------------------------------

        Pergunta(
            texto="Meu cão gostou de estar perto de mim",
            invertida=True,
            peso=1.0
        ),
        Pergunta(
            texto="Meu cão demonstrou uma quantidade normal de afeto",
            invertida=True,
            peso=1.0
        ),
        Pergunta(
            texto="Meu cão gostou de ser tocado ou acariciado",
            invertida=True,
            peso=1.0
        ),

        # ------------------------------
        # Comportamento Geral
        # ------------------------------

        Pergunta(
            texto="Meu cão agiu normalmente",
            invertida=True,
            peso=1.0
        ),
        Pergunta(
            texto="Meu cão teve dificuldade para ficar confortável",
            invertida=False,
            peso=1.0
        ),

        # ------------------------------
        # Sono
        # ------------------------------

        Pergunta(
            texto="Meu cão dormiu bem durante a noite",
            invertida=True,
            peso=1.0
        ),
    ],
)

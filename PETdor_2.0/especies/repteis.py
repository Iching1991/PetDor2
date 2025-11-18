"""
🦎 Configuração de avaliação para RÉPTEIS
⚠ Em construção — avaliação especializada ainda não disponível.
"""
from especies.index import EspecieConfig, Pergunta

CONFIG_REPTEIS = EspecieConfig(
    nome="Répteis",
    descricao="Avaliação de dor em répteis — Em construção.",
    opcoes_escala=["0 - Em desenvolvimento"],
    perguntas=[
        Pergunta(texto="Avaliação para esta espécie ainda está em desenvolvimento.", invertida=False, peso=0.0)
    ]
)

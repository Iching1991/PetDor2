"""
Pacote utilitário do PETDor2.
Expondo funções e helpers gerais de forma explícita.
"""

# Importações nomeadas
from .petdor import format_pet_nome, calcular_idade_pet
from .validators import validar_email, validar_cpf
from .notifications import enviar_email, enviar_sms
from .utils import gerar_token, formatar_data
from .config import CONFIG, EMAIL_SETTINGS

# Lista explícita de nomes exportados
__all__ = [
    "format_pet_nome",
    "calcular_idade_pet",
    "validar_email",
    "validar_cpf",
    "enviar_email",
    "enviar_sms",
    "gerar_token",
    "formatar_data",
    "CONFIG",
    "EMAIL_SETTINGS",
]

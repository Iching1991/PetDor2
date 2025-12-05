"""
Pacote de páginas da aplicação PETDor2.

Centraliza todas as páginas do Streamlit,
evitando importações circulares e facilitando organização.
"""

# Importações explícitas dos módulos
from . import login
from . import cadastro
from . import cadastro_pet
from . import avaliacao
from . import admin
from . import home

# Quais páginas estão disponíveis publicamente
__all__ = [
    "login",
    "cadastro",
    "cadastro_pet",
    "avaliacao",
    "admin",
    "home",
]

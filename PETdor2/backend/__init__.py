"""
Pacote principal do backend do PETDor2.
Expondo subpacotes e funções principais para importações simples.
"""

from . import auth
from . import database
from . import especies
from . import pages
from . import utils

__all__ = [
    "auth",
    "database",
    "especies",
    "pages",
    "utils",
]

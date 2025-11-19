"""
Pacote de acesso ao banco de dados da aplicação PETDor.

Responsável por:
- Conexão com o banco SQLite (conectar_db)
- Criação e migração das tabelas (criar_tabelas, migrar_banco_completo)
- Funções de acesso a dados (models)
"""

from .connection import conectar_db
from .migration import criar_tabelas, migrar_banco_completo
from . import models

__all__ = [
    "conectar_db",
    "criar_tabelas",
    "migrar_banco_completo",
    "models",
]

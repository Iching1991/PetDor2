"""
Pacote de acesso ao banco de dados da aplicação PETdor2.

Este módulo inicializa o pacote 'database', permitindo acesso claro e
organizado aos submódulos:

- database.connection
- database.migration
- database.models

O pacote evita ciclos de importação: apenas módulos seguros são expostos.
"""

# Importação explícita e organizada dos submódulos
from PETdor2.database import connection
from PETdor2.database import migration
from PETdor2.database import models

# Exportações públicas do pacote
__all__ = [
    "connection",
    "migration",
    "models",
    "conectar_db",
]

# Exporta diretamente a função principal de conexão
from PETdor2.database.connection import conectar_db

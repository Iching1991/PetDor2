# PETdor_2.0/auth/__init__.py
"""
Módulo de autenticação e gerenciamento de usuários para o PETDor.
Contém funcionalidades para cadastro, login, redefinição de senha e segurança.
"""

# Não importamos os módulos aqui para evitar ciclos de importação.
# Os módulos (user, password_reset, email_confirmation, security)
# devem ser importados diretamente onde forem necessários (ex: em petdor.py, ou dentro de outros módulos do pacote 'auth').

# Definimos __all__ para indicar quais módulos fazem parte do pacote 'auth'
# quando alguém faz 'from auth import *', mas sem carregá-los imediatamente.
__all__ = [
    "user",
    "password_reset",
    "email_confirmation",
    "security",
]

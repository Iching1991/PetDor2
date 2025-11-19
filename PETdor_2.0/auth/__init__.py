# PETdor_2.0/auth/__init__.py

"""
Módulo de inicialização do pacote 'auth'.
Expõe funcionalidades de autenticação e gerenciamento de usuários.
"""

# Importa os submódulos para que possam ser acessados via auth.user, auth.password_reset, etc.
from . import user
from . import password_reset
from . import email_confirmation # Você tem email_confirmation.py na sua estrutura
from . import security # Você tem security.py na sua estrutura

__all__ = [
    "user",
    "password_reset",
    "email_confirmation", # Adicionado para expor o módulo
    "security",           # Adicionado para expor o módulo
]

# Se você *realmente* precisar expor funções específicas diretamente do pacote 'auth'
# (ex: auth.cadastrar_usuario), você pode fazer isso AQUI, mas com cuidado para não criar ciclos.
# Por exemplo, se auth.user não depende de auth.__init__ para carregar, você pode fazer:
# from .user import cadastrar_usuario, autenticar_usuario, buscar_usuario_por_id
# __all__.extend(["cadastrar_usuario", "autenticar_usuario", "buscar_usuario_por_id"])
# Mas para evitar o ciclo atual, é melhor que o petdor.py importe diretamente de auth.user
# ou auth.password_reset.

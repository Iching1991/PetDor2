# PETdor2/backend/database/__init__.py
"""
Pacote de gerenciamento de banco de dados para o PETdor2.
"""
# Remova qualquer importação de 'supabase_client' ou suas funções aqui.
# Por exemplo, se você tinha:
# from .supabase_client import testar_conexao, get_supabase
# REMOVA ESSAS LINHAS.

# Se você tiver outras funções de outros módulos dentro de 'database'
# que não dependem de 'supabase_client' e que você queira expor,
# você pode importá-las aqui. Caso contrário, deixe-o vazio.

# Para o problema atual, o mais importante é que a linha 6
# (ou qualquer linha que importe supabase_client) seja removida ou comentada.

# Exemplo de __init__.py para resolver a circularidade:
# (Pode estar vazio, ou ter outras importações que não sejam de supabase_client)
# from .migration import criar_tabelas # Exemplo de outra importação
# __all__ = ["criar_tabelas"] # Exemplo de __all__

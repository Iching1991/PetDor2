"""
Inicializa o módulo de database e expõe as funções principais.
Evita importações circulares carregando apenas o necessário.
"""

from .supabase_client import (
    criar_cliente_supabase,
    cliente_supabase,
)


def testar_conexao():
    """
    Testa a conexão com o Supabase de forma segura.
    Retorna True se conectar, False caso contrário.
    """
    try:
        client = criar_cliente_supabase()
        if not client:
            return False

        # Faz uma consulta mínima para testar
        response = client.table("usuarios").select("id").limit(1).execute()

        # Se chegou aqui sem erro → OK
        return True

    except Exception as e:
        print(f"[ERRO] Falha ao conectar ao Supabase: {e}")
        return False


__all__ = [
    "testar_conexao",
    "criar_cliente_supabase",
    "cliente_supabase",
]

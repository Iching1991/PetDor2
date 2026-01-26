def testar_conexao() -> bool:
    """
    Testa a conexão com o Supabase usando a API REST.
    """
    try:
        resultado = supabase_table_select(
            table="usuarios",
            limit=1
        )
        return resultado is not None
    except Exception as e:
        print("Erro ao testar conexão com Supabase:", e)
        return False

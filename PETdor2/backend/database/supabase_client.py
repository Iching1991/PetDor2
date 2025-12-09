  # PETdor2/backend/database/supabase_client.py  import streamlit as st
  import os
  from supabase import create_client, Client

  def get_supabase() -> Client:
      try:
          # Prioriza st.secrets no Streamlit Cloud
          if "streamlit" in os.environ.get("STREAMLIT_VERSION", ""):
              supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
              supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
          else:
              # Fallback para desenvolvimento local com .env
              supabase_url = os.getenv("SUPABASE_URL")
              supabase_key = os.getenv("SUPABASE_ANON_KEY")

          if not supabase_url or not supabase_key:
              raise RuntimeError("SUPABASE_URL ou SUPABASE_ANON_KEY não configurados. Verifique seu arquivo .env ou as variáveis de ambiente do Streamlit Cloud.")

          return create_client(supabase_url, supabase_key)
      except Exception as e:
          st.error(f"Erro ao conectar com Supabase: {e}")
          raise

  def testar_conexao():
      try:
          client = get_supabase()
          # Teste simples: lista tabelas ou faz uma query vazia
          response = client.table("usuarios").select("*").limit(0).execute()
          st.success("✅ Conexão com Supabase estabelecida com sucesso!")
          return True
      except Exception as e:
          st.error(f"❌ Falha ao testar conexão com Supabase: {e}")
          return False

  # ... resto do código (supabase_table_select, etc.)
Falha ao testar conexão com Supabase: {e}", exc_info=True)
        return False

def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None, # Adicionado para ordenação
    desc: bool = False, # Adicionado para ordenação
    single: bool = False
) -> Tuple[bool, Union[List[Dict[str, Any]], Dict[str, Any], str]]:
    """
    SELECT genérico no Supabase.
    Args:
        tabela: Nome da tabela.
        colunas: String de colunas a selecionar (ex: "id, nome, email").
        filtros: Dicionário com os filtros (ex: {"email": "teste@exemplo.com"}).
        order_by: Coluna para ordenar os resultados.
        desc: Se True, ordena em ordem decrescente.
        single: Se True, espera um único resultado.
    Returns:
        (True, dados) em caso de sucesso, (False, mensagem de erro) caso contrário.
        Dados pode ser uma lista de dicts, um único dict ou uma string de erro.
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).select(colunas)

        if filtros:
            for coluna, valor in filtros.items():
                query = query.eq(coluna, valor)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        response: APIResponse = query.execute() # Tipagem mais específica

        # Verifica se response.data é None (nenhum resultado) ou um dict/list vazio
        if response.data is None:
            return True, {} if single else [] # Retorna dict vazio para single, lista vazia para múltiplos

        return True, response.data
    except Exception as e:
        logger.error(f"Erro no SELECT em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao buscar dados: {e}"

def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    INSERT genérico no Supabase.
    Args:
        tabela: Nome da tabela.
        dados: Dicionário com os dados a inserir.
    Returns:
        (True, dados_inseridos) em caso de sucesso, (False, mensagem de erro) caso contrário.
        Dados inseridos é uma lista de dicts.
    """
    try:
        client = get_supabase()
        response: APIResponse = client.from_(tabela).insert(dados).execute()
        if response.data:
            logger.info(f"✅ Inserido em {tabela}: {response.data}")
            return True, response.data
        logger.warning(f"⚠️ Inserção em {tabela} não retornou dados, mas não houve erro.")
        return False, "Falha ao inserir dados ou nenhum dado retornado."
    except Exception as e:
        logger.error(f"Erro na inserção em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao inserir dados: {e}"

def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, Union[List[Dict[str, Any]], str]]:
    """
    UPDATE genérico no Supabase.
    Args:
        tabela: Nome da tabela.
        dados_update: Dicionário com os dados a atualizar.
        filtros: Dicionário com os filtros para identificar os registros.
    Returns:
        (True, dados_atualizados) em caso de sucesso, (False, mensagem de erro) caso contrário.
        Dados atualizados é uma lista de dicts.
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).update(dados_update)
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        response: APIResponse = query.execute()
        if response.data:
            logger.info(f"✅ Atualizado em {tabela}: {response.data}")
            return True, response.data
        logger.warning(f"⚠️ Atualização em {tabela} não afetou registros.")
        return False, "Nenhum registro foi atualizado."
    except Exception as e:
        logger.error(f"Erro na atualização em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao atualizar dados: {e}"

def supabase_table_delete(
    tabela: str,
    filtros: Dict[str, Any]
) -> Tuple[bool, int]:
    """
    DELETE genérico no Supabase.
    Args:
        tabela: Nome da tabela.
        filtros: Dicionário com os filtros para identificar os registros.
    Returns:
        (True, numero_de_registros_deletados) em caso de sucesso, (False, 0) caso contrário.
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).delete()
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        response: APIResponse = query.execute()
        # response.data pode ser uma lista vazia se nada foi deletado, mas a operação foi bem-sucedida
        num_deletados = len(response.data) if response.data else 0
        if num_deletados > 0:
            logger.info(f"✅ Deletado em {tabela}: {num_deletados} registro(s)")
            return True, num_deletados
        logger.warning(f"⚠️ Deleção em {tabela} não afetou registros.")
        return False, 0
    except Exception as e:
        logger.error(f"Erro na deleção em {tabela}: {e}", exc_info=True)
        return False, 0



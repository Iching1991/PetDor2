# PETdor2/backend/database/supabase_client.py
"""
Cliente Supabase centralizado - substitui SQLite connection.py
Usa variáveis de ambiente: SUPABASE_URL, SUPABASE_ANON_KEY
"""
import os
import logging
from typing import Any, Dict, List, Optional, Tuple
from supabase import create_client, Client

logger = logging.getLogger(__name__)

# Singleton para o cliente Supabase
_supabase_client: Client | None = None

def get_supabase() -> Client:
    """Retorna instância singleton do cliente Supabase (equivalente a conectar_db())."""
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL ou SUPABASE_ANON_KEY não configurados. "
            "Verifique seu arquivo .env ou as variáveis de ambiente do Streamlit Cloud."
        )
    try:
        _supabase_client = create_client(url, key)
        logger.info("✅ Cliente Supabase inicializado com sucesso (substituindo SQLite).")
        return _supabase_client
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar cliente Supabase: {e}", exc_info=True)
        raise

def testar_conexao() -> Tuple[bool, str]:
    """Testa a conexão com o Supabase."""
    try:
        client = get_supabase()
        # Tenta fazer uma requisição simples para verificar a conexão
        # Por exemplo, listar tabelas ou fazer um SELECT em uma tabela existente (mesmo que vazia)
        # Se não tiver uma tabela 'usuarios' ainda, pode usar uma tabela de teste ou a própria autenticação
        # Para um teste mais robusto, podemos tentar buscar algo de uma tabela conhecida.
        # Por enquanto, apenas a inicialização do cliente já indica sucesso.
        # Se get_supabase() não levantar erro, a conexão inicial foi bem-sucedida.
        # Podemos tentar um select simples para ter certeza.
        response = client.from_("usuarios").select("id").limit(1).execute()
        if response.data is not None: # Apenas verifica se a resposta não é nula
            logger.info("✅ Conexão Supabase testada com sucesso.")
            return True, "Conexão Supabase estabelecida com sucesso!"
        else:
            logger.warning("⚠️ Conexão Supabase estabelecida, mas select simples não retornou dados.")
            return True, "Conexão Supabase estabelecida, mas select simples não retornou dados."
    except Exception as e:
        logger.error(f"❌ Falha ao testar conexão Supabase: {e}", exc_info=True)
        return False, f"Falha ao conectar ao Supabase: {e}"

def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    single: bool = False
) -> Tuple[bool, List[Dict[str, Any]] | Dict[str, Any] | str]:
    """
    SELECT genérico no Supabase (substitui SELECT SQL).
    Args:
        tabela: Nome da tabela
        colunas: String com colunas a selecionar (ex: "id, nome, email")
        filtros: Dict com os filtros (ex: {"email": "teste@email.com"})
        single: Se True, retorna apenas um registro (ou None).
    Returns:
        (sucesso, dados) ou (sucesso, mensagem de erro)
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).select(colunas)
        if filtros:
            for coluna, valor in filtros.items():
                query = query.eq(coluna, valor)
        if single:
            query = query.single()

        response = query.execute()

        if response.data is not None:
            if single:
                return True, response.data
            return True, response.data
        else:
            # Supabase retorna data vazia se não encontrar, não é um erro
            return True, {} if single else []
    except Exception as e:
        logger.error(f"Erro no SELECT em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao buscar dados: {e}"

def supabase_table_insert(
    tabela: str,
    dados: Dict[str, Any]
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    INSERT genérico no Supabase (substitui INSERT SQL).
    Args:
        tabela: Nome da tabela
        dados: Dict com os dados a inserir
    Returns:
        (sucesso, dados_inseridos) ou (sucesso, mensagem de erro)
    """
    try:
        client = get_supabase()
        response = client.from_(tabela).insert(dados).execute()
        if response.data:
            logger.info(f"✅ Inserido em {tabela}: {response.data}")
            return True, response.data
        else:
            logger.error(f"❌ Falha na inserção em {tabela}: {response.data}")
            return False, "Falha ao inserir dados."
    except Exception as e:
        logger.error(f"Erro na inserção em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao inserir dados: {e}"

def supabase_table_update(
    tabela: str,
    dados_update: Dict[str, Any],
    filtros: Dict[str, Any]
) -> Tuple[bool, List[Dict[str, Any]] | str]:
    """
    UPDATE genérico no Supabase (substitui UPDATE SQL).
    Args:
        tabela: Nome da tabela
        dados_update: Dict com os dados a atualizar
        filtros: Dict com os filtros (ex: {"id": 1})
    Returns:
        (sucesso, dados_atualizados) ou (sucesso, mensagem de erro)
    """
    try:
        client = get_supabase()
        query = client.from_(tabela).update(dados_update)
        # Aplica filtros (substitui WHERE)
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        response = query.execute()
        if response.data:
            logger.info(f"✅ Atualizado em {tabela}: {response.data}")
            return True, response.data
        else:
            logger.warning(f"⚠️ Atualização em {tabela} não afetou registros")
            return False, "Nenhum registro foi atualizado."
    except Exception as e:
        logger.error(f"Erro na atualização em {tabela}: {e}", exc_info=True)
        return False, f"Erro ao atualizar dados: {e}"

def supabase_table_delete(
    tabela: str,
    filtros: Dict[str, Any]
) -> Tuple[bool, int]:
    """
    DELETE genérico no Supabase (substitui DELETE SQL).
    Args:
        tabela: Nome da tabela
        filtros: Dict com os filtros (ex: {"id": 1})
    Returns:
        (sucesso, numero_de_registros_deletados)
    """
    try:
        client = get_supabase()
        query = client.table(tabela).delete()
        # Aplica filtros (substitui WHERE)
        for coluna, valor in filtros.items():
            query = query.eq(coluna, valor)
        response = query.execute()
        if response.data:
            logger.info(f"✅ Deletado em {tabela}: {len(response.data)} registro(s)")
            return True, len(response.data)
        else:
            logger.warning(f"⚠️ Deleção em {tabela} não afetou registros")
            return False, 0
    except Exception as e:
        logger.error(f"Erro na deleção em {tabela}: {e}", exc_info=True)
        return False, 0

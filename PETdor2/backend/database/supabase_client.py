# PETdor2/backend/database/supabase_client.py
"""
Cliente Supabase PostgreSQL - Conexão direta
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import streamlit as st

logger = logging.getLogger(__name__)

def get_secret(key: str, default: str = None) -> str:
    """Lê secret do Streamlit Cloud ou .env"""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key, default)

# Configurações do banco
DB_HOST = get_secret("DB_HOST")
DB_PORT = int(get_secret("DB_PORT", 5432))
DB_NAME = get_secret("DB_NAME", "postgres")
DB_USER = get_secret("DB_USER", "postgres")
DB_PASSWORD = get_secret("DB_PASSWORD")

def get_connection():
    """Cria conexão com Supabase PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode="require"
        )
        logger.info("✅ Conexão com Supabase PostgreSQL estabelecida")
        return conn
    except psycopg2.Error as e:
        logger.error(f"❌ Erro ao conectar ao Supabase: {e}")
        raise

def testar_conexao():
    """Testa conexão com o banco de dados"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        logger.info(f"✅ Conexão testada com sucesso: {version[0]}")
        return True, "Conexão com Supabase OK"
    except Exception as e:
        logger.error(f"❌ Erro ao testar conexão: {e}")
        return False, str(e)

def executar_query(query: str, params: tuple = None):
    """Executa uma query no banco"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        conn.commit()
        cursor.close()
        conn.close()

        return True, "Query executada com sucesso"
    except Exception as e:
        logger.error(f"❌ Erro ao executar query: {e}")
        return False, str(e)

def buscar_dados(query: str, params: tuple = None):
    """Busca dados do banco"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        dados = cursor.fetchall()
        cursor.close()
        conn.close()

        return True, dados
    except Exception as e:
        logger.error(f"❌ Erro ao buscar dados: {e}")
        return False, []

def buscar_um(query: str, params: tuple = None):
    """Busca um único registro"""
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        dado = cursor.fetchone()
        cursor.close()
        conn.close()

        return True, dado
    except Exception as e:
        logger.error(f"❌ Erro ao buscar registro: {e}")
        return False, None

def inserir_dados(tabela: str, dados: dict):
    """Insere dados na tabela"""
    try:
        colunas = ", ".join(dados.keys())
        placeholders = ", ".join(["%s"] * len(dados))
        query = f"INSERT INTO {tabela} ({colunas}) VALUES ({placeholders}) RETURNING *"

        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, tuple(dados.values()))
        resultado = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return True, resultado
    except Exception as e:
        logger.error(f"❌ Erro ao inserir dados: {e}")
        return False, None

def atualizar_dados(tabela: str, dados: dict, condicao: str, params_condicao: tuple):
    """Atualiza dados na tabela"""
    try:
        set_clause = ", ".join([f"{k} = %s" for k in dados.keys()])
        query = f"UPDATE {tabela} SET {set_clause} WHERE {condicao} RETURNING *"

        valores = tuple(dados.values()) + params_condicao

        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute(query, valores)
        resultado = cursor.fetchone()

        conn.commit()
        cursor.close()
        conn.close()

        return True, resultado
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar dados: {e}")
        return False, None

def deletar_dados(tabela: str, condicao: str, params: tuple):
    """Deleta dados da tabela"""
    try:
        query = f"DELETE FROM {tabela} WHERE {condicao}"

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)

        conn.commit()
        cursor.close()
        conn.close()

        return True, "Dados deletados com sucesso"
    except Exception as e:
        logger.error(f"❌ Erro ao deletar dados: {e}")
        return False, str(e)

__all__ = [
    "get_connection",
    "testar_conexao",
    "executar_query",
    "buscar_dados",
    "buscar_um",
    "inserir_dados",
    "atualizar_dados",
    "deletar_dados",
]

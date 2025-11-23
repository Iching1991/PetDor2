# PETdor2/database/connection.py
import os
import psycopg2
import logging
from psycopg2.extras import RealDictCursor # Para retornar resultados como dicionários

logger = logging.getLogger(__name__)

def conectar_db():
    """
    Estabelece uma conexão com o banco de dados PostgreSQL (Supabase).
    As credenciais são obtidas de variáveis de ambiente.
    """
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432") # Default para 5432 se não especificado
        )
        # Configura o cursor para retornar dicionários (como sqlite3.Row)
        # Isso facilita a compatibilidade com o código existente que espera acesso por nome
        conn.cursor_factory = RealDictCursor 
        logger.info("Conexão com o banco de dados Supabase estabelecida com sucesso.")
        return conn
    except psycopg2.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados Supabase: {e}", exc_info=True)
        st.error(f"Erro ao conectar ao banco de dados. Por favor, tente novamente mais tarde. Detalhes: {e}")
        st.stop() # Interrompe a execução do Streamlit se a conexão falhar
    except Exception as e:
        logger.error(f"Erro inesperado ao conectar ao banco de dados: {e}", exc_info=True)
        st.error(f"Erro inesperado ao conectar ao banco de dados. Detalhes: {e}")
        st.stop()

# PETdor_2.0/database/connection.py
"""
Conexão inteligente: PostgreSQL (Supabase com pg8000) na nuvem ou SQLite local.
"""
import os
import sqlite3
import logging

# Para PostgreSQL (Supabase)
try:
    import pg8000.dbapi
    PG8000_AVAILABLE = True
except ImportError:
    PG8000_AVAILABLE = False
    logging.warning("pg8000 não instalado. PostgreSQL indisponível.")

logger = logging.getLogger(__name__)

# ------------- SQLite (desenvolvimento local) -------------
def conectar_db_sqlite():
    """Conecta ao SQLite local (petdor.db)."""
    db_dir = "data"
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "petdor.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    logger.info(f"Conectado ao SQLite: {db_path}")
    return conn

# ------------- PostgreSQL (Supabase - produção com pg8000) -------------
def conectar_db_supabase():
    """Conecta ao PostgreSQL no Supabase usando pg8000."""
    if not PG8000_AVAILABLE:
        raise RuntimeError("pg8000 não instalado. Instale com: pip install pg8000")

    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_PORT = os.getenv("DB_PORT", "5432")

    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        raise RuntimeError("Variáveis de ambiente do Supabase não configuradas (DB_HOST, DB_NAME, etc.)")

    try:
        conn = pg8000.dbapi.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=int(DB_PORT), # pg8000 espera int para port
            ssl_context=True,  # pg8000 usa ssl_context=True para SSL
        )
        logger.info("Conectado ao Supabase (PostgreSQL com pg8000)")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar no Supabase com pg8000: {e}")
        raise

# ------------- Função principal: escolhe o banco certo -------------
def conectar_db():
    """
    Conecta ao banco apropriado automaticamente:
    - Supabase (PostgreSQL com pg8000) se DB_HOST estiver configurado (produção)
    - SQLite local se não (desenvolvimento)
    """
    if os.getenv("DB_HOST") and PG8000_AVAILABLE:
        logger.info("Usando Supabase (PostgreSQL com pg8000) - produção")
        return conectar_db_supabase()
    else:
        logger.info("Usando SQLite local - desenvolvimento")
        return conectar_db_sqlite()

# ------------- Função de teste de conexão -------------
def testar_conexao_supabase():
    """Testa se consegue conectar no Supabase e listar tabelas."""
    try:
        if not PG8000_AVAILABLE:
            return False, "pg8000 não instalado"

        if not os.getenv("DB_HOST"):
            return False, "DB_HOST não configurado nos Secrets"

        conn = conectar_db_supabase()
        cur = conn.cursor()
        cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public';")
        tabelas = [row[0] for row in cur.fetchall()]
        conn.close()

        logger.info(f"Conexão Supabase OK. Tabelas: {tabelas}")
        return True, f"Conexão OK. Tabelas encontradas: {tabelas}"

    except Exception as e:
        logger.error(f"Falha na conexão Supabase com pg8000: {e}")
        return False, str(e)

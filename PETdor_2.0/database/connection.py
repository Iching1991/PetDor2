import sqlite3
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = str(ROOT_DIR / "petdor.db")

def conectar_db():
    """Conecta ao banco SQLite, criando diretório se necessário"""
    try:
        db_dir = os.path.dirname(DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"[ERRO] Falha ao conectar ao banco: {e}")
        raise

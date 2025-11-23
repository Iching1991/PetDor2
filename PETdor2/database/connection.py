   # PETdor2/database/connection.py
   import os
   import sqlite3
   import logging

   logger = logging.getLogger(__name__)

   DB_PATH = os.path.join(os.path.dirname(__file__), "..", "petdor.db")

   def conectar_db():
       try:
           conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
           conn.row_factory = sqlite3.Row
           logger.info(f"Conectado ao banco SQLite em {DB_PATH}")
           return conn
       except Exception as e:
           logger.error(f"Erro ao conectar ao SQLite: {e}", exc_info=True)
           raise

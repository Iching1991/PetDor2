# PETdor2/database/__init__.py
import logging
import os
# Removendo sqlite3 e Row, pois vamos usar psycopg2 para Supabase
# import sqlite3
# from sqlite3 import Row

# CORREÇÃO: Importação relativa para connection
from . import connection 

logger = logging.getLogger(__name__)

# ... (restante do seu código __init__.py, se houver)

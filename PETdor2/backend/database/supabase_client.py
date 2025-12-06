# PETdor2/backend/database/supabase_client.py
# backend/database/supabase_client.py

from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ ERRO: Variáveis SUPABASE_URL e SUPABASE_KEY não foram carregadas.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ------------------------------
# FUNÇÕES DE OPERAÇÃO NO BANCO
# ------------------------------

def testar_conexao():
    """Valida se a conexão está funcionando."""
    try:
        res = supabase.table("usuarios").select("*").limit(1).execute()
        return True, "Conexão Supabase OK"
    except Exception as e:
        return False, str(e)


def buscar_usuario_por_email(email: str):
    """Retorna usuário pelo email (corrigido p/ Supabase v2)."""
    try:
        query = supabase.table("usuarios").select("*").eq("email", email).single().execute()
        return query.data
    except Exception:
        return None


def criar_usuario(data: dict):
    """Insere novo usuário na tabela."""
    try:
        res = supabase.table("usuarios").insert(data).execute()
        return res.data
    except Exception as e:
        return None



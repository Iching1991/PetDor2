# PETdor2/database/supabase_client.py
"""
Módulo de cliente Supabase para acesso ao banco de dados.
"""
import os
from supabase import create_client, Client

# Carrega as variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "❌ Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não estão definidas. "
        "Configure-as no Streamlit Cloud ou no arquivo .streamlit/secrets.toml"
    )

# Cria o cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

__all__ = ["supabase"]


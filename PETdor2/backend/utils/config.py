# PETdor2/backend/utils/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

# ================================
# CAMINHO BASE DO BACKEND
# ================================
# utils -> backend
ROOT_DIR = Path(__file__).resolve().parent.parent

# ================================
# CONFIGURAÇÕES GERAIS DO APP
# ================================
APP_CONFIG = {
    "titulo": "PETDOR",
    "versao": "1.0.0",
    "autor": "Salute Vitae AI",
}

# ================================
# CONFIGURAÇÕES DO SUPABASE
# ================================
# No Streamlit Cloud, são lidas de st.secrets automaticamente.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

# ================================
# CONFIG SMTP (EMAIL)
# ================================
SMTP_SERVIDOR = os.getenv("EMAIL_HOST", "smtpout.secureserver.net")
SMTP_PORTA = int(os.getenv("EMAIL_PORT", "587"))

SMTP_EMAIL = os.getenv("EMAIL_USER", "relatorio@petdor.app")
SMTP_SENHA = os.getenv("EMAIL_PASSWORD", "")
SMTP_REMETENTE = os.getenv("EMAIL_SENDER", SMTP_EMAIL)

SMTP_USAR_SSL = os.getenv("EMAIL_USE_SSL", "True").lower() == "true"

# ================================
# SEGURANÇA
# ================================
SECRET_KEY = os.getenv("SECRET_KEY", "CHAVE_SECRETA_TEMPORARIA")

# ================================
# URL DO APP STREAMLIT
# ================================
STREAMLIT_APP_URL = os.getenv("STREAMLIT_APP_URL", "https://petdor.streamlit.app")

# PETdor2/backend/petdor.py

import os
import sys
import logging

# =======================================
# 🔧 Logging
# =======================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# =======================================
# 🔧 Ajuste do sys.path
# =======================================
# Adiciona a raiz do projeto (PETdor2/) ao sys.path para imports absolutos funcionarem
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
    logger.info(f"📂 BASE_DIR adicionado ao sys.path: {BASE_DIR}")

# =======================================
# 🔧 IMPORTS ABSOLUTOS DO BACKEND
# =======================================

# Banco de dados
from backend.database import testar_conexao, get_supabase

# Autenticação
from backend.auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_id,
    buscar_usuario_por_email,
    atualizar_usuario,
    deletar_usuario,
)
from backend.auth.password_reset import (
    solicitar_reset_senha,
    validar_token_reset,
    redefinir_senha_com_token,
)
from backend.auth.email_confirmation import confirmar_email_com_token
from backend.auth.security import usuario_logado, logout

# =======================================
# 🔧 IMPORTS DAS PÁGINAS (corretos para raiz PETdor2/pages/)
# =======================================
from pages.cadastro_pet import render as cadastro_pet_app
from pages.avaliacao import render as avaliacao_app
from pages.admin import render as admin_app
from pages.home import render as home_app
from pages.login import render as login_app
from pages.conta import render as conta_app
from pages.historico import render as historico_app
from pages.recuperar_senha import render as recuperar_senha_app
from pages.password_reset import render as password_reset_app
from pages.confirmar_email import render as confirmar_email_app

# =======================================
# 🔧 Inicialização do Supabase
# =======================================
def inicializar_supabase():
    """
    Inicializa o Supabase e testa a conexão.
    Retorna (True, None) se OK, ou (False, mensagem de erro) se falhar.
    """
    try:
        get_supabase()
        ok, msg = testar_conexao()

        if not ok:
            return False, f"Falha ao conectar ao Supabase: {msg}"

        logger.info("✅ Supabase inicializado com sucesso.")
        return True, None

    except Exception as e:
        return False, f"Erro inesperado na inicialização do Supabase: {e}"

# =======================================
# 🧪 Função principal para rodar o backend
# =======================================
def start():
    """
    Função que será chamada caso você queira rodar o backend
    sem o Streamlit (ex.: testes locais, workers, scripts).
    """
    ok, msg = inicializar_supabase()

    if not ok:
        logger.error(msg)
        return

    logger.info("🚀 Backend PETDor carregado com sucesso.")
    logger.info("Backend pronto para ser usado por Streamlit ou chamadas internas.")

# =======================================
# 📌 Execução direta (opcional)
# =======================================
if __name__ == "__main__":
    start()

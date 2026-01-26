import os
import sys
import logging

# =======================================
# 🔧 Logging
# =======================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =======================================
# 🔧 sys.path
# =======================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# =======================================
# 🔧 IMPORTS CORRETOS
# =======================================

from backend.database import testar_conexao

from backend.auth.user import (
    cadastrar_usuario,
    verificar_credenciais,
    buscar_usuario_por_email,
    atualizar_usuario,
    deletar_usuario,
)

from backend.auth.password_reset import (
    solicitar_reset_senha,
    validar_token_reset,
    redefinir_senha_com_token,
)

from backend.auth.security import usuario_logado, logout

# =======================================
# 🔧 Inicialização (REST)
# =======================================
def inicializar_backend():
    """
    Apenas testa conexão REST com Supabase.
    """
    if not testar_conexao():
        logger.error("❌ Falha ao conectar ao Supabase.")
        return False

    logger.info("✅ Backend PETDor inicializado com sucesso.")
    return True


def start():
    if not inicializar_backend():
        return

    logger.info("🚀 Backend PETDor pronto para uso.")


if __name__ == "__main__":
    start()

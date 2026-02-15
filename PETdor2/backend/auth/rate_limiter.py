"""
Rate Limiter para Supabase Auth - PETDor2
Gerencia tentativas e cooldowns para evitar 429
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


# ==========================================================
# 🕐 CONFIGURAÇÕES
# ==========================================================

COOLDOWN_AFTER_429 = 60  # 1 minuto

RATE_LIMITS = {
    "cadastro": {"max_attempts": 2, "period_minutes": 15},
    "login": {"max_attempts": 5, "period_minutes": 5},
    "recuperacao_senha": {"max_attempts": 2, "period_minutes": 15},
    "redefinir_senha": {"max_attempts": 3, "period_minutes": 10},
}


# ==========================================================
# 📊 FUNÇÕES
# ==========================================================

def _get_key(operacao: str, identificador: str = "") -> str:
    """Gera chave única para session_state."""
    if identificador:
        return f"rl_{operacao}_{identificador}"
    return f"rl_{operacao}_global"


def verificar_rate_limit(
    operacao: str,
    identificador: str = ""
) -> Tuple[bool, Optional[str]]:
    """
    Verifica se pode executar operação.

    Returns:
        (pode_executar: bool, mensagem_erro: str | None)
    """

    if operacao not in RATE_LIMITS:
        return True, None

    config = RATE_LIMITS[operacao]
    key = _get_key(operacao, identificador)

    # Inicializar
    if key not in st.session_state:
        st.session_state[key] = {
            "attempts": [],
            "last_429": None,
        }

    hist = st.session_state[key]
    now = datetime.now()

    # Verificar cooldown 429
    if hist["last_429"]:
        elapsed = (now - hist["last_429"]).total_seconds()

        if elapsed < COOLDOWN_AFTER_429:
            remaining = int(COOLDOWN_AFTER_429 - elapsed)
            return False, (
                f"⏱️ Aguarde {remaining} segundos antes de tentar novamente."
            )
        else:
            hist["last_429"] = None

    # Verificar limite de tentativas
    period = timedelta(minutes=config["period_minutes"])
    cutoff = now - period

    recent = [t for t in hist["attempts"] if t > cutoff]
    hist["attempts"] = recent

    if len(recent) >= config["max_attempts"]:
        wait_time = (recent[0] + period - now).total_seconds()
        minutes = int(wait_time / 60) + 1

        return False, (
            f"⏱️ Muitas tentativas. "
            f"Aguarde {minutes} minuto(s)."
        )

    return True, None


def registrar_tentativa(operacao: str, identificador: str = ""):
    """Registra tentativa."""
    key = _get_key(operacao, identificador)

    if key not in st.session_state:
        st.session_state[key] = {
            "attempts": [],
            "last_429": None,
        }

    st.session_state[key]["attempts"].append(datetime.now())


def registrar_erro_429(operacao: str, identificador: str = ""):
    """Registra erro 429."""
    key = _get_key(operacao, identificador)

    if key not in st.session_state:
        st.session_state[key] = {
            "attempts": [],
            "last_429": None,
        }

    st.session_state[key]["last_429"] = datetime.now()
    logger.warning(f"429 registrado: {operacao} - {identificador}")


def limpar_historico(operacao: str, identificador: str = ""):
    """Limpa histórico após sucesso."""
    key = _get_key(operacao, identificador)

    if key in st.session_state:
        del st.session_state[key]

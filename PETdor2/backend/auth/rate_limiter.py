"""
Rate Limiter para Supabase Auth - PETDor2
Gerencia tentativas, cooldowns e estatísticas para evitar erro 429.

Escopo atual:
- Baseado em session_state (por sessão Streamlit)
- Protege UX e abuso básico
- Possui estatísticas para debug/admin
"""

# ==========================================================
# 📚 IMPORTS
# ==========================================================

import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ==========================================================
# 🕐 CONFIGURAÇÕES
# ==========================================================

# Cooldown aplicado após erro 429 da API
COOLDOWN_AFTER_429 = 60  # segundos

# Limites por operação
RATE_LIMITS = {
    "cadastro": {"max_attempts": 2, "period_minutes": 15},
    "login": {"max_attempts": 5, "period_minutes": 5},
    "recuperacao_senha": {"max_attempts": 2, "period_minutes": 15},
    "redefinir_senha": {"max_attempts": 3, "period_minutes": 10},
}


# ==========================================================
# 🔑 HELPERS INTERNOS
# ==========================================================

def _get_key(operacao: str, identificador: str = "") -> str:
    """
    Gera chave única para session_state.

    Ex:
        rl_login_email@email.com
        rl_cadastro_global
    """
    if identificador:
        return f"rl_{operacao}_{identificador}"

    return f"rl_{operacao}_global"


def _init_if_not_exists(key: str):
    """Inicializa estrutura no session_state."""
    if key not in st.session_state:
        st.session_state[key] = {
            "attempts": [],
            "last_429": None,
            "created_at": datetime.now(),
        }


# ==========================================================
# 🚦 VERIFICAÇÃO DE RATE LIMIT
# ==========================================================

def verificar_rate_limit(
    operacao: str,
    identificador: str = ""
) -> Tuple[bool, Optional[str]]:
    """
    Verifica se operação pode ser executada.

    Returns:
        (pode_executar, mensagem_erro)
    """

    # Operação sem limite
    if operacao not in RATE_LIMITS:
        return True, None

    config = RATE_LIMITS[operacao]
    key = _get_key(operacao, identificador)

    _init_if_not_exists(key)

    hist = st.session_state[key]
    now = datetime.now()

    # ------------------------------------------------------
    # ⏱️ Cooldown após erro 429
    # ------------------------------------------------------
    if hist["last_429"]:
        elapsed = (now - hist["last_429"]).total_seconds()

        if elapsed < COOLDOWN_AFTER_429:
            remaining = int(COOLDOWN_AFTER_429 - elapsed)

            return False, (
                f"⏱️ Aguarde {remaining} segundos antes de tentar novamente."
            )

        # Reset cooldown
        hist["last_429"] = None

    # ------------------------------------------------------
    # 📊 Limite de tentativas
    # ------------------------------------------------------
    period = timedelta(minutes=config["period_minutes"])
    cutoff = now - period

    # Filtra tentativas recentes
    recent_attempts = [
        t for t in hist["attempts"]
        if t > cutoff
    ]

    hist["attempts"] = recent_attempts

    if len(recent_attempts) >= config["max_attempts"]:
        wait_time = (recent_attempts[0] + period - now).total_seconds()
        minutes = int(wait_time / 60) + 1

        return False, (
            f"⏱️ Muitas tentativas. "
            f"Aguarde {minutes} minuto(s) para tentar novamente."
        )

    return True, None


# ==========================================================
# 📝 REGISTRO DE EVENTOS
# ==========================================================

def registrar_tentativa(
    operacao: str,
    identificador: str = ""
):
    """Registra tentativa de operação."""

    key = _get_key(operacao, identificador)
    _init_if_not_exists(key)

    st.session_state[key]["attempts"].append(datetime.now())

    logger.info(
        f"Tentativa registrada | Operação={operacao} | ID={identificador}"
    )


def registrar_erro_429(
    operacao: str,
    identificador: str = ""
):
    """Registra ocorrência de erro 429."""

    key = _get_key(operacao, identificador)
    _init_if_not_exists(key)

    st.session_state[key]["last_429"] = datetime.now()

    logger.warning(
        f"Erro 429 registrado | Operação={operacao} | ID={identificador}"
    )


def limpar_historico(
    operacao: str,
    identificador: str = ""
):
    """Limpa histórico após sucesso."""

    key = _get_key(operacao, identificador)

    if key in st.session_state:
        del st.session_state[key]

        logger.info(
            f"Histórico limpo | Operação={operacao} | ID={identificador}"
        )


# ==========================================================
# 📈 ESTATÍSTICAS
# ==========================================================

def obter_estatisticas() -> Dict[str, Any]:
    """
    Retorna estatísticas completas do Rate Limiter.

    Útil para:
        • Debug
        • Painel admin
        • Auditoria
        • Monitoramento de abuso
    """

    stats: Dict[str, Any] = {}

    for key, value in st.session_state.items():

        if not key.startswith("rl_"):
            continue

        attempts = value.get("attempts", [])
        last_429 = value.get("last_429")
        created_at = value.get("created_at")

        stats[key] = {
            "total_tentativas": len(attempts),
            "ultima_tentativa": attempts[-1] if attempts else None,
            "ultimo_429": last_429,
            "criado_em": created_at,
        }

    resumo = {
        "total_chaves_monitoradas": len(stats),
        "timestamp_consulta": datetime.now(),
        "dados": stats,
    }

    return resumo


# ==========================================================
# 🧹 LIMPEZA GLOBAL (OPCIONAL)
# ==========================================================

def limpar_tudo_rate_limit():
    """
    Remove TODOS os dados de rate limit da sessão.
    Útil para logout ou reset admin.
    """

    keys_to_remove = [
        key for key in st.session_state
        if key.startswith("rl_")
    ]

    for key in keys_to_remove:
        del st.session_state[key]

    logger.info("Todos os rate limits foram limpos.")
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
# 🕐 CONFIGURAÇÕES DE RATE LIMITING
# ==========================================================

# Tempo de cooldown após erro 429 (em segundos)
COOLDOWN_AFTER_429 = 60  # 1 minuto

# Limites por operação (tentativas por período)
RATE_LIMITS = {
    "cadastro": {"max_attempts": 3, "period_minutes": 10},
    "login": {"max_attempts": 5, "period_minutes": 5},
    "recuperacao_senha": {"max_attempts": 2, "period_minutes": 15},
    "redefinir_senha": {"max_attempts": 3, "period_minutes": 10},
}


# ==========================================================
# 📊 FUNÇÕES DE CONTROLE
# ==========================================================

def _get_rate_limit_key(operacao: str, identificador: str = "") -> str:
    """
    Gera chave única para rastrear tentativas.

    Args:
        operacao: Tipo de operação (cadastro, login, etc)
        identificador: Email ou outro identificador único (opcional)

    Returns:
        Chave para session_state
    """
    if identificador:
        return f"rate_limit_{operacao}_{identificador}"
    return f"rate_limit_{operacao}_global"


def verificar_rate_limit(
    operacao: str,
    identificador: str = ""
) -> Tuple[bool, Optional[str]]:
    """
    Verifica se a operação pode ser executada ou está em cooldown.

    Args:
        operacao: Tipo de operação (cadastro, login, recuperacao_senha)
        identificador: Email ou outro identificador (opcional)

    Returns:
        (pode_executar: bool, mensagem_erro: str | None)
    """

    # Verificar se operação existe nas configurações
    if operacao not in RATE_LIMITS:
        logger.warning(f"Operação desconhecida: {operacao}")
        return True, None

    config = RATE_LIMITS[operacao]
    key = _get_rate_limit_key(operacao, identificador)

    # Inicializar histórico se não existir
    if key not in st.session_state:
        st.session_state[key] = {
            "attempts": [],
            "last_429": None,
        }

    historico = st.session_state[key]
    agora = datetime.now()

    # -------------------------
    # 1️⃣ VERIFICAR COOLDOWN 429
    # -------------------------
    if historico["last_429"]:
        tempo_desde_429 = (agora - historico["last_429"]).total_seconds()

        if tempo_desde_429 < COOLDOWN_AFTER_429:
            segundos_restantes = int(COOLDOWN_AFTER_429 - tempo_desde_429)
            return False, (
                f"⏱️ Aguarde {segundos_restantes} segundos antes de tentar novamente."
            )
        else:
            # Cooldown expirou, limpar
            historico["last_429"] = None

    # -------------------------
    # 2️⃣ VERIFICAR LIMITE DE TENTATIVAS
    # -------------------------
    periodo = timedelta(minutes=config["period_minutes"])
    limite_tempo = agora - periodo

    # Filtrar tentativas dentro do período
    tentativas_recentes = [
        t for t in historico["attempts"]
        if t > limite_tempo
    ]

    # Atualizar histórico
    historico["attempts"] = tentativas_recentes

    # Verificar se excedeu limite
    if len(tentativas_recentes) >= config["max_attempts"]:
        tempo_ate_liberar = (tentativas_recentes[0] + periodo - agora).total_seconds()
        minutos = int(tempo_ate_liberar / 60) + 1

        return False, (
            f"⏱️ Muitas tentativas. "
            f"Aguarde {minutos} minuto(s) antes de tentar novamente."
        )

    # -------------------------
    # 3️⃣ PERMITIR OPERAÇÃO
    # -------------------------
    return True, None


def registrar_tentativa(operacao: str, identificador: str = ""):
    """
    Registra uma tentativa de operação.

    Args:
        operacao: Tipo de operação
        identificador: Email ou outro identificador (opcional)
    """
    key = _get_rate_limit_key(operacao, identificador)

    if key not in st.session_state:
        st.session_state[key] = {
            "attempts": [],
            "last_429": None,
        }

    st.session_state[key]["attempts"].append(datetime.now())
    logger.debug(f"Tentativa registrada: {operacao} - {identificador}")


def registrar_erro_429(operacao: str, identificador: str = ""):
    """
    Registra que recebeu erro 429 (rate limit do servidor).

    Args:
        operacao: Tipo de operação
        identificador: Email ou outro identificador (opcional)
    """
    key = _get_rate_limit_key(operacao, identificador)

    if key not in st.session_state:
        st.session_state[key] = {
            "attempts": [],
            "last_429": None,
        }

    st.session_state[key]["last_429"] = datetime.now()
    logger.warning(f"Erro 429 registrado: {operacao} - {identificador}")


def limpar_historico(operacao: str, identificador: str = ""):
    """
    Limpa histórico de tentativas (usar após sucesso).

    Args:
        operacao: Tipo de operação
        identificador: Email ou outro identificador (opcional)
    """
    key = _get_rate_limit_key(operacao, identificador)

    if key in st.session_state:
        del st.session_state[key]
        logger.debug(f"Histórico limpo: {operacao} - {identificador}")


def obter_estatisticas(operacao: str, identificador: str = "") -> dict:
    """
    Retorna estatísticas de uso do rate limiter.

    Args:
        operacao: Tipo de operação
        identificador: Email ou outro identificador (opcional)

    Returns:
        Dicionário com estatísticas
    """
    key = _get_rate_limit_key(operacao, identificador)

    if key not in st.session_state:
        return {
            "tentativas_recentes": 0,
            "em_cooldown_429": False,
            "pode_tentar": True,
        }

    historico = st.session_state[key]
    config = RATE_LIMITS.get(operacao, {"max_attempts": 999, "period_minutes": 60})

    agora = datetime.now()
    periodo = timedelta(minutes=config["period_minutes"])
    limite_tempo = agora - periodo

    tentativas_recentes = [
        t for t in historico["attempts"]
        if t > limite_tempo
    ]

    em_cooldown = False
    if historico["last_429"]:
        tempo_desde_429 = (agora - historico["last_429"]).total_seconds()
        em_cooldown = tempo_desde_429 < COOLDOWN_AFTER_429

    return {
        "tentativas_recentes": len(tentativas_recentes),
        "max_tentativas": config["max_attempts"],
        "em_cooldown_429": em_cooldown,
        "pode_tentar": len(tentativas_recentes) < config["max_attempts"] and not em_cooldown,
    }

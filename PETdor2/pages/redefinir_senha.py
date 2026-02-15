"""
Página de redefinição de senha - PETDor2

✅ Permite redefinir senha via token do Supabase
✅ Validações de senha forte
✅ Feedback visual aprimorado
✅ Proteção contra rate limiting
✅ Compatível com Supabase Auth
"""

import streamlit as st
import logging

from backend.auth.password_reset import redefinir_senha
from backend.auth.rate_limiter import verificar_rate_limit, obter_estatisticas

logger = logging.getLogger(__name__)


# ==========================================================
# 🖥️ RENDER PRINCIPAL
# ==========================================================

def render():
    """Renderiza a página de redefinição de senha."""

    # -------------------------
    # HEADER E INSTRUÇÕES
    # -------------------------
    st.title("🔐 Redefinir Senha")

    st.markdown("""
    Digite sua nova senha abaixo.  

    ⚠️ **Requisitos de segurança:**
    - Mínimo de **6 caracteres**
    - Recomendado: **8+ caracteres** com letras e números
    """)

    st.divider()

    # -------------------------
    # VERIFICAR SESSÃO ATIVA
    # -------------------------
    if not _verificar_sessao_ativa():
        _mostrar_sessao_invalida()
        return

    # -------------------------
    # FORMULÁRIO
    # -------------------------
    with st.form("form_redefinir_senha", clear_on_submit=True):
        nova_senha = st.text_input(
            "🔑 Nova senha",
            type="password",
            placeholder="Digite sua nova senha",
            help="Mínimo de 6 caracteres",
        )

        confirmar_senha = st.text_input(
            "🔑 Confirmar nova senha",
            type="password",
            placeholder="Digite novamente",
            help="Deve ser igual à senha acima",
        )

        # Indicador de força da senha
        if nova_senha:
            _mostrar_forca_senha(nova_senha)

        st.divider()

        # Botão de envio
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button(
                "✅ Redefinir Senha",
                use_container_width=True,
                type="primary"
            )

        if submit:
            _processar_redefinicao(nova_senha, confirmar_senha)


# ==========================================================
# 🔍 VERIFICAR SESSÃO ATIVA
# ==========================================================

def _verificar_sessao_ativa() -> bool:
    """
    Verifica se há uma sessão ativa do Supabase.

    Returns:
        True se sessão válida, False caso contrário
    """

    try:
        from backend.database.supabase_client import supabase

        session = supabase.auth.get_session()
        return session is not None and session.user is not None

    except Exception as e:
        logger.exception("Erro ao verificar sessão")
        return False


# ==========================================================
# ⚠️ MOSTRAR SESSÃO INVÁLIDA
# ==========================================================

def _mostrar_sessao_invalida():
    """Exibe mensagem de sessão inválida ou expirada."""

    st.warning("""
    ⚠️ **Sessão inválida ou expirada**

    O link de redefinição de senha expirou ou é inválido.
    """)

    st.info("""
    **O que fazer:**

    1. Solicite um novo link de recuperação
    2. Verifique se clicou no link mais recente do e-mail
    3. Links expiram em **1 hora** por segurança
    """)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔐 Solicitar Novo Link", use_container_width=True, type="primary"):
            st.session_state.pagina = "recuperar_senha"
            st.rerun()

    with col2:
        if st.button("← Voltar ao Login", use_container_width=True):
            st.session_state.pagina = "login"
            st.rerun()


# ==========================================================
# 💪 MOSTRAR FORÇA DA SENHA
# ==========================================================

def _mostrar_forca_senha(senha: str):
    """
    Exibe indicador visual da força da senha.

    Args:
        senha: Senha digitada pelo usuário
    """

    forca = 0
    feedback = []

    # Critérios de força
    if len(senha) >= 6:
        forca += 1
    if len(senha) >= 8:
        forca += 1
        feedback.append("✅ Comprimento adequado")
    else:
        feedback.append("⚠️ Use pelo menos 8 caracteres")

    if any(c.isdigit() for c in senha):
        forca += 1
        feedback.append("✅ Contém números")
    else:
        feedback.append("💡 Adicione números")

    if any(c.isupper() for c in senha):
        forca += 1
        feedback.append("✅ Contém maiúsculas")
    else:
        feedback.append("💡 Adicione letras maiúsculas")

    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in senha):
        forca += 1
        feedback.append("✅ Contém caracteres especiais")

    # Exibir indicador
    if forca <= 2:
        st.warning("🔴 **Senha fraca**")
    elif forca <= 3:
        st.info("🟡 **Senha média**")
    else:
        st.success("🟢 **Senha forte**")

    # Exibir feedback
    with st.expander("💡 Dicas de segurança"):
        for item in feedback:
            st.markdown(f"- {item}")


# ==========================================================
# 🔄 PROCESSAR REDEFINIÇÃO
# ==========================================================

def _processar_redefinicao(nova_senha: str, confirmar_senha: str):
    """
    Processa a redefinição de senha.

    Args:
        nova_senha: Nova senha digitada
        confirmar_senha: Confirmação da senha
    """

    try:
        # -------------------------
        # 1️⃣ VALIDAÇÕES BÁSICAS
        # -------------------------
        if not nova_senha or not confirmar_senha:
            st.error("❌ Preencha todos os campos.")
            return

        if nova_senha != confirmar_senha:
            st.error("❌ As senhas não coincidem.")
            return

        if len(nova_senha) < 6:
            st.error("❌ A senha deve ter pelo menos 6 caracteres.")
            return

        # -------------------------
        # 2️⃣ VERIFICAR RATE LIMIT
        # -------------------------
        stats = obter_estatisticas("redefinir_senha")

        if not stats["pode_tentar"]:
            st.warning(
                "⏱️ Muitas tentativas. "
                "Aguarde alguns instantes antes de tentar novamente."
            )
            return

        # -------------------------
        # 3️⃣ REDEFINIR SENHA
        # -------------------------
        with st.spinner("⏳ Redefinindo senha..."):
            sucesso, mensagem = redefinir_senha(nova_senha)

        # -------------------------
        # 4️⃣ FEEDBACK AO USUÁRIO
        # -------------------------
        if sucesso:
            st.success(mensagem)
            st.balloons()

            st.markdown("""
            ---
            ### ✅ Senha redefinida com sucesso!

            Você já pode fazer login com sua nova senha.
            """)

            # Botão para ir ao login
            if st.button("🔐 Ir para o Login", type="primary", use_container_width=True):
                st.session_state.pagina = "login"
                st.rerun()

        else:
            # Diferenciar entre rate limit e outros erros
            if "⏱️" in mensagem:
                st.warning(mensagem)
            elif "Sessão" in mensagem or "expirada" in mensagem:
                st.error(mensagem)

                if st.button("🔐 Solicitar Novo Link"):
                    st.session_state.pagina = "recuperar_senha"
                    st.rerun()
            else:
                st.error(mensagem)

    except Exception as e:
        logger.exception("Erro ao processar redefinição de senha")
        st.error(
            "⚠️ Erro inesperado ao redefinir senha. "
            "Tente novamente em alguns instantes."
        )


# ==========================================================
# 🛡️ PROTEÇÃO CONTRA ERROS INESPERADOS
# ==========================================================

try:
    render()
except Exception as e:
    logger.exception("Erro crítico ao renderizar página de redefinição")
    st.error("❌ Erro inesperado ao carregar a página.")

    if st.button("🔄 Recarregar Página"):
        st.rerun()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = ["render"]

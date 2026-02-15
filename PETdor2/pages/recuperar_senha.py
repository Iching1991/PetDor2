"""
Página de recuperação de senha - PETDor2

✅ Solicita envio de link de redefinição por e-mail
✅ Proteção contra rate limiting (429)
✅ Validações robustas
✅ Feedback visual aprimorado
✅ Compatível com Supabase Auth + RLS
"""

import streamlit as st
import logging

from backend.auth.password_reset import solicitar_reset_senha
from backend.auth.rate_limiter import verificar_rate_limit, obter_estatisticas
from backend.utils.validators import validar_email

logger = logging.getLogger(__name__)


# ==========================================================
# 🖥️ RENDER PRINCIPAL
# ==========================================================

def render():
    """Renderiza a página de recuperação de senha."""

    # -------------------------
    # HEADER E INSTRUÇÕES
    # -------------------------
    st.title("🔐 Recuperar Senha")

    st.markdown("""
    Digite o e-mail usado na sua conta do **PETDor**.  
    Se ele estiver cadastrado, enviaremos um link para redefinir sua senha.

    ⏱️ **Importante:** Por segurança, você pode solicitar recuperação apenas 
    **2 vezes a cada 15 minutos**.
    """)

    st.divider()

    # -------------------------
    # FORMULÁRIO
    # -------------------------
    with st.form("form_recuperar_senha", clear_on_submit=False):
        email = st.text_input(
            "📧 E-mail cadastrado",
            placeholder="seu@email.com",
            key="email_recuperacao",
            help="Digite o e-mail usado no cadastro",
        )

        # Botão de envio
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit = st.form_submit_button(
                "📨 Enviar Link de Recuperação",
                use_container_width=True,
                type="primary"
            )

        if submit:
            _processar_solicitacao(email)

    # -------------------------
    # RODAPÉ
    # -------------------------
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        if st.button("← Voltar ao Login", use_container_width=True):
            st.session_state.pagina = "login"
            st.rerun()

    with col2:
        if st.button("📝 Criar Conta", use_container_width=True):
            st.session_state.pagina = "cadastro"
            st.rerun()

    # -------------------------
    # INFORMAÇÕES ADICIONAIS
    # -------------------------
    with st.expander("ℹ️ Não recebeu o e-mail?"):
        st.markdown("""
        **Verifique:**
        - ✉️ Sua caixa de entrada e **pasta de spam**
        - 📧 Se o e-mail digitado está correto
        - ⏱️ Aguarde alguns minutos (o e-mail pode demorar)

        **Ainda com problemas?**
        - Entre em contato pelo suporte: suporte@petdor.app
        """)


# ==========================================================
# 🔄 PROCESSAR SOLICITAÇÃO
# ==========================================================

def _processar_solicitacao(email: str):
    """
    Processa a solicitação de recuperação de senha.

    Args:
        email: E-mail informado pelo usuário
    """

    try:
        # -------------------------
        # 1️⃣ VALIDAÇÕES BÁSICAS
        # -------------------------
        email = email.strip().lower()

        if not email:
            st.error("❌ Por favor, informe seu e-mail.")
            return

        if not validar_email(email):
            st.error("❌ Formato de e-mail inválido.")
            return

        # -------------------------
        # 2️⃣ VERIFICAR RATE LIMIT
        # -------------------------
        stats = obter_estatisticas("recuperacao_senha", email)

        if not stats["pode_tentar"]:
            if stats["em_cooldown_429"]:
                st.warning(
                    "⏱️ Você fez muitas tentativas recentemente. "
                    "Aguarde 1 minuto antes de tentar novamente."
                )
            else:
                st.warning(
                    f"⏱️ Você já solicitou recuperação {stats['tentativas_recentes']} vez(es). "
                    f"Aguarde alguns minutos antes de tentar novamente."
                )
            return

        # -------------------------
        # 3️⃣ SOLICITAR RECUPERAÇÃO
        # -------------------------
        with st.spinner("⏳ Processando solicitação..."):
            sucesso, mensagem = solicitar_reset_senha(email)

        # -------------------------
        # 4️⃣ FEEDBACK AO USUÁRIO
        # -------------------------
        if sucesso:
            st.success("✅ Solicitação processada com sucesso!")

            st.info(mensagem)

            st.markdown("""
            ---
            ### 📬 Próximos Passos:

            1. **Verifique seu e-mail** (inclusive a pasta de spam)
            2. **Clique no link** enviado para redefinir sua senha
            3. **Digite sua nova senha** e confirme

            ⏱️ O link expira em **1 hora** por segurança.
            """)

            # Limpar campo após sucesso
            if "email_recuperacao" in st.session_state:
                del st.session_state.email_recuperacao

        else:
            # Diferenciar entre rate limit e outros erros
            if "⏱️" in mensagem:
                st.warning(mensagem)
            else:
                st.error(mensagem)

    except Exception as e:
        logger.exception(f"Erro ao processar recuperação: {email}")
        st.error(
            "⚠️ Erro inesperado ao processar a solicitação. "
            "Tente novamente em alguns instantes."
        )


# ==========================================================
# 🛡️ PROTEÇÃO CONTRA ERROS INESPERADOS
# ==========================================================

try:
    render()
except Exception as e:
    logger.exception("Erro crítico ao renderizar página de recuperação")
    st.error("❌ Erro inesperado ao carregar a página.")

    if st.button("🔄 Recarregar Página"):
        st.rerun()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = ["render"]

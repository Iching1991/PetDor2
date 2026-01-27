"""
Página 'Sobre' do PETDor2.
Exibe informações sobre o projeto, propósito e tecnologias.
"""

import streamlit as st
import logging

logger = logging.getLogger(__name__)

# ==========================================================
# 🖥️ Render
# ==========================================================

def render():
    st.title("ℹ️ Sobre o PETDor")

    st.markdown(
        """
        ## 🐾 O que é o PETDor?

        O **PETDor** é uma plataforma desenvolvida para auxiliar **tutores, veterinários e clínicas**
        na **avaliação da dor em animais**, utilizando **escalas científicas adaptadas por espécie**.

        O objetivo é oferecer uma ferramenta:
        - Simples
        - Rápida
        - Confiável

        Facilitando a tomada de decisão clínica, o acompanhamento da evolução do paciente
        e a comunicação entre tutor e profissional de saúde animal.

        ---

        ## 🧪 Tecnologias Utilizadas

        - 🐍 **Python 3.13**
        - ⚡ **Streamlit**
        - 🗄️ **Supabase** (Banco de Dados, REST e RLS)
        - 🔐 **JWT** para autenticação e segurança
        - 🌐 **API REST integrada**

        ---

        ## 👥 Criador

        **Agnaldo Angelico Baldissera**  
        *Salute Vitae AI*  
        Desenvolvedor e idealizador do **PETDor**.

        ---

        ## 📬 Contato

        Em caso de dúvidas, sugestões ou parcerias:

        - 📧 **E-mail:** relatorio@petdor.app  
        - 🌐 **Site:** https://petdor.app
        """
    )

    st.divider()

    if st.button("🏠 Voltar para a Página Inicial"):
        st.session_state.pagina = "home"
        st.rerun()


# ==========================================================
# 🛡️ Proteção contra tela branca (Streamlit Cloud)
# ==========================================================

try:
    render()
except Exception as e:
    logger.exception("Erro ao carregar página Sobre")
    st.error("❌ Erro inesperado ao carregar a página 'Sobre'.")
    st.exception(e)


__all__ = ["render"]

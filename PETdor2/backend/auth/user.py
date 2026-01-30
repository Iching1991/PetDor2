"""
Cadastro e autenticação de usuários - PETDor2
USANDO SUPABASE AUTH OFICIAL
"""

from typing import Tuple, Dict, Any
from supabase import create_client
import streamlit as st

# ==========================================================
# Supabase Auth Client
# ==========================================================

supabase = create_client(
    st.secrets["supabase"]["SUPABASE_URL"],
    st.secrets["supabase"]["SUPABASE_SECRET_KEY"],  # SERVICE ROLE
)

# ==========================================================
# Cadastro
# ==========================================================

def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str,
    pais: str,
) -> Tuple[bool, str]:

    try:
        # 1️⃣ Criar usuário no AUTH (envia e-mail automaticamente)
        auth_resp = supabase.auth.sign_up({
            "email": email,
            "password": senha,
            "options": {
                "email_redirect_to": "https://petdor.streamlit.app/confirmar_email"
            }
        })

        if auth_resp.user is None:
            return False, "Falha ao criar usuário."

        user_id = auth_resp.user.id

        # 2️⃣ Criar perfil na tabela usuarios
        supabase.table("usuarios").insert({
            "id": user_id,
            "nome": nome,
            "email": email,
            "tipo_usuario": tipo.lower(),
            "pais": pais,
            "ativo": True,
            "is_admin": False,
        }).execute()

        return True, "Conta criada! Verifique seu e-mail para confirmação."

    except Exception as e:
        return False, f"Erro ao cadastrar: {e}"

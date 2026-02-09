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

import hashlib
import uuid
from typing import Tuple, Optional, Dict, Any

from backend.database import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
)

from backend.email.service import enviar_email
from backend.email.templates import template_confirmacao_email


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode()).hexdigest()


def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    tipo: str,
    pais: str,
) -> Tuple[bool, str]:

    email = email.lower().strip()

    existente = supabase_table_select(
        table="usuarios",
        filters={"email": email},
        limit=1,
    )

    if existente:
        return False, "Este e-mail já está cadastrado."

    token = str(uuid.uuid4())

    usuario = supabase_table_insert(
        table="usuarios",
        data={
            "nome": nome.strip(),
            "email": email,
            "senha_hash": hash_senha(senha),
            "tipo_usuario": tipo.lower(),
            "pais": pais,
            "email_confirmado": False,
            "email_confirm_token": token,
            "ativo": True,
            "is_admin": False,
        },
    )

    if not usuario:
        return False, "Erro ao criar usuário."

    enviar_email(
        destinatario=email,
        assunto="Confirme seu e-mail – PETDor",
        html=template_confirmacao_email(nome, token),
    )

    return True, "Conta criada com sucesso. Verifique seu e-mail."


def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    resultado = supabase_table_select(
        table="usuarios",
        filters={"email": email.lower()},
        limit=1,
    )
    return resultado[0] if resultado else None

from supabase import create_client
import streamlit as st
from typing import Tuple, Dict, Any

supabase = create_client(
    st.secrets["supabase"]["SUPABASE_URL"],
    st.secrets["supabase"]["SUPABASE_KEY"]  # anon key
)

def login_usuario(email: str, senha: str) -> Tuple[bool, Dict[str, Any] | str]:
    try:
        auth = supabase.auth.sign_in_with_password({
            "email": email,
            "password": senha
        })

        if not auth.user:
            return False, "Credenciais inválidas."

        # buscar perfil
        perfil = supabase.table("usuarios").select("*").eq(
            "id", auth.user.id
        ).single().execute().data

        return True, perfil

    except Exception as e:
        return False, str(e)

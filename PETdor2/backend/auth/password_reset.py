from supabase import create_client
import streamlit as st
from typing import Tuple

supabase = create_client(
    st.secrets["supabase"]["SUPABASE_URL"],
    st.secrets["supabase"]["SUPABASE_KEY"]
)

def solicitar_reset_senha(email: str) -> Tuple[bool, str]:
    try:
        supabase.auth.reset_password_for_email(
            email,
            {"redirect_to": "https://petdor.streamlit.app/resetar_senha"}
        )
        return True, "Se o e-mail existir, o link foi enviado."
    except Exception as e:
        return False, str(e)

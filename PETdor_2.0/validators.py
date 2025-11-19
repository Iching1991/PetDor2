# PETdor_2.0/utils/validators.py

"""
Módulo para funções de validação de dados, como e-mails e senhas.
"""
import re

def validar_email(email: str) -> bool:
    """
    Valida o formato de um endereço de e-mail.
    """
    # Regex simples para validação de e-mail. Pode ser mais complexa se necessário.
    # Garante que há um @ e um ponto no domínio.
    if not email or not isinstance(email, str):
        return False
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def validar_senha(senha: str, min_len: int = 6, require_digit: bool = False, require_upper: bool = False) -> bool:
    """
    Valida a complexidade de uma senha.
    Por padrão, verifica apenas o comprimento mínimo.
    Pode ser configurado para exigir dígitos e letras maiúsculas.
    """
    if not senha or not isinstance(senha, str):
        return False
    if len(senha) < min_len:
        return False
    if require_digit and not any(char.isdigit() for char in senha):
        return False
    if require_upper and not any(char.isupper() for char in senha):
        return False
    return True

# Você pode adicionar outras funções de validação aqui conforme a necessidade do projeto.

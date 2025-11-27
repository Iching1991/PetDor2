# PETdor_2.0/utils/validators.py

"""
Módulo para funções de validação de dados, como e-mails e senhas.
"""

import re


# ---------------------------
# Validação de E-mail
# ---------------------------
def validar_email(email: str) -> bool:
    """
    Valida o formato de um endereço de e-mail.
    Regex simples e funcional.
    """
    regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(regex, email) is not None


# ---------------------------
# Validação de Senha
# ---------------------------
def validar_senha(senha: str) -> bool:
    """
    Valida a força de uma senha.
    Requisitos:
    - Mínimo: 8 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 número
    - Pelo menos 1 caractere especial
    """

    if not senha or len(senha) < 8:
        return False

    if not re.search(r"[A-Z]", senha):  # Maiúscula
        return False

    if not re.search(r"[a-z]", senha):  # Minúscula
        return False

    if not re.search(r"\d", senha):  # Número
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):  # Especial
        return False

    return True


# ---------------------------
# (Opcional) Outras validações
# ---------------------------
# Você pode adicionar validação de telefone, CPF, CRMV etc.


#backend/utils/password_strength.py


import re


def calcular_forca_senha(senha: str):

    score = 0

    if len(senha) >= 8:
        score += 20

    if len(senha) >= 12:
        score += 10

    if re.search(r"[A-Z]", senha):
        score += 15

    if re.search(r"[a-z]", senha):
        score += 15

    if re.search(r"[0-9]", senha):
        score += 15

    if re.search(r"[^A-Za-z0-9]", senha):
        score += 15

    if not re.search(r"(.)\1{2,}", senha):  # evita aaa / 111
        score += 10

    return min(score, 100)


def classificar_forca(score: int):

    if score < 40:
        return "Fraca", "red"

    elif score < 70:
        return "Média", "orange"

    elif score < 90:
        return "Forte", "blue"

    else:
        return "Muito forte", "green"

import sqlite3
from .connection import conectar_db # Já está com importação relativa, ótimo!

# ==========================================================
# USUÁRIOS
# ==========================================================
def buscar_usuario_por_email(email: str):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, email, senha, tipo_usuario, pais, email_confirmado
        FROM usuarios
        WHERE email = ?
    """, (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nome": row[1],
            "email": row[2],
            "senha": row[3],
            "tipo_usuario": row[4],
            "pais": row[5],
            "email_confirmado": row[6],
        }
    return None


# ==========================================================
# PETS
# ==========================================================
def buscar_pet_por_id(pet_id: int):
    conn = conectar_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, especie, idade, peso, tutor_id
        FROM pets
        WHERE id = ?
    """, (pet_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "nome": row[1],
            "especie": row[2],
            "idade": row[3],
            "peso": row[4],
            "tutor_id": row[5],
        }
    return None

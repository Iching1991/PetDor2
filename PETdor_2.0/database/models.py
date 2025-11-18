from .connection import conectar_db
import logging

logger = logging.getLogger(__name__)

def buscar_usuario_por_id(usuario_id):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, email, data_criacao, ativo, is_admin
            FROM usuarios
            WHERE id = ?
        """, (usuario_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "data_criacao": row["data_criacao"],
                "ativo": bool(row["ativo"]),
                "is_admin": bool(row["is_admin"])
            }
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar usuario: {e}")
        return None

def buscar_usuario_por_email(email):
    try:
        conn = conectar_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, nome, email, ativo, is_admin
            FROM usuarios
            WHERE email = ?
        """, (email.lower().strip(),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "ativo": bool(row["ativo"]),
                "is_admin": bool(row["is_admin"])
            }
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar usuario por email: {e}")
        return None

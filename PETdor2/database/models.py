# PETdor2/database/models.py

from dataclasses import dataclass
from typing import Optional

from PETdor2.database.connection import conectar_db
import os

USANDO_POSTGRES = bool(os.getenv("DB_HOST"))


# ==========================================================
# MODELOS (DATACLASSES)
# ==========================================================

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha_hash: str
    tipo_usuario: str
    pais: str
    email_confirmado: bool
    ativo: bool
    criado_em: str


@dataclass
class Pet:
    id: int
    nome: str
    especie: str
    tutor_id: int
    idade: Optional[int] = None
    peso: Optional[float] = None
    criado_em: Optional[str] = None


# ==========================================================
# PLACEHOLDER AUTOMÁTICO (SQLite ? / PostgreSQL %s)
# ==========================================================
def placeholder():
    return "%s" if USANDO_POSTGRES else "?"


# ==========================================================
# USUÁRIOS — CONSULTAS
# ==========================================================
def buscar_usuario_por_email(email: str) -> Optional[Usuario]:
    conn = conectar_db()
    cursor = conn.cursor()

    sql = f"""
        SELECT id, nome, email, senha_hash, tipo_usuario, pais,
               email_confirmado, ativo, criado_em
        FROM usuarios
        WHERE email = {placeholder()}
    """

    cursor.execute(sql, (email,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    # PostgreSQL retorna dict; SQLite retorna Row
    return Usuario(
        id=row["id"] if USANDO_POSTGRES else row[0],
        nome=row["nome"] if USANDO_POSTGRES else row[1],
        email=row["email"] if USANDO_POSTGRES else row[2],
        senha_hash=row["senha_hash"] if USANDO_POSTGRES else row[3],
        tipo_usuario=row["tipo_usuario"] if USANDO_POSTGRES else row[4],
        pais=row["pais"] if USANDO_POSTGRES else row[5],
        email_confirmado=row["email_confirmado"] if USANDO_POSTGRES else bool(row[6]),
        ativo=row["ativo"] if USANDO_POSTGRES else bool(row[7]),
        criado_em=row["criado_em"] if USANDO_POSTGRES else row[8],
    )


def buscar_usuario_por_id(user_id: int) -> Optional[Usuario]:
    conn = conectar_db()
    cursor = conn.cursor()

    sql = f"""
        SELECT id, nome, email, senha_hash, tipo_usuario, pais,
               email_confirmado, ativo, criado_em
        FROM usuarios
        WHERE id = {placeholder()}
    """

    cursor.execute(sql, (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return Usuario(
        id=row["id"] if USANDO_POSTGRES else row[0],
        nome=row["nome"] if USANDO_POSTGRES else row[1],
        email=row["email"] if USANDO_POSTGRES else row[2],
        senha_hash=row["senha_hash"] if USANDO_POSTGRES else row[3],
        tipo_usuario=row["tipo_usuario"] if USANDO_POSTGRES else row[4],
        pais=row["pais"] if USANDO_POSTGRES else row[5],
        email_confirmado=row["email_confirmado"] if USANDO_POSTGRES else bool(row[6]),
        ativo=row["ativo"] if USANDO_POSTGRES else bool(row[7]),
        criado_em=row["criado_em"] if USANDO_POSTGRES else row[8],
    )


# ==========================================================
# PETS — CONSULTAS
# ==========================================================
def buscar_pet_por_id(pet_id: int) -> Optional[Pet]:
    conn = conectar_db()
    cursor = conn.cursor()

    sql = f"""
        SELECT id, nome, especie, tutor_id, idade, peso, criado_em
        FROM pets
        WHERE id = {placeholder()}
    """

    cursor.execute(sql, (pet_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return Pet(
        id=row["id"] if USANDO_POSTGRES else row[0],
        nome=row["nome"] if USANDO_POSTGRES else row[1],
        especie=row["especie"] if USANDO_POSTGRES else row[2],
        tutor_id=row["tutor_id"] if USANDO_POSTGRES else row[3],
        idade=row["idade"] if USANDO_POSTGRES else row[4],
        peso=row["peso"] if USANDO_POSTGRES else row[5],
        criado_em=row["criado_em"] if USANDO_POSTGRES else row[6]
    )

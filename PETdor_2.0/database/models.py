# PETdor_2.0/database/models.py

import sqlite3
from dataclasses import dataclass
from typing import Optional
from .connection import conectar_db

# ==========================================================
# DATACLASSES (Modelos de Dados)
# ==========================================================

@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    tipo_usuario: str
    pais: Optional[str] = None
    email_confirmado: bool = False

@dataclass
class Pet: # <-- CORREÇÃO: Campos reordenados aqui!
    id: int
    nome: str
    especie: str
    tutor_id: int               # <-- Campo obrigatório movido para antes dos opcionais
    idade: Optional[int] = None
    peso: Optional[float] = None

# ==========================================================
# USUÁRIOS (Funções de Acesso ao Banco)
# ==========================================================
def buscar_usuario_por_email(email: str) -> Optional[Usuario]:
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
        return Usuario(
            id=row[0],
            nome=row[1],
            email=row[2],
            senha=row[3],
            tipo_usuario=row[4],
            pais=row[5],
            email_confirmado=bool(row[6]),
        )
    return None

# ==========================================================
# PETS (Funções de Acesso ao Banco)
# ==========================================================
def buscar_pet_por_id(pet_id: int) -> Optional[Pet]:
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
        return Pet(
            id=row[0],
            nome=row[1],
            especie=row[2],
            idade=row[3],
            peso=row[4],
            tutor_id=row[5],
        )
    return None



# PETdor_2.0/database/models.py

import sqlite3
from dataclasses import dataclass # <-- Importa dataclass
from typing import Optional # <-- Importa Optional para tipos opcionais
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
class Pet: # <-- NOVA DATACLASS ADICIONADA AQUI!
    id: int
    nome: str
    especie: str
    idade: Optional[int] = None # Assumindo que idade pode ser opcional
    peso: Optional[float] = None
    tutor_id: int

# ==========================================================
# USUÁRIOS (Funções de Acesso ao Banco)
# ==========================================================
def buscar_usuario_por_email(email: str) -> Optional[Usuario]: # <-- Adicionado tipo de retorno
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
        # Retorna uma instância da dataclass Usuario
        return Usuario(
            id=row[0],
            nome=row[1],
            email=row[2],
            senha=row[3],
            tipo_usuario=row[4],
            pais=row[5],
            email_confirmado=bool(row[6]), # Converte para booleano
        )
    return None

# ==========================================================
# PETS (Funções de Acesso ao Banco)
# ==========================================================
def buscar_pet_por_id(pet_id: int) -> Optional[Pet]: # <-- Adicionado tipo de retorno
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
        # Retorna uma instância da dataclass Pet
        return Pet(
            id=row[0],
            nome=row[1],
            especie=row[2],
            idade=row[3],
            peso=row[4],
            tutor_id=row[5],
        )
    return None

# Adicionei também uma dataclass Usuario e ajustei as funções para retornarem instâncias das dataclasses,
# o que é uma boa prática para trabalhar com modelos de dados.

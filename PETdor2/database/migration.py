# PETdor2/database/migration.py
import logging
import streamlit as st
from database.supabase_client import supabase

logger = logging.getLogger(__name__)

def migrar_banco_completo():
    """
    Cria/verifica todas as tabelas necessárias no Supabase.
    Nota: Supabase é baseado em PostgreSQL, mas a criação de tabelas
    deve ser feita via SQL direto ou dashboard. Aqui usamos execuções SQL.
    """
    try:
        # Tabela de usuários
        sql_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            tipo_usuario TEXT NOT NULL DEFAULT 'Tutor',
            pais TEXT NOT NULL DEFAULT 'Brasil',
            email_confirm_token TEXT UNIQUE,
            email_confirmado BOOLEAN NOT NULL DEFAULT FALSE,
            ativo BOOLEAN NOT NULL DEFAULT TRUE,
            data_cadastro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            reset_password_token TEXT UNIQUE,
            reset_password_expires TIMESTAMPTZ
        );
        """
        supabase.rpc("exec_sql", {"query": sql_usuarios}).execute()
        logger.info("Tabela 'usuarios' verificada/criada.")

        # Tabela de pets
        sql_pets = """
        CREATE TABLE IF NOT EXISTS pets (
            id SERIAL PRIMARY KEY,
            nome TEXT NOT NULL,
            especie TEXT NOT NULL,
            raca TEXT,
            data_nascimento DATE,
            id_usuario INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
            data_cadastro TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """
        supabase.rpc("exec_sql", {"query": sql_pets}).execute()
        logger.info("Tabela 'pets' verificada/criada.")

        # Tabela de avaliações
        sql_avaliacoes = """
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id SERIAL PRIMARY KEY,
            id_pet INTEGER REFERENCES pets(id) ON DELETE CASCADE,
            data_avaliacao TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            pontuacao_total INTEGER NOT NULL,
            observacoes TEXT
        );
        """
        supabase.rpc("exec_sql", {"query": sql_avaliacoes}).execute()
        logger.info("Tabela 'avaliacoes' verificada/criada.")

        # Tabela de backups
        sql_backups = """
        CREATE TABLE IF NOT EXISTS backups (
            id SERIAL PRIMARY KEY,
            nome_arquivo TEXT NOT NULL,
            data_backup TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            tamanho_bytes INTEGER,
            caminho_armazenamento TEXT
        );
        """
        supabase.rpc("exec_sql", {"query": sql_backups}).execute()
        logger.info("Tabela 'backups' verificada/criada.")

        logger.info("Migração do banco de dados concluída com sucesso.")

    except Exception as e:
        logger.error(f"Erro ao migrar o banco de dados no Supabase: {e}", exc_info=True)
        st.error(f"Erro crítico ao inicializar o banco de dados. Detalhes: {e}")
        st.stop()

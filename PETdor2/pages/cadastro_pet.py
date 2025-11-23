# PETdor2/pages/cadastro_pet.py
import sys
import os
import logging
from typing import List, Optional, Dict, Any
import streamlit as st

# Configuração do logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Corrige importações para Streamlit Cloud ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
# --- Fim correção ---

# Importações locais
from database.connection import conectar_db
from especies.index import listar_especies, EspecieConfig

# ==========================================================
# Helpers
# ==========================================================

def format_especie_nome(especie_cfg: EspecieConfig) -> str:
    """
    Retorna o nome de exibição da espécie para o selectbox.
    """
    return especie_cfg.nome

def cadastrar_pet_db(
    tutor_id: int,
    nome: str,
    especie_nome: str,
    raca: Optional[str] = None,
    peso: Optional[float] = None
) -> bool:
    """
    Insere um novo pet no banco de dados.
    
    Args:
        tutor_id (int): ID do tutor.
        nome (str): Nome do pet.
        especie_nome (str): Nome da espécie do pet.
        raca (Optional[str]): Raça do pet.
        peso (Optional[float]): Peso do pet em kg.
    
    Returns:
        bool: True se inserido com sucesso, False caso contrário.
    """
    try:
        conn = conectar_db()
        cur = conn.cursor()
        sql = """
            INSERT INTO pets (tutor_id, nome, especie, raca, peso)
            VALUES (?, ?, ?, ?, ?)
        """
        cur.execute(sql, (tutor_id, nome, especie_nome, raca, peso))
        conn.commit()
        logger.info(f"Pet '{nome}' cadastrado com sucesso para tutor {tutor_id}.")
        return True
    except Exception as e:
        logger.error(f"Erro ao cadastrar pet '{nome}': {e}", exc_info=True)
        return False
    finally:
        conn.close()

def listar_pets_db(tutor_id: int) -> List[Dict[str, Any]]:
    """
    Lista todos os pets cadastrados de um tutor.
    
    Args:
        tutor_id (int): ID do tutor.
    
    Returns:
        List[Dict[str, Any]]: Lista de dicionários representando os pets.
    """
    try:
        conn = conectar_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pets WHERE tutor_id = ?", (tutor_id,))
        pets = cur.fetchall()
        return pets
    except Exception as e:
        logger.error(f"Erro ao listar pets do tutor {tutor_id}: {e}", exc_info=True)
        return []
    finally:
        conn.close()

# ==========================================================
# Página principal
# ==========================================================

def render() -> None:
    """
    Renderiza a página de cadastro de pets no Streamlit.
    """
    st.header("🐾 Cadastro de Pet")

    user = st.session_state.get("usuario")
    if not user:
        st.warning("Faça login para cadastrar pets.")
        return

    tutor_id = user["id"]

    # Formulário de cadastro
    with st.form("form_cadastro_pet"):
        nome = st.text_input("Nome do pet")
        especies = listar_especies()
        especie_cfg = st.selectbox(
            "Espécie",
            options=especies,
            format_func=format_especie_nome
        )
        raca = st.text_input("Raça (opcional)")
        peso = st.number_input("Peso (kg)", min_value=0.0, step=0.1)
        enviado = st.form_submit_button("Cadastrar Pet")

    if enviado:
        if not nome or not especie_cfg:
            st.error("Nome e espécie são obrigatórios.")
        else:
            sucesso = cadastrar_pet_db(
                tutor_id=tutor_id,
                nome=nome,
                especie_nome=especie_cfg.nome,
                raca=raca or None,
                peso=peso if peso > 0 else None
            )
            if sucesso:
                st.success(f"Pet '{nome}' cadastrado com sucesso!")
            else:
                st.error(f"Erro ao cadastrar pet '{nome}'. Veja os logs para detalhes.")

    # ======================================================
    # Lista de pets já cadastrados
    # ======================================================
    st.markdown("---")
    st.subheader("Seus pets")

    pets = listar_pets_db(tutor_id)

    if not pets:
        st.info("Nenhum pet cadastrado ainda.")
    else:
        for p in pets:
            nome_pet = p.get("nome") or "Nome não informado"
            especie_pet = p.get("especie") or "Espécie não informada"
            raca_pet = p.get("raca") or "Raça não informada"
            peso_pet = f"{p.get('peso')} kg" if p.get("peso") else "Peso não informado"
            st.write(f"- **{nome_pet}** — {especie_pet} — {raca_pet} — {peso_pet}")


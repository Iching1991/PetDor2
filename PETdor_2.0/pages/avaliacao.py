# pages/avaliacao.py
"""
Página de Avaliação - PETDor
- Seleciona pet do tutor logado
- Carrega perguntas da espécie
- Calcula percentual de dor
- Salva avaliação e respostas no banco
- Gera PDF e envia por e-mail (se configurado)
"""

from datetime import datetime
import sqlite3
import io
import os

import streamlit as st

from database.connection import conectar_db
from especies import get_especie_config, get_especies_nomes
from utils.pdf_generator import gerar_pdf_relatorio
from utils.email_sender import enviar_email

# ---------- Helpers DB ----------
def garantir_tabelas_resposta():
    """Garante que a tabela avaliacao_respostas exista (caso migration não tenha criado)."""
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS avaliacao_respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            avaliacao_id INTEGER NOT NULL,
            pergunta_id TEXT NOT NULL,
            resposta INTEGER NOT NULL,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def listar_pets_do_usuario(usuario_id):
    conn = conectar_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, especie, raca FROM pets WHERE tutor_id = ?", (usuario_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def salvar_avaliacao_e_respostas(usuario_id, pet_id, percentual, observacoes, respostas_dict):
    """Salva a avaliação e as respostas detalhadas. Retorna id da avaliacao."""
    garantir_tabelas_resposta()

    conn = conectar_db()
    cur = conn.cursor()
    now = datetime.now().isoformat()
    cur.execute("""
        INSERT INTO avaliacoes (pet_id, usuario_id, percentual_dor, observacoes, data_avaliacao)
        VALUES (?, ?, ?, ?, ?)
    """, (pet_id, usuario_id, percentual, observacoes, now))
    avaliacao_id = cur.lastrowid

    # salva respostas
    for pergunta_id, resposta in respostas_dict.items():
        cur.execute("""
            INSERT INTO avaliacao_respostas (avaliacao_id, pergunta_id, resposta)
            VALUES (?, ?, ?)
        """, (avaliacao_id, pergunta_id, int(resposta)))

    conn.commit()
    conn.close()
    return avaliacao_id

# ---------- UI ----------
st.title("📋 Avaliação de Dor — PETDor")

# Requer login
if "user_id" not in st.session_state:
    st.warning("Você precisa estar logado para acessar a avaliação.")
    st.info("Faça login ou crie uma conta no menu.")
    st.stop()

usuario_id = st.session_state["user_id"]

# Carrega pets do usuário
pets = listar_pets_do_usuario(usuario_id)
if not pets:
    st.info("Você ainda não cadastrou pets. Vá em 'Cadastrar Pet' para adicionar um.")
    st.stop()

# Seleção do pet
pet_options = {f"{r['nome']} — {r['especie']} (#{r['id']})": r for r in pets}
pet_label = st.selectbox("Escolha o pet para avaliação", list(pet_options.keys()))
pet = pet_options[pet_label]
pet_id = pet["id"]
pet_especie = pet["especie"]

# Carrega configuração da espécie
especie_config = get_especie_config(pet_especie) if pet_especie else None
if not especie_config:
    # tentar buscar por nomes possíveis (normaliza)
    especie_config = get_especie_config(pet_especie or "")
if not especie_config:
    st.error("Configuração para a espécie deste pet não foi encontrada. Contate o suporte.")
    st.stop()

st.markdown(f"### 🐾 {pet['nome']} — {especie_config.nome}")
st.write(especie_config.descricao)

# Observações livres
observacoes = st.text_area("Observações (opcional)")

# Renderiza perguntas dinamicamente
st.markdown("#### Responda as perguntas abaixo (0 = nunca / 7 = sempre)")
respostas = {}  # pergunta_id -> valor

# Calcula máximo possível (soma dos pesos * 7)
max_possivel = sum(p.peso * 7 for p in especie_config.perguntas)
if max_possivel == 0:
    max_possivel = 1  # para evitar divisão por zero

# Exibe perguntas com sliders
for idx, pergunta in enumerate(especie_config.perguntas, start=1):
    pergunta_id = f"q_{idx}"
    label = pergunta.texto
    # streamlit slider 0-7
    val = st.slider(label, 0, 7, 0, key=f"pergunta_{pet_id}_{pergunta_id}")
    respostas[pergunta_id] = {
        "valor": val,
        "invertida": pergunta.invertida,
        "peso": pergunta.peso,
        "texto": pergunta.texto
    }

# Botões de ação
col1, col2 = st.columns(2)
with col1:
    if st.button("Calcular e Salvar Avaliação"):
        # processar respostas
        soma = 0.0
        for pid, info in respostas.items():
            v = int(info["valor"])
            if info["invertida"]:
                v = 7 - v  # inverter
            soma += v * float(info["peso"])

        percentual = round((soma / max_possivel) * 100, 1)

        # grava no banco
        # respostas detalhadas simplificadas: armazenamos o valor original (0-7) por pergunta_id
        respostas_simples = {pid: info["valor"] for pid, info in respostas.items()}
        try:
            avaliacao_id = salvar_avaliacao_e_respostas(usuario_id, pet_id, percentual, observacoes, respostas_simples)
            st.success(f"Avaliação salva — Dor: {percentual}% (ID: {avaliacao_id})")
        except Exception as e:
            st.error(f"Erro ao salvar avaliação: {e}")
            raise

        # gerar PDF e mostrar botão de download
        try:
            pdf_filename = gerar_pdf_relatorio(pet["nome"], {
                "percentual": percentual,
                "observacoes": observacoes,
                "data": datetime.now().isoformat(),
                "respostas": respostas_simples,
                "pet": {"id": pet_id, "nome": pet["nome"], "especie": pet["especie"]}
            })
            # mostrar link de download
            with open(pdf_filename, "rb") as f:
                st.download_button("📥 Baixar Relatório em PDF", f, file_name=os.path.basename(pdf_filename))

            # enviar por e-mail (se quiser)
            enviar_para = st.text_input("Enviar relatório por e-mail (opcional) — digite o e-mail")
            if st.button("Enviar por e-mail"):
                try:
                    enviar_email(enviar_para, f"Relatório PETDor — {pet['nome']}", "Segue em anexo o relatório.", attachments=[pdf_filename])
                    st.success("E-mail enviado (ou simulado).")
                except Exception as e:
                    st.error(f"Falha ao enviar e-mail: {e}")

        except Exception as e:
            st.warning(f"Relatório/PDF não pôde ser gerado: {e}")

with col2:
    if st.button("Limpar respostas"):
        # apenas recarregar a página para reset (simples)
        st.experimental_rerun()

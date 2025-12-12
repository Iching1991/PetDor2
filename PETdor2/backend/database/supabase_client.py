# backend/database/supabase_client.py
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def conectar_supabase():
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Conectado ao Supabase com sucesso!")
        return supabase

    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        return None


# =====================================================
# Obter cliente Supabase
# =====================================================
def get_supabase() -> Client:
    try:
        if "SUPABASE_URL" in st.secrets["supabase"]:
            supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
            supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
        else:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY")

        if not supabase_url or not supabase_key:
            raise RuntimeError("Variáveis do Supabase não configuradas corretamente.")

        return create_client(supabase_url, supabase_key)

    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {e}")
        raise


# =====================================================
# Testar conexão
# =====================================================
def testar_conexao() -> bool:
    try:
        client = get_supabase()
        client.table("usuarios").select("*").limit(1).execute()
        return True
    except Exception as e:
        st.error(f"❌ Falha ao conectar ao Supabase: {e}")
        return False


# =====================================================
# SELECT
# =====================================================
def supabase_table_select(
    tabela: str,
    colunas: str = "*",
    filtros: Optional[Dict[str, Any]] = None,
    order_by: Optional[str] = None,
    desc: bool = False,
    single: bool = False
) -> Tuple[bool, Any]:

    try:
        client = get_supabase()
        query = client.from_(tabela).select(colunas)

        if filtros:
            for k, v in filtros.items():
                query = query.eq(k, v)

        if order_by:
            query = query.order(order_by, desc=desc)

        if single:
            query = query.single()

        resp: APIResponse = query.execute()

        return True, resp.data or {}

    except Exception as e:
        return False, f"Erro no SELECT: {e}"


# =====================================================
# INSERT
# =====================================================
def supabase_table_insert(tabela: str, dados: Dict[str, Any]):
    try:
        client = get_supabase()
        resp: APIResponse = client.from_(tabela).insert(dados).execute()
        return True, resp.data
    except Exception as e:
        return False, f"Erro no INSERT: {e}"


# =====================================================
# UPDATE
# =====================================================
def supabase_table_update(tabela: str, dados_update: Dict[str, Any], filtros: Dict[str, Any]):
    try:
        client = get_supabase()
        query = client.from_(tabela).update(dados_update)

        for k, v in filtros.items():
            query = query.eq(k, v)

        resp: APIResponse = query.execute()
        return True, resp.data

    except Exception as e:
        return False, f"Erro no UPDATE: {e}"


# =====================================================
# DELETE
# =====================================================
def supabase_table_delete(tabela: str, filtros: Dict[str, Any]):
    try:
        client = get_supabase()
        query = client.from_(tabela).delete()

        for k, v in filtros.items():
            query = query.eq(k, v)

        resp: APIResponse = query.execute()
        deleted = len(resp.data) if resp.data else 0

        return True, deleted

    except Exception as e:
        return False, f"Erro no DELETE: {e}"


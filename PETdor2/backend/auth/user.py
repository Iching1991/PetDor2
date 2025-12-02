# PetDor2/auth/user.py
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

# Importações absolutas a partir da raiz do projeto
from database.supabase_client import (
    supabase_table_select,
    supabase_table_insert,
    supabase_table_update,
    supabase_table_delete,
)
from auth.security import hash_password, verify_password # Nomes corretos das funções de hash
from utils.validators import validar_email # Para validação de e-mail
from auth.email_confirmation import enviar_email_confirmacao # Importa a função de envio de e-mail de confirmação

logger = logging.getLogger(__name__)

TABELA_USUARIOS = "usuarios"

# =========================
# Cadastro de Usuário
# =========================
def cadastrar_usuario(
    nome: str,
    email: str,
    senha: str,
    confirmar_senha: str,
    tipo_usuario: str = "Tutor",  # Padrão para "Tutor"
    pais: str = "Brasil",
    is_admin: bool = False, # Define se o usuário é admin no cadastro
) -> Tuple[bool, str]:
    """
    Cadastra um novo usuário no Supabase.
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        # 1. Validações básicas
        if not nome or not email or not senha or not confirmar_senha:
            return False, "Preencha todos os campos obrigatórios."
        if senha != confirmar_senha:
            return False, "As senhas não conferem."
        if not validar_email(email):
            return False, "E-mail inválido."
        if len(senha) < 8: # Adiciona validação de tamanho mínimo da senha
            return False, "A senha deve ter pelo menos 8 caracteres."

        # 2. Verifica se o e-mail já está cadastrado no Supabase
        ok, usuarios_existentes = supabase_table_select(
            TABELA_USUARIOS,
            "id",
            {"email": email.lower()}, # Garante que a busca é case-insensitive
            single=False
        )
        if not ok:
            logger.error(f"Erro ao verificar usuário existente para {email}: {usuarios_existentes}")
            return False, f"Erro ao verificar usuário existente: {usuarios_existentes}"
        if usuarios_existentes:
            return False, "E-mail já cadastrado."

        # 3. Gera hash da senha
        senha_hash = hash_password(senha)

        # 4. Insere o novo usuário no Supabase
        dados_usuario = {
            "nome": nome.strip(),
            "email": email.lower(),
            "senha_hash": senha_hash,
            "tipo": tipo_usuario,  # Coluna 'tipo' no Supabase
            "pais": pais,
            "email_confirmado": False, # Sempre False no cadastro inicial
            "ativo": True,
            "is_admin": is_admin, # Define o status de admin
            "criado_em": datetime.now().isoformat(),
            "atualizado_em": datetime.now().isoformat()
        }

        ok_insert, resultado_insert = supabase_table_insert(TABELA_USUARIOS, dados_usuario)

        if not ok_insert or not resultado_insert:
            logger.error(f"Erro ao salvar usuário {email}: {resultado_insert}")
            return False, f"Erro ao criar conta: {resultado_insert}"

        usuario_criado = resultado_insert[0]
        user_id = usuario_criado["id"]

        # 5. Envia e-mail de confirmação (usando a função de auth.email_confirmation)
        try:
            # A função enviar_email_confirmacao agora gera o token JWT internamente
            # e o salva no banco, então só precisamos passar os dados do usuário.
            sucesso_email = enviar_email_confirmacao(email, nome, user_id)
            if not sucesso_email:
                logger.warning(f"Falha ao enviar email de confirmação para {email}. O usuário foi cadastrado, mas precisa confirmar manualmente.")
        except Exception as e:
            logger.exception(f"Erro inesperado ao tentar enviar email de confirmação para {email}")

        logger.info(f"✅ Usuário {email} cadastrado com ID {user_id} no Supabase")
        return True, "Conta criada com sucesso. Verifique seu e-mail para confirmar."

    except Exception as e:
        logger.exception("Erro geral ao cadastrar usuário no Supabase")
        return False, f"Erro interno ao criar conta: {e}"


# =========================
# Autenticar Usuário
# =========================
def verificar_credenciais(email: str, senha: str) -> Tuple[bool, str | Dict[str, Any]]:
    """
    Verifica credenciais do usuário no Supabase.
    Retorna (True, user_data_dict) em sucesso ou (False, mensagem de erro) em falha.
    """
    try:
        if not email or not senha:
            return False, "E-mail e senha são obrigatórios."

        email = email.strip().lower()

        # 1. Busca usuário no Supabase
        ok, usuario_db = supabase_table_select(
            TABELA_USUARIOS,
            "id, nome, email, senha_hash, tipo, pais, email_confirmado, ativo, is_admin",
            {"email": email},
            single=True
        )

        if not ok:
            logger.error(f"Erro ao buscar usuário {email}: {usuario_db}")
            return False, "Erro ao buscar usuário."
        if not usuario_db:
            return False, "E-mail ou senha incorretos." # Mensagem genérica por segurança

        # 2. Verifica status da conta
        if not usuario_db.get("ativo"):
            return False, "Sua conta está desativada. Entre em contato com o suporte."

        # Opcional: exigir confirmação de e-mail para login
        # if not usuario_db.get("email_confirmado"):
        #     return False, "Confirme seu e-mail antes de entrar."

        # 3. Verifica a senha
        if not verify_password(senha, usuario_db.get("senha_hash", "")):
            logger.warning(f"❌ Falha na autenticação para {email} (senha incorreta)")
            return False, "E-mail ou senha incorretos." # Mensagem genérica por segurança

        # 4. Login bem-sucedido, retorna dados do usuário
        user_data = {
            "id": usuario_db["id"],
            "nome": usuario_db["nome"],
            "email": usuario_db["email"],
            "tipo": usuario_db.get("tipo", "Tutor"), # Garante um valor padrão
            "pais": usuario_db.get("pais", "Brasil"),
            "email_confirmado": bool(usuario_db.get("email_confirmado", False)),
            "ativo": bool(usuario_db.get("ativo", False)),
            "is_admin": bool(usuario_db.get("is_admin", False)),
        }
        logger.info(f"✅ Usuário {email} autenticado com sucesso (ID: {user_data['id']})")
        return True, user_data

    except Exception as e:
        logger.exception("Erro geral na autenticação no Supabase")
        return False, f"Erro interno ao autenticar: {e}"


# =========================
# Buscar Usuário por ID
# =========================
def buscar_usuario_por_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Busca usuário por ID no Supabase.
    Retorna dicionário com dados do usuário ou None.
    """
    try:
        ok, usuario_db = supabase_table_select(
            TABELA_USUARIOS,
            "id, nome, email, tipo, pais, email_confirmado, ativo, is_admin",
            {"id": user_id},
            single=True
        )
        if not ok or not usuario_db:
            return None

        return {
            "id": usuario_db["id"],
            "nome": usuario_db["nome"],
            "email": usuario_db["email"],
            "tipo": usuario_db.get("tipo", "Tutor"),
            "pais": usuario_db.get("pais", "Brasil"),
            "email_confirmado": bool(usuario_db.get("email_confirmado", False)),
            "ativo": bool(usuario_db.get("ativo", False)),
            "is_admin": bool(usuario_db.get("is_admin", False)),
        }
    except Exception as e:
        logger.exception(f"Erro ao buscar usuário por ID {user_id} no Supabase")
        return None

# =========================
# Buscar Usuário por Email
# =========================
def buscar_usuario_por_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário por e-mail no Supabase.
    Retorna dicionário com dados do usuário ou None.
    """
    try:
        email = email.strip().lower()
        ok, usuario_db = supabase_table_select(
            TABELA_USUARIOS,
            "id, nome, email, tipo, pais, email_confirmado, ativo, is_admin",
            {"email": email},
            single=True
        )
        if not ok or not usuario_db:
            return None

        return {
            "id": usuario_db["id"],
            "nome": usuario_db["nome"],
            "email": usuario_db["email"],
            "tipo": usuario_db.get("tipo", "Tutor"),
            "pais": usuario_db.get("pais", "Brasil"),
            "email_confirmado": bool(usuario_db.get("email_confirmado", False)),
            "ativo": bool(usuario_db.get("ativo", False)),
            "is_admin": bool(usuario_db.get("is_admin", False)),
        }
    except Exception as e:
        logger.exception(f"Erro ao buscar usuário por e-mail {email} no Supabase")
        return None

# =========================
# Atualizar Usuário
# =========================
def atualizar_usuario(
    user_id: int,
    nome: Optional[str] = None,
    email: Optional[str] = None,
    tipo: Optional[str] = None, # Renomeado de tipo_usuario para tipo para consistência
    pais: Optional[str] = None,
    is_admin: Optional[bool] = None, # Permite atualizar status de admin
    ativo: Optional[bool] = None, # Permite ativar/desativar
) -> Tuple[bool, str]:
    """
    Atualiza dados do usuário no Supabase.
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        dados_update = {}
        if nome is not None:
            dados_update["nome"] = nome.strip()
        if email is not None:
            dados_update["email"] = email.strip().lower()
        if tipo is not None:
            dados_update["tipo"] = tipo
        if pais is not None:
            dados_update["pais"] = pais
        if is_admin is not None:
            dados_update["is_admin"] = is_admin
        if ativo is not None:
            dados_update["ativo"] = ativo

        dados_update["atualizado_em"] = datetime.now().isoformat()

        if not dados_update:
            logger.warning(f"Nenhum campo para atualizar no usuário {user_id}")
            return True, "Nenhum dado fornecido para atualização."

        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS,
            dados_update,
            {"id": user_id}
        )

        if ok_update:
            logger.info(f"✅ Usuário {user_id} atualizado no Supabase")
            return True, "Usuário atualizado com sucesso."
        else:
            logger.error(f"❌ Falha ao atualizar usuário {user_id}: {resultado_update}")
            return False, f"Erro ao atualizar usuário: {resultado_update}"

    except Exception as e:
        logger.exception(f"Erro ao atualizar usuário {user_id} no Supabase")
        return False, f"Erro interno ao atualizar usuário: {e}"

# =========================
# Alterar Senha
# =========================
def alterar_senha(user_id: int, nova_senha: str) -> Tuple[bool, str]:
    """
    Altera a senha de um usuário no Supabase.
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        if len(nova_senha) < 8:
            return False, "A nova senha deve ter pelo menos 8 caracteres."

        senha_hash = hash_password(nova_senha)
        dados_update = {
            "senha_hash": senha_hash,
            "atualizado_em": datetime.now().isoformat()
        }

        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS,
            dados_update,
            {"id": user_id}
        )

        if ok_update:
            logger.info(f"✅ Senha alterada para usuário {user_id}")
            return True, "Senha alterada com sucesso."
        else:
            logger.error(f"❌ Falha ao alterar senha para usuário {user_id}: {resultado_update}")
            return False, f"Erro ao alterar senha: {resultado_update}"

    except Exception as e:
        logger.exception(f"Erro ao alterar senha para usuário {user_id} no Supabase")
        return False, f"Erro interno ao alterar senha: {e}"

# =========================
# Deletar/Desativar Usuário
# =========================
def deletar_usuario(user_id: int) -> Tuple[bool, str]:
    """
    Desativa um usuário no Supabase (não remove fisicamente).
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        dados_update = {
            "ativo": False,
            "atualizado_em": datetime.now().isoformat()
        }
        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS,
            dados_update,
            {"id": user_id}
        )
        if ok_update:
            logger.info(f"✅ Usuário {user_id} desativado no Supabase")
            return True, "Usuário desativado com sucesso."
        else:
            logger.error(f"❌ Falha ao desativar usuário {user_id}: {resultado_update}")
            return False, f"Erro ao desativar usuário: {resultado_update}"
    except Exception as e:
        logger.exception(f"Erro ao desativar usuário {user_id} no Supabase")
        return False, f"Erro interno ao desativar usuário: {e}"

# =========================
# Marcar E-mail como Confirmado
# =========================
def marcar_email_como_confirmado(user_id: int) -> Tuple[bool, str]:
    """
    Marca o e-mail de um usuário como confirmado no Supabase e remove o token.
    Retorna (True, mensagem de sucesso) ou (False, mensagem de erro).
    """
    try:
        dados_update = {
            "email_confirmado": True,
            "email_confirm_token": None, # Remove o token após a confirmação
            "atualizado_em": datetime.now().isoformat()
        }
        ok_update, resultado_update = supabase_table_update(
            TABELA_USUARIOS,
            dados_update,
            {"id": user_id}
        )
        if ok_update:
            logger.info(f"✅ E-mail confirmado para usuário {user_id}")
            return True, "E-mail confirmado com sucesso."
        else:
            logger.error(f"❌ Falha ao marcar e-mail como confirmado para usuário {user_id}: {resultado_update}")
            return False, f"Erro ao confirmar e-mail: {resultado_update}"
    except Exception as e:
        logger.exception(f"Erro ao marcar e-mail como confirmado para usuário {user_id} no Supabase")
        return False, f"Erro interno ao confirmar e-mail: {e}"

# =========================
# Funções de compatibilidade (para uso em outros módulos)
# =========================
def atualizar_tipo_usuario(user_id: int, novo_tipo: str) -> Tuple[bool, str]:
    """Atualiza o tipo de usuário no Supabase."""
    return atualizar_usuario(user_id, tipo=novo_tipo)

def atualizar_status_usuario(user_id: int, novo_status: bool) -> Tuple[bool, str]:
    """Atualiza o status (ativo/inativo) do usuário no Supabase."""
    return atualizar_usuario(user_id, ativo=novo_status)

# Removida a função 'redefinir_senha' pois a lógica está em auth.password_reset.py
# Removida a função 'gerar_token_confirmacao_para_usuario' pois a lógica está em auth.email_confirmation.py
# Removida a função 'confirmar_email' pois a lógica está em auth.email_confirmation.py

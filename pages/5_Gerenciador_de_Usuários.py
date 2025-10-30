# pages/5_Gerenciador_de_Usuários.py (VERSÃO CORRIGIDA)

import streamlit as st
from src.C_auth import check_authentication
from dotenv import load_dotenv
import bcrypt
import pandas as pd

from src.database import (
    get_user_permissions,
    fetch_all_user_details,
    create_user,
    update_user_role,
    update_user_password,
    delete_user,
    fetch_all_roles
)

st.set_page_config(page_title="Gerenciador de Usuários", layout="wide")

# --- BLOCO DE SEGURANÇA E INICIALIZAÇÃO ---
check_authentication()

load_dotenv()
admin_username = st.session_state.get("username")

# --- CONTROLE DE ACESSO DINÂMICO ---
user_permissions = get_user_permissions(admin_username)

st.header("👥 Gerenciador de Usuários")

if 'pode_gerenciar_usuarios' not in user_permissions:
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()

st.info("Crie, edite e remova usuários da plataforma.")

# --- CRIAR NOVO USUÁRIO ---
with st.expander("➕ Criar Novo Usuário"):
    with st.form("novo_usuario_form", clear_on_submit=True):
        st.subheader("Dados do Novo Usuário")
        novo_username = st.text_input("Nome de Usuário (para login)")
        novo_name = st.text_input("Nome Completo")
        novo_password = st.text_input("Senha Provisória", type="password")
        
        all_roles = fetch_all_roles()
        role_names = [role.name for role in all_roles]
        novo_role = st.selectbox("Perfil de Acesso", role_names)
        
        if st.form_submit_button("Criar Usuário"):
            if all([novo_username, novo_name, novo_password, novo_role]):
                try:
                    password_bytes = novo_password.encode('utf-8')
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
                    create_user(novo_username, novo_name, hashed_password, novo_role)
                    st.success(f"Usuário '{novo_username}' criado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao criar usuário: {e}. O nome de usuário já pode existir.")
            else:
                st.warning("Todos os campos são obrigatórios.")

st.divider()

# --- LISTAR E GERENCIAR USUÁRIOS EXISTENTES ---
st.subheader("Usuários Atuais")
user_list = fetch_all_user_details()

if not user_list:
    st.info("Nenhum usuário encontrado.")
else:
    # --- CORREÇÃO DE NOMES NO DATAFRAME ---
    df_users = pd.DataFrame(user_list, columns=['ID', 'Username', 'Nome Completo', 'Perfil'])
    st.dataframe(df_users, use_container_width=True)

    st.divider()

    st.subheader("Editar Usuário")
    
    # --- CORREÇÃO DO CASE (LETRA MINÚSCULA) ---
    editable_users = [user.username for user in user_list if user.username != admin_username]
    
    if not editable_users:
        st.write("Nenhum outro usuário para editar.")
    else:
        user_to_edit = st.selectbox("Selecione um usuário para editar:", editable_users)
        
        if user_to_edit:
            st.markdown(f"**Mudar Perfil de '{user_to_edit}'**")

            # --- CORREÇÃO DO CASE (LETRA MINÚSCULA) ---
            current_role_name = [user.role_name for user in user_list if user.username == user_to_edit][0]
            
            role_options = [role.name for role in fetch_all_roles()]
            current_role_index = role_options.index(current_role_name)
            
            new_role = st.selectbox("Novo Perfil:", role_options, index=current_role_index, key=f"role_{user_to_edit}")
            if st.button("Atualizar Perfil", key=f"update_role_{user_to_edit}"):
                update_user_role(user_to_edit, new_role)
                st.success(f"Perfil de '{user_to_edit}' atualizado para '{new_role}'.")
                st.rerun()

            st.markdown("---")
            with st.form(f"reset_password_form_{user_to_edit}"):
                st.markdown(f"**Resetar Senha de '{user_to_edit}'**")
                new_password = st.text_input("Nova Senha", type="password", key=f"pwd1_{user_to_edit}")
                confirm_password = st.text_input("Confirmar Nova Senha", type="password", key=f"pwd2_{user_to_edit}")
                if st.form_submit_button("Resetar Senha"):
                    if new_password and new_password == confirm_password:
                        password_bytes = new_password.encode('utf-8')
                        salt = bcrypt.gensalt()
                        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
                        update_user_password(user_to_edit, hashed_password)
                        st.success(f"Senha de '{user_to_edit}' resetada com sucesso!")
                    else:
                        st.error("As senhas não coincidem ou estão em branco.")
            
            st.markdown("---")
            st.markdown(f"**Remover Usuário '{user_to_edit}'**")
            if st.button(f"❌ Deletar Usuário '{user_to_edit}'", type="primary"):
                delete_user(user_to_edit)
                st.success(f"Usuário '{user_to_edit}' deletado com sucesso.")
                st.rerun()
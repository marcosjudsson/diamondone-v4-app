# app.py (VERSÃO CORRIGIDA)

import streamlit as st
from dotenv import load_dotenv
import bcrypt

# Importa APENAS as funções que precisamos
from src.database import create_tables, fetch_all_users, create_admin_user

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv() # Carrega o .env no início de tudo
st.set_page_config(page_title="Plataforma DiamondOne", layout="wide")

# Inicializa as tabelas
create_tables()

# Busca todos os usuários existentes
users_db = fetch_all_users()

# ---- SEÇÃO DE LOGIN ----
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

# Se não houver usuários no banco, mostra o formulário de criação do admin
if not users_db:
    st.warning("Nenhum usuário encontrado. Crie o primeiro administrador.")
    with st.form("primeiro_admin"):
        st.subheader("Criar usuário Administrador inicial")
        username_input = st.text_input("Usuário (nome único)")
        name_input = st.text_input("Nome Completo")
        password_input = st.text_input("Senha", type="password")
        confirm_password_input = st.text_input("Confirme a Senha", type="password")

        if st.form_submit_button("Criar Admin"):
            if not all([username_input, name_input, password_input, confirm_password_input]):
                st.error("Todos os campos são obrigatórios.")
            elif password_input != confirm_password_input:
                st.error("As senhas não coincidem.")
            else:
                try:
                    password_bytes = password_input.encode('utf-8')
                    salt = bcrypt.gensalt()
                    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)
                    hashed_password = hashed_password_bytes.decode('utf-8')
                    
                    # Usa a nova função para criar o usuário
                    create_admin_user(username_input, name_input, hashed_password)
                    
                    st.success("Administrador criado! Por favor, recarregue a página para fazer login.")
                    st.stop()
                except Exception as e:
                    st.error(f"Erro ao criar administrador: {e}")
    st.stop()

# Se o usuário NÃO estiver logado, mostra o formulário de login
if not st.session_state.get("authentication_status"):
    st.header("Login - Plataforma de Inteligência DiamondOne")
    login_username = st.text_input("Usuário", key="login_user")
    login_password = st.text_input("Senha", type="password", key="login_pass")

    if st.button("Login"):
        if login_username in users_db:
            user_data = users_db[login_username]
            stored_password_hash = user_data['password'].encode('utf-8')
            
            if bcrypt.checkpw(login_password.encode('utf-8'), stored_password_hash):
                st.session_state['authentication_status'] = True
                st.session_state['username'] = login_username
                st.session_state['name'] = user_data['name']
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        else:
            st.error("Usuário ou senha incorretos.")
    st.stop()

# --- PÁGINA PRINCIPAL APÓS O LOGIN ---
st.sidebar.title(f"Bem-vindo, {st.session_state['name']}!")
if st.sidebar.button("Sair"):
    st.session_state['authentication_status'] = None
    st.session_state['username'] = None
    st.session_state['name'] = None
    st.rerun()

st.header("Bem-vindo à Plataforma de Inteligência DiamondOne")
st.markdown("Use a barra de navegação à esquerda para acessar as ferramentas.")
st.info("As páginas disponíveis serão exibidas automaticamente com base no seu perfil de acesso.")
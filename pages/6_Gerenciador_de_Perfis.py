# pages/6_Gerenciador_de_Perfis.py

import streamlit as st
from src.C_auth import check_authentication
from dotenv import load_dotenv

from src.database import (
    get_user_role_name,
    fetch_all_roles,
    fetch_all_permissions,
    fetch_permissions_for_role,
    update_role_permissions
)

st.set_page_config(page_title="Gerenciador de Perfis", layout="wide")

# --- BLOCO DE SEGURANÇA E INICIALIZAÇÃO ---
check_authentication()

load_dotenv()
admin_username = st.session_state.get("username")
admin_role_name = get_user_role_name(admin_username)

st.header("⚙️ Gerenciador de Perfis e Permissões")

# --- CONTROLE DE ACESSO ---
# Apenas o perfil 'admin' pode gerenciar outros perfis.
if admin_role_name != 'admin':
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()

st.info("Atribua ou remova permissões para cada perfil de usuário. As alterações são aplicadas a todos os usuários com o perfil selecionado.")

# --- CARREGAMENTO DOS DADOS ---
all_roles = fetch_all_roles()
all_permissions = fetch_all_permissions()

# Remove o perfil 'admin' da lista para evitar auto-edição
editable_roles = [role for role in all_roles if role.name != 'admin']

if not editable_roles:
    st.warning("Nenhum perfil editável encontrado.")
    st.stop()

# --- INTERFACE DE EDIÇÃO ---
# Criamos abas para cada perfil editável (ex: 'gerente', 'usuario')
role_names = [role.name.title() for role in editable_roles]
selected_role_tab = st.tabs(role_names)

for i, tab in enumerate(selected_role_tab):
    with tab:
        current_role = editable_roles[i]
        st.subheader(f"Permissões para o Perfil: '{current_role.name.title()}'")
        
        # Busca as permissões que este perfil já possui
        current_permissions_ids = fetch_permissions_for_role(current_role.id)
        
        # Cria um formulário para cada perfil
        with st.form(f"form_{current_role.name}"):
            # Dicionário para armazenar o estado das checkboxes
            new_permissions = {}
            
            st.write("Marque as ações que este perfil pode executar:")
            # Gera uma checkbox para cada permissão disponível no sistema
            for perm in all_permissions:
                # A checkbox estará marcada se a permissão já estiver atribuída a este perfil
                is_checked = perm.id in current_permissions_ids
                new_permissions[perm.id] = st.checkbox(
                    f"**{perm.name}** (`{perm.description}`)",
                    value=is_checked,
                    key=f"perm_{current_role.id}_{perm.id}"
                )

            if st.form_submit_button("Salvar Permissões"):
                # Coleta os IDs de todas as permissões que foram marcadas
                selected_permission_ids = [pid for pid, is_selected in new_permissions.items() if is_selected]
                
                try:
                    # Atualiza o banco de dados com a nova lista de permissões
                    update_role_permissions(current_role.id, selected_permission_ids)
                    st.success(f"Permissões para o perfil '{current_role.name}' atualizadas com sucesso!")
                    # Limpa os caches para garantir que as novas permissões sejam lidas na próxima vez
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Ocorreu um erro ao salvar as permissões: {e}")
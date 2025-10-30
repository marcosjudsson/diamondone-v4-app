# pages/3_Gerenciador_de_Conhecimento.py (VERSÃO COM PERMISSÃO DINÂmica)

import streamlit as st
from src.C_auth import check_authentication
from dotenv import load_dotenv
import time

# --- ALTERAÇÃO 1: Importar a nova função de permissões ---
from src.database import (
    get_user_permissions, 
    fetch_knowledge_sets, 
    create_knowledge_set, 
    delete_knowledge_set, 
    list_documents_in_set, 
    delete_document_record
)
from src.knowledge_logic import process_and_index_files, rebuild_full_index, process_and_index_url

st.set_page_config(page_title="Gerenciador de Conhecimento", layout="wide")

# --- BLOCO DE SEGURANÇA E INICIALIZAÇÃO ---
check_authentication()

load_dotenv()
username = st.session_state.get("username")

# --- ALTERAÇÃO 2: Bloco de Controle de Acesso Dinâmico ---
user_permissions = get_user_permissions(username)

st.header("📚 Gerenciador de Conhecimento")

if 'pode_gerenciar_conhecimento' not in user_permissions:
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()
# --- FIM DAS ALTERAÇÕES ---

st.info("Crie conjuntos, adicione documentos e processe-os para a base de conhecimento da IA.")

# --- FORMULÁRIO PARA CRIAR NOVO CONJUNTO ---
with st.expander("➕ Criar Novo Conjunto de Conhecimento"):
    with st.form("novo_conjunto_form", clear_on_submit=True):
        novo_nome = st.text_input("Nome do Conjunto")
        nova_desc = st.text_area("Descrição do Conjunto")
        if st.form_submit_button("Criar Conjunto"):
            if novo_nome:
                try:
                    create_knowledge_set(novo_nome, nova_desc, username)
                    st.success(f"Conjunto '{novo_nome}' criado com sucesso!")
                    st.session_state.show_success = True
                except Exception as e:
                    st.error(f"Erro ao criar conjunto: {e}. O nome já pode existir.")
            else:
                st.warning("O nome do conjunto é obrigatório.")

st.divider()

# --- SEÇÃO DE MANUTENÇÃO DO ÍNDICE ---
st.subheader("Manutenção da Base de Conhecimento")
st.warning("A reconstrução do índice é uma operação lenta que reprocessa TODOS os documentos. Use apenas quando arquivos forem removidos ou atualizados.")

if st.button("🚨 Reconstruir Base de Conhecimento Completa", type="primary"):
    with st.spinner("Iniciando a reconstrução completa da base de conhecimento..."):
        progress_bar = st.progress(0, text="Iniciando...")
        status_text = st.empty()
        rebuild_full_index(progress_bar, status_text)
    
    st.cache_data.clear()
    st.cache_resource.clear()
    st.success("Reconstrução finalizada! A aplicação será recarregada.")
    time.sleep(2)
    st.rerun()

st.divider()

# --- EXIBIÇÃO E GERENCIAMENTO DOS CONJUNTOS EXISTENTES ---
st.subheader("Conjuntos de Conhecimento Existentes")
knowledge_sets = fetch_knowledge_sets()

if not knowledge_sets:
    st.info("Nenhum conjunto de conhecimento foi criado ainda.")
else:
    for name, data in knowledge_sets.items():
        set_id = data['id']
        description = data['description']
        
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.caption(f"Descrição: {description if description else 'Nenhuma'}")
            
            st.markdown("**Arquivos Indexados no Conjunto:**")
            arquivos_no_conjunto = list_documents_in_set(set_id)
            if not arquivos_no_conjunto:
                st.write("Nenhum arquivo adicionado a este conjunto ainda.")
            else:
                for filename in arquivos_no_conjunto:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"📄 `{filename}` - **Status:** <span style='color: green;'>Indexado</span>", unsafe_allow_html=True)
                    with col2:
                        if st.button("Remover Registro", key=f"del_file_{set_id}_{filename}"):
                            delete_document_record(filename, set_id)
                            st.warning(f"Registro de '{filename}' removido.")
                            st.cache_data.clear()
                            st.rerun()
            
            st.divider()

            with st.form(f"upload_form_{set_id}", clear_on_submit=True):
                st.markdown("**Adicionar novos documentos a este conjunto:**")
                uploaded_files = st.file_uploader("Selecione os arquivos", key=f"upload_{set_id}", accept_multiple_files=True, type=['pdf', 'docx', 'txt'])
                submitted = st.form_submit_button("Processar e Adicionar à Base")
                
                if submitted and uploaded_files:
                    arquivos_existentes = list_documents_in_set(set_id)
                    arquivos_para_processar = [f for f in uploaded_files if f.name not in arquivos_existentes]
                    arquivos_duplicados = [f for f in uploaded_files if f.name in arquivos_existentes]

                    if arquivos_duplicados:
                        st.warning(f"Arquivos ignorados (já existem): {', '.join([f.name for f in arquivos_duplicados])}")

                    if arquivos_para_processar:
                        progress_bar = st.progress(0, text="Iniciando processamento...")
                        status_text = st.empty()
                        process_and_index_files(arquivos_para_processar, set_id, progress_bar, status_text)
                        st.cache_data.clear()
                        st.success("Processamento concluído!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.info("Nenhum arquivo novo para processar.")
                elif submitted:
                    st.warning("Por favor, selecione ao menos um arquivo para processar.")

            with st.form(f"url_form_{set_id}", clear_on_submit=True):
                st.markdown("**Adicionar a partir de uma URL:**")
                url = st.text_input("Insira a URL completa")
                url_submitted = st.form_submit_button("Processar e Adicionar URL")

                if url_submitted and url:
                    progress_bar = st.progress(0, text="Iniciando processamento da URL...")
                    status_text = st.empty()
                    process_and_index_url(url, set_id, progress_bar, status_text)
                    st.cache_data.clear()
                    st.success("Processamento da URL concluído!")
                    time.sleep(1)
                    st.rerun()
                elif url_submitted:
                    st.warning("Por favor, insira uma URL.")

            if st.button("❌ Deletar Conjunto Inteiro", key=f"delete_set_{set_id}", type="primary"):
                delete_knowledge_set(set_id)
                st.success(f"Conjunto '{name}' deletado.")
                st.cache_data.clear()
                st.rerun()

# --- LÓGICA DE ATUALIZAÇÃO ---
if st.session_state.pop("show_success", False):
    st.success("Operação concluída. Atualizando...")
    time.sleep(1)
    st.rerun()
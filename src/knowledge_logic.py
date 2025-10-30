# src/knowledge_logic.py (VERSÃO COM FEEDBACK DE PROGRESSO)

import shutil # Adicione esta importação no topo do arquivo
import os
import time
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from src.config import get_embeddings_model, FAISS_INDEX_PATH
from src.database import add_document_record # Importamos a nova função

def process_and_index_files(files, set_id, progress_bar, status_text):
    if not files:
        return

    docs = []
    temp_dir = "temp_uploaded_files"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    total_files = len(files)
    for i, file in enumerate(files):
        # --- ATUALIZAÇÃO DO FEEDBACK DE UX ---
        progress = (i + 1) / total_files
        progress_bar.progress(progress, text=f"Processando arquivo {i+1}/{total_files}: {file.name}")
        
        # Registra o arquivo no banco de dados SQL
        add_document_record(file.name, set_id)
        
        temp_filepath = os.path.join(temp_dir, file.name)
        with open(temp_filepath, "wb") as f:
            f.write(file.getbuffer())
        
        loader_map = {".pdf": PyPDFLoader, ".docx": Docx2txtLoader, ".txt": TextLoader}
        ext = os.path.splitext(file.name)[1].lower()
        
        if ext in loader_map:
            try:
                loader = loader_map[ext](temp_filepath)
                loaded_docs = loader.load()
                for doc in loaded_docs:
                    doc.metadata["set_id"] = set_id
                docs.extend(loaded_docs)
            except Exception as e:
                status_text.error(f"Erro ao carregar {file.name}: {e}")
        else:
            status_text.warning(f"Formato não suportado: {file.name}")

    if not docs:
        status_text.error("Nenhum documento pôde ser carregado.")
        return

    status_text.text("Dividindo documentos em trechos (chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    if not chunks:
        status_text.error("Não foi possível extrair conteúdo dos documentos.")
        return

    status_text.text("Gerando embeddings e atualizando o índice vetorial...")
    embeddings = get_embeddings_model()
    if os.path.exists(FAISS_INDEX_PATH):
        vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(FAISS_INDEX_PATH)
    progress_bar.empty() # Limpa a barra de progresso
    status_text.success("Documentos processados e adicionados à base de conhecimento com sucesso!")
    time.sleep(2)

def process_and_index_url(url, set_id, progress_bar, status_text):
    if not url:
        return

    progress_bar.progress(0.1, text=f"Processando URL: {url}")

    try:
        loader = WebBaseLoader(url, header_template={"User-Agent": "DiamondOne/1.0"})
        docs = loader.load()
        for doc in docs:
            doc.metadata["set_id"] = set_id
            doc.metadata["source"] = url # Adiciona a URL como fonte
    except Exception as e:
        status_text.error(f"Erro ao carregar conteúdo da URL {url}: {e}")
        return

    if not docs:
        status_text.error("Nenhum documento pôde ser carregado da URL.")
        return

    status_text.text("Dividindo conteúdo em trechos (chunks)...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    if not chunks:
        status_text.error("Não foi possível extrair conteúdo da URL.")
        return

    status_text.text("Gerando embeddings e atualizando o índice vetorial...")
    embeddings = get_embeddings_model()
    if os.path.exists(FAISS_INDEX_PATH):
        vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        vectorstore.add_documents(chunks)
    else:
        vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(FAISS_INDEX_PATH)
    add_document_record(url, set_id) # Reutiliza a função existente para registrar a URL como um 'documento'

    progress_bar.empty()
    status_text.success(f"URL '{url}' processada e adicionada à base de conhecimento com sucesso!")
    time.sleep(2)
    
    
# Adicione esta função no final de src/knowledge_logic.py

def rebuild_full_index(progress_bar, status_text):
    """
    Apaga o índice FAISS existente e o reconstrói do zero com todos os
    documentos atualmente registrados no banco de dados.
    """
    from src.database import fetch_all_document_paths # Importação local para evitar circularidade

    # --- 1. Apagar o índice antigo ---
    status_text.text("Removendo índice antigo...")
    if os.path.exists(FAISS_INDEX_PATH):
        try:
            shutil.rmtree(FAISS_INDEX_PATH)
            time.sleep(1) # Pequena pausa para garantir que o SO liberou os arquivos
        except Exception as e:
            st.error(f"Não foi possível remover o índice antigo: {e}")
            return
    progress_bar.progress(0.1, text="Índice antigo removido.")

    # --- 2. Buscar todos os documentos válidos ---
    status_text.text("Buscando lista de documentos válidos no banco de dados...")
    all_docs_to_process = fetch_all_document_paths()
    
    if not all_docs_to_process:
        status_text.info("Nenhum documento registrado para indexar. A base de conhecimento está vazia.")
        progress_bar.empty()
        return

    progress_bar.progress(0.2, text=f"Encontrados {len(all_docs_to_process)} documentos para reindexar.")
    time.sleep(1)

    # --- 3. Carregar e Processar todos os arquivos ---
    all_chunks = []
    total_files = len(all_docs_to_process)
    
    for i, (filepath, set_id) in enumerate(all_docs_to_process):
        filename = os.path.basename(filepath)
        progress_bar.progress(0.2 + (0.6 * (i / total_files)), text=f"Processando {filename}...")
        
        if not os.path.exists(filepath):
            st.warning(f"Arquivo '{filename}' registrado no banco mas não encontrado no disco. Pulando.")
            continue

        ext = os.path.splitext(filename)[1].lower()
        loader_map = {".pdf": PyPDFLoader, ".docx": Docx2txtLoader, ".txt": TextLoader}

        if ext in loader_map:
            try:
                loader = loader_map[ext](filepath)
                loaded_docs = loader.load()
                for doc in loaded_docs:
                    doc.metadata["set_id"] = set_id
                
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = text_splitter.split_documents(loaded_docs)
                all_chunks.extend(chunks)
            except Exception as e:
                st.warning(f"Erro ao processar o arquivo '{filename}': {e}. Pulando.")
    
    if not all_chunks:
        status_text.error("Nenhum conteúdo pôde ser extraído dos documentos. O índice não será criado.")
        progress_bar.empty()
        return

    # --- 4. Criar e Salvar o novo índice ---
    progress_bar.progress(0.9, text="Criando novo índice vetorial...")
    status_text.text("Gerando embeddings e criando o novo índice. Isso pode levar um tempo...")
    
    embeddings = get_embeddings_model()
    vectorstore = FAISS.from_documents(all_chunks, embeddings)
    vectorstore.save_local(FAISS_INDEX_PATH)

    progress_bar.progress(1.0)
    status_text.success("Base de Conhecimento reconstruída com sucesso!")
    time.sleep(2)
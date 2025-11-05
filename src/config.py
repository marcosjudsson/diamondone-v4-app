# src/config.py

import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis de ambiente do .env

# --- CONSTANTES COMPARTILHADAS ---
FAISS_INDEX_PATH = "faiss_index"

# --- MODELOS COMPARTILHADOS ---

@st.cache_resource
def get_llm():
    """Retorna o modelo de linguagem (LLM) principal."""
    return ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0.5, streaming=True)

@st.cache_resource
def get_embeddings_model():
    """Retorna o modelo de embeddings."""
    return HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
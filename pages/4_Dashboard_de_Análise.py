# pages/4_Dashboard_de_Análise.py (VERSÃO FINAL COM COMENTÁRIOS)

import streamlit as st
from src.C_auth import check_authentication
from dotenv import load_dotenv
import pandas as pd

from src.database import get_user_permissions, fetch_full_chat_history

st.set_page_config(page_title="Dashboard de Análise", layout="wide")

# --- BLOCO DE SEGURANÇA E INICIALIZAÇÃO ---
check_authentication()

load_dotenv()
username = st.session_state.get("username")
user_permissions = get_user_permissions(username)

st.header("📊 Dashboard de Análise")

# --- CONTROLE DE ACESSO ---
if 'pode_ver_dashboard' not in user_permissions:
    st.error("Você não tem permissão para acessar esta página.")
    st.stop()

# --- CARREGAMENTO DOS DADOS ---
st.subheader("Visão Geral da Utilização")

history_data = fetch_full_chat_history()
if not history_data:
    st.info("Nenhuma interação foi registrada no histórico ainda."); st.stop()

df = pd.DataFrame(history_data, columns=['id', 'session_id', 'username', 'persona_name', 'question', 'answer', 'context', 'feedback', 'feedback_comment', 'timestamp'])

# --- EXIBIÇÃO DOS KPIs ---
st.subheader("Métricas Gerais")
total_interactions = len(df)
unique_users = df['username'].nunique()
pos_feedback_count = df[df['feedback'] == 1].shape[0]
neg_feedback_count = df[df['feedback'] == -1].shape[0]
if not df['persona_name'].empty:
    most_used_persona = df['persona_name'].mode()[0]
else:
    most_used_persona = "N/A"

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Total de Interações", total_interactions)
with col2: st.metric("Usuários Ativos", unique_users)
with col3: st.metric("Persona Mais Utilizada", most_used_persona)
with col4: st.metric("Feedbacks Positivos 👍", pos_feedback_count)
with col5: st.metric("Feedbacks Negativos 👎", neg_feedback_count, delta_color="inverse")

st.divider()

# --- ANÁLISE DE DADOS ---
st.subheader("Análise de Conteúdo e Engajamento")
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Top 5 Perguntas Frequentes")
    most_frequent_questions = df['question'].str.strip().str.lower().value_counts().head(5)
    st.dataframe(most_frequent_questions)

with col2:
    st.subheader("Uso de Personas")
    persona_usage = df['persona_name'].value_counts()
    st.bar_chart(persona_usage)

with col3:
    st.subheader("Top 5 Usuários Ativos")
    top_users = df['username'].value_counts().head(5)
    st.bar_chart(top_users)

st.divider()

# --- SEÇÃO DE REVISÃO DE FEEDBACK NEGATIVO ---
st.subheader("Interações com Feedback Negativo para Revisão")
df_neg_feedback = df[df['feedback'] == -1].sort_values(by='timestamp', ascending=False)
if df_neg_feedback.empty:
    st.success("Ótimo! Nenhuma resposta recebeu feedback negativo até agora.")
else:
    for index, row in df_neg_feedback.iterrows():
        ts = pd.to_datetime(row['timestamp']).strftime('%d/%m/%Y %H:%M')
        with st.expander(f"**{ts}** | **Usuário:** {row['username']} | **Pergunta:** *{row['question'][:50]}...*"):
            st.markdown("**Pergunta:**"); st.info(row['question'])
            st.markdown("**Resposta (que recebeu 👎):**"); st.warning(row['answer'])
            if pd.notna(row['feedback_comment']) and row['feedback_comment']:
                st.markdown("**Comentário do Usuário:**"); st.error(row['feedback_comment'])
            if row['context']:
                st.markdown("**Contexto Utilizado:**"); st.code(row['context'], language='text')

st.divider()

# --- LOG DE INTERAÇÕES RECENTES ---
st.subheader("Log de Todas as Interações Recentes")
df_display = df.copy()
df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%d/%m/%Y %H:%M:%S')

def map_feedback(val):
    if val == 1: return "👍"
    if val == -1: return "👎"
    return "N/A"
df_display['feedback_status'] = df_display['feedback'].apply(map_feedback)

st.dataframe(
    df_display[['timestamp', 'username', 'persona_name', 'question', 'feedback_status']],
    use_container_width=True
)
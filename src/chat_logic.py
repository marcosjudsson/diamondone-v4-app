# src/chat_logic.py (VERSÃO FINAL COM SAÍDAS PADRONIZADAS)

import os
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src import api_integrations
from src import seo_tools
from langchain_core.output_parsers import StrOutputParser
from langchain_classic.chains.history_aware_retriever import create_history_aware_retriever
from langchain_classic.chains.retrieval import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_tavily import TavilySearch
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.config import get_llm, get_embeddings_model, FAISS_INDEX_PATH

@st.cache_resource
def load_persistent_vectorstore():
    if not os.path.exists(FAISS_INDEX_PATH): return None
    return FAISS.load_local(FAISS_INDEX_PATH, get_embeddings_model(), allow_dangerous_deserialization=True)

def get_rag_chain(persona_prompt, allowed_set_ids):
    llm = get_llm()
    vectorstore = load_persistent_vectorstore()
    if vectorstore is None: st.error("Base de conhecimento não criada."); st.stop()
    
    base_retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 20})
    
    def filter_documents(docs):
        return [doc for doc in docs if doc.metadata.get("set_id") in set(allowed_set_ids)]

    filtered_retriever = base_retriever | RunnableLambda(filter_documents)
    
    contextualize_q_prompt = ChatPromptTemplate.from_messages([("system", "Dada a conversa e a pergunta, reformule a pergunta para ser autônoma."), MessagesPlaceholder("chat_history"), ("human", "{input}")])
    history_aware_retriever = create_history_aware_retriever(llm, filtered_retriever, contextualize_q_prompt)
    
    qa_prompt = ChatPromptTemplate.from_messages([("system", persona_prompt), MessagesPlaceholder("chat_history"), ("human", "{input}")])
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    return create_retrieval_chain(history_aware_retriever, question_answer_chain)

def get_web_search_chain(persona_prompt):
    llm = get_llm()
    search_tool = TavilySearch()
    prompt = ChatPromptTemplate.from_messages([("system", persona_prompt), ("human", "Pergunta: {input}\n\nResultados da Web:\n<web_search_results>{web_search_results}</web_search_results>")])

    chain = ({"web_search_results": (lambda x: search_tool.invoke({"query": x["input"]})), "input": RunnablePassthrough()} | prompt | llm | StrOutputParser())
    
    final_chain = RunnablePassthrough.assign(answer=chain, context=lambda x: [])
    return final_chain

def get_hybrid_chain(persona_prompt, allowed_set_ids):
    llm = get_llm()
    vectorstore = load_persistent_vectorstore()
    if vectorstore is None: st.error("Base de conhecimento não criada."); st.stop()

    base_retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5})
    
    def filter_documents(docs):
        return [doc for doc in docs if doc.metadata.get("set_id") in set(allowed_set_ids)]

    filtered_retriever = base_retriever | RunnableLambda(filter_documents)
    search_tool = TavilySearch()
    prompt = ChatPromptTemplate.from_template(persona_prompt)

    context_chain = RunnablePassthrough.assign(
        context=lambda x: filtered_retriever.invoke(x["input"]),
        web_search_results=lambda x: search_tool.invoke({"query": x["input"]}),
        input=lambda x: x["input"]
    )
    
    response_chain = context_chain | prompt | llm | StrOutputParser()
    
    final_chain = RunnablePassthrough.assign(answer=response_chain, context=context_chain.pick("context"))
    return final_chain

from src.config import get_llm, get_embeddings_model, FAISS_INDEX_PATH

def get_seo_analysis_chain(persona_prompt, input_text, keyword, url):
    llm = get_llm()
    embeddings_model = get_embeddings_model()
    search_tool = TavilySearch()

    # Definir o prompt para o agente de SEO, agora incluindo dados de PageSpeed
    prompt_template = ChatPromptTemplate.from_template("""
    Você é um especialista em SEO de alto nível, focado em otimização de conteúdo e performance. Sua tarefa é REESCREVER COMPLETAMENTE o rascunho de post fornecido, otimizando-o para SEO, legibilidade e engajamento, com base na palavra-chave foco, URL de referência e dados de performance.

    Após reescrever o post, forneça uma ANÁLISE DETALHADA das otimizações realizadas, justificando suas escolhas e apresentando as métricas.

    --- INFORMAÇÕES PARA OTIMIZAÇÃO ---
    Tópico: {keyword}
    URL de Referência (ou do post): {url}
    Scores de Performance (PageSpeed Insights): {pagespeed_scores}
    Score de Legibilidade (Flesch Reading Ease): {readability_score} (Scores mais altos são mais fáceis de ler. Idealmente, acima de 60 para um público geral).
    Resultados da Web da Concorrência:
    <web_search_results>{web_search_results}</web_search_results>

    Rascunho Original:
    {input_text}

    --- INSTRUÇÕES DE SAÍDA ---
    1.  Comece com o TEXTO OTIMIZADO DO POST. Este deve ser um artigo completo, pronto para publicação (após revisão humana), com título (H1), meta descrição, introdução, subtítulos (H2, H3), corpo do texto e um Call-to-Action (CTA) forte e específico.
    2.  O texto otimizado deve ter legibilidade aprimorada (frases curtas, parágrafos concisos, listas, negritos).
    3.  Incorpore a palavra-chave foco e termos semânticos relevantes.
    4.  Após o TEXTO OTIMIZADO, insira a linha: `--- ANÁLISE DETALHADA ---`
    5.  Em seguida, forneça a ANÁLISE DETALHADA, explicando as otimizações feitas, justificando as escolhas com base nos dados fornecidos (PageSpeed, Legibilidade, Concorrência) e oferecendo sugestões adicionais (KPIs, Schema Markup, etc.).
    """)

    # Criar a cadeia que primeiro busca na web, analisa a legibilidade, verifica o PageSpeed e depois chama o LLM
    chain = (
        {
            "web_search_results": lambda x: search_tool.invoke({"query": x["keyword"]}),
            "readability_score": lambda x: seo_tools.analyze_readability(x["input_text"]),
            "pagespeed_scores": lambda x: api_integrations.get_psi_data(x["url"]),
            "persona_prompt": lambda x: x["persona_prompt"],
            "input_text": lambda x: x["input_text"],
            "keyword": lambda x: x["keyword"],
            "url": lambda x: x["url"],
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )

    # Invocar a cadeia para obter a análise inicial do LLM
    initial_analysis = chain.invoke({"persona_prompt": persona_prompt, "input_text": input_text, "keyword": keyword, "url": url})

    # Por enquanto, retornamos apenas a análise inicial do LLM.
    return {"answer": initial_analysis, "context": []}


# --- LÓGICA DO ASSISTENTE DE CRIAÇÃO DE PERSONA ---

# --- V1 (FLUXO DIRETO) ---
PROMPT_ASSISTENTE_GERACAO_DIRETA = """
# IDENTIDADE E OBJETIVO
Você é o "Mestre Criador de Agentes" (MeCA), um especialista sênior em engenharia de prompts. Seu único objetivo é gerar um prompt final de alta performance com base no diagnóstico do usuário.

# PROCESSO
Analise o diagnóstico e crie o melhor prompt possível para a tarefa. Sua resposta deve ser APENAS o texto do prompt, sem comentários, explicações ou blocos de código.

# REGRAS
1. O prompt gerado deve ser completo e autocontido.
2. O prompt deve incluir as variáveis corretas ({{context}}, {{web_search_results}}, {{input}}) com base na "Fonte de Conhecimento" definida no diagnóstico.
---
DIAGNÓSTICO FORNECIDO PELO USUÁRIO:
- **Objetivo Final do Agente:** {objetivo_final}
- **Público-Alvo do Agente:** {usuario_final}
- **Persona e Tom do Agente:** {persona_e_tom}
- **Formato de Saída Desejado:** {formato_saida}
- **Fonte de Conhecimento Principal:** {fonte_conhecimento}
---
Agora, gere o prompt final.
"""

def gerar_prompt_final_direto(diagnostico: dict) -> str:
    """
    Usa o LLM para gerar o prompt final diretamente do diagnóstico fornecido pelo formulário.
    """
    llm = get_llm()
    prompt_template = ChatPromptTemplate.from_template(PROMPT_ASSISTENTE_GERACAO_DIRETA)
    
    geracao_chain = prompt_template | llm | StrOutputParser()
    
    # O dicionário 'diagnostico' do formulário é passado diretamente para o prompt.
    return geracao_chain.invoke(diagnostico)

# --- V2 (FLUXO 3-PASSOS) ---

PROMPT_ASSISTENTE_BRAINSTORMING = """
# IDENTIDADE E OBJETIVO
Você é o "Mestre Criador de Agentes" (MeCA), um especialista sênior em engenharia de prompts. Seu objetivo é atuar como um "Parceiro Criativo" para o usuário.

# PROCESSO
Com base no diagnóstico fornecido, sugira 2 a 3 abordagens ou estratégias diferentes para a estrutura do prompt final. Apresente os prós e contras de cada uma de forma clara e concisa. Estruture sua resposta usando Markdown e separe as abordagens com '---'.

# EXEMPLO DE RESPOSTA
**Abordagem 1: Resposta Direta**
- **Prós:** Simples, rápido, eficiente em tokens.
- **Contras:** Pode ser menos detalhado.
---
**Abordagem 2: Chain of Thought (CoT)**
- **Prós:** Gera respostas mais elaboradas e lógicas.
- **Contras:** Usa mais tokens e pode ser mais lento.
---
DIAGNÓSTICO FORNECIDO PELO USUÁRIO:
- **Objetivo Final do Agente:** {objetivo_final}
- **Público-Alvo do Agente:** {usuario_final}
- **Persona e Tom do Agente:** {persona_e_tom}
- **Formato de Saída Desejado:** {formato_saida}
- **Fonte de Conhecimento Principal:** {fonte_conhecimento}
---
Agora, gere as sugestões de abordagem.
"""

PROMPT_ASSISTENTE_EXECUCAO = """
# IDENTIDADE E OBJETIVO
Você é o "Mestre Criador de Agentes" (MeCA), um especialista sênior em engenharia de prompts. Seu objetivo é gerar um prompt final de alta performance com base no diagnóstico do usuário e na diretriz de abordagem que ele escolheu.

# PROCESSO
Analise o diagnóstico e a diretriz de abordagem. Crie o melhor prompt final possível para a tarefa. Sua resposta deve ser APENAS o texto do prompt, sem comentários, explicações ou blocos de código.

# REGRAS
1. O prompt gerado deve ser completo e autocontido.
2. **CRÍTICO:** O prompt DEVE incluir as variáveis corretas ({{context}}, {{web_search_results}}, {{input}}) com base na "Fonte de Conhecimento" definida no diagnóstico. **Exemplo: Se a fonte é RAG_ONLY, o prompt DEVE conter {{context}} e {{input}}.**
---
DIAGNÓSTICO FORNECIDO PELO USUÁRIO:
- **Objetivo Final do Agente:** {objetivo_final}
- **Público-Alvo do Agente:** {usuario_final}
- **Persona e Tom do Agente:** {persona_e_tom}
- **Formato de Saída Desejado:** {formato_saida}
- **Fonte de Conhecimento Principal:** {fonte_conhecimento}

DIRETRIZ DE ABORDAGEM ESCOLHIDA:
{diretriz_abordagem}
---
Agora, gere o prompt final.
"""

def gerar_sugestoes(diagnostico: dict) -> str:
    """Usa o LLM para gerar sugestões de abordagens de prompt."""
    llm = get_llm()
    prompt_template = ChatPromptTemplate.from_template(PROMPT_ASSISTENTE_BRAINSTORMING)
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke(diagnostico)

def gerar_prompt_final_com_abordagem(diagnostico: dict, diretriz_abordagem: str) -> str:
    """Usa o LLM para gerar o prompt final com base no diagnóstico e na abordagem escolhida."""
    llm = get_llm()
    prompt_template = ChatPromptTemplate.from_template(PROMPT_ASSISTENTE_EXECUCAO)
    chain = prompt_template | llm | StrOutputParser()
    
    input_data = {**diagnostico, "diretriz_abordagem": diretriz_abordagem}
    
    return chain.invoke(input_data)
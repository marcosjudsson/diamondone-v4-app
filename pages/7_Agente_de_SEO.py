import streamlit as st
import pyperclip
from src.chat_logic import get_seo_analysis_chain

st.set_page_config(page_title="Agente de SEO", page_icon="📈")

st.title("📈 Agente de SEO")
st.markdown("Analise e otimize seu conteúdo para motores de busca.")

# Inicializa st.session_state para armazenar o resultado da análise
if 'analysis_output' not in st.session_state:
    st.session_state.analysis_output = None

# Campos de entrada para o usuário
post_draft = st.text_area("Rascunho do Post/Conteúdo", height=300, help="Cole aqui o rascunho do seu artigo ou conteúdo para análise.")
keyword = st.text_input("Palavra-chave Foco", help="Qual é a palavra-chave principal que você deseja otimizar?")
url = st.text_input("URL de Referência (Opcional)", help="URL do seu post (se já publicado) ou de um concorrente para análise de PageSpeed e contexto.")

if st.button("Analisar SEO"):
    if not post_draft or not keyword:
        st.warning("Por favor, preencha o Rascunho do Post e a Palavra-chave Foco.")
    else:
        with st.spinner("Analisando seu conteúdo... Isso pode levar alguns segundos."):
            try:
                # A persona_prompt será fixa para o agente de SEO
                persona_prompt = "Você é um especialista em SEO de alto nível, focado em otimização de conteúdo e performance. Forneça análises detalhadas e sugestões acionáveis."
                
                analysis_result = get_seo_analysis_chain(
                    persona_prompt=persona_prompt,
                    input_text=post_draft,
                    keyword=keyword,
                    url=url if url else None # Passa None se a URL estiver vazia
                )
                
                # Armazena o resultado na session_state
                st.session_state.analysis_output = analysis_result["answer"]

            except Exception as e:
                st.error(f"Ocorreu um erro durante a análise: {e}")
                st.exception(e)
                st.session_state.analysis_output = None # Limpa o resultado em caso de erro

# Exibe os resultados se houver algo na session_state
if st.session_state.analysis_output:
    st.subheader("Resultados da Análise de SEO:")

    # Divide a resposta do LLM usando o delimitador
    if "--- ANÁLISE DETALHADA ---" in st.session_state.analysis_output:
        optimized_text, detailed_analysis = st.session_state.analysis_output.split("--- ANÁLISE DETALHADA ---", 1)
        
        st.markdown("### Post Otimizado:")
        st.markdown(optimized_text.strip()) # Exibe o texto otimizado formatado
        if st.button("Copiar Post Otimizado", key="copy_optimized_post"):
            pyperclip.copy(optimized_text.strip())
            st.toast("Post otimizado copiado para a área de transferência!")

        with st.expander("Ver Análise Detalhada e Justificativas"):
            st.markdown(detailed_analysis.strip()) # Exibe a análise detalhada formatada
            if st.button("Copiar Análise Detalhada", key="copy_detailed_analysis"):
                pyperclip.copy(detailed_analysis.strip())
                st.toast("Análise detalhada copiada para a área de transferência!")
    else:
        # Caso o delimitador não seja encontrado (fallback)
        st.markdown("### Análise Completa (Formato Antigo ou Sem Delimitador):")
        st.write(st.session_state.analysis_output)

# pages/2_Gerenciador_de_Personas.py (VERSÃO FINAL, COMPLETA E VALIDADA)

import streamlit as st
from src.C_auth import check_authentication
from dotenv import load_dotenv

from src.database import (
    get_user_permissions, fetch_personas, create_persona, update_persona, delete_persona, 
    create_default_personas, PERSONAS_PADRAO, fetch_knowledge_sets, 
    link_persona_to_sets, fetch_linked_sets_for_persona, fetch_persona_history
)
from src.chat_logic import gerar_sugestoes, gerar_prompt_final_com_abordagem

# --- FUNÇÕES AUXILIARES E CALLBACKS ---

def restaurar_prompt_callback(persona_nome, prompt, access_level, username, editor_key):
    """
    Callback para o botão de restaurar.
    Atualiza o BD e o estado da sessão para o editor de texto.
    """
    update_persona(persona_nome, prompt, access_level, username, save_history=False)
    # Deleta o estado do widget para forçá-lo a recarregar o valor do banco na próxima execução
    if editor_key in st.session_state:
        del st.session_state[editor_key]
    st.session_state.restore_success = f"Prompt da persona '{persona_nome}' restaurado com sucesso."

def validar_prompt(prompt_text, access_level):
    variaveis_necessarias = ["{input}"]
    if access_level in ["RAG_ONLY", "HYBRID"]: variaveis_necessarias.append("{context}")
    if access_level in ["WEB_ONLY", "HYBRID"]: variaveis_necessarias.append("{web_search_results}")
    return [var for var in variaveis_necessarias if var not in prompt_text]

def gerar_texto_correcao(ausentes):
    correcao = ""
    if "{context}" in ausentes: correcao += "\n\nContexto Interno:\n{context}"
    if "{web_search_results}" in ausentes: correcao += "\n\nResultados da Web:\n{web_search_results}"
    if "{input}" in ausentes: correcao += "\n\nInput do Usuário:\n{input}"
    return correcao

# --- CONFIGURAÇÃO DA PÁGINA E SEGURANÇA ---
st.set_page_config(page_title="Gerenciador de Personas", layout="wide")

check_authentication()

load_dotenv()
username = st.session_state.get("username")
user_permissions = get_user_permissions(username)
can_edit = 'pode_gerenciar_personas' in user_permissions

st.header("🎭 Gerenciador de Personas")

# Exibe a mensagem de sucesso de restauração se o flag estiver no estado da sessão
if st.session_state.get("restore_success"):
    st.success(st.session_state.restore_success)
    del st.session_state.restore_success

if can_edit: st.info("Crie, edite e delete as personalidades do seu especialista de IA.")
else: st.info("Visualize as personalidades disponíveis do especialista de IA.")

# --- MODO DE LEITURA PARA USUÁRIOS SEM PERMISSÃO ---
if not can_edit:
    st.warning("Você não tem permissão para editar. Acesso somente leitura.")
    personas_db = fetch_personas()
    if not personas_db:
        st.info("Nenhuma persona foi criada ainda.")
    else:
        st.subheader("Personas Disponíveis:")
        for nome, data in personas_db.items():
            access_level_str = data.get('access_level', 'N/A').replace('_', ' ').title()
            with st.expander(f"**{nome}** (Tipo: {access_level_str})"):
                st.code(data['prompt'], language='text')
    st.stop()

# --- INTERFACE DE EDIÇÃO PARA USUÁRIOS COM PERMISSÃO ---

# Inicialização dos estados da sessão para o assistente
if 'assistant_mode' not in st.session_state: st.session_state.assistant_mode = False
if 'sugestoes_prompt' not in st.session_state: st.session_state.sugestoes_prompt = None
if 'diagnostico_data' not in st.session_state: st.session_state.diagnostico_data = None
if 'prompt_invalido_info' not in st.session_state: st.session_state.prompt_invalido_info = None

st.divider()
if st.button("✨ Usar Assistente de Criação de Persona", type="primary"):
    st.session_state.assistant_mode = not st.session_state.assistant_mode
    st.session_state.sugestoes_prompt = None
    st.session_state.diagnostico_data = None

# --- MODO ASSISTENTE V2 (3-PASSOS) ---
if st.session_state.assistant_mode:
    # Etapa 1: Diagnóstico
    if not st.session_state.sugestoes_prompt:
        st.subheader("🤖 Assistente de Criação - Etapa 1: Diagnóstico")
        st.caption("Preencha os campos abaixo para que o assistente de IA (MeCA) sugira abordagens para seu prompt.")
        
        with st.form("diagnostico_form_v2"):
            nome_persona = st.text_input("Primeiro, dê um nome para a nova persona:")
            objetivo_final = st.text_area("1. Qual resultado o novo agente deve gerar? (Ex: Criar um resumo técnico de um artigo)")
            usuario_final = st.text_area("2. Quem irá usar o novo agente e qual seu nível de conhecimento? (Ex: Engenheiros de software sênior)")
            persona_e_tom = st.text_area("3. Como o novo agente deve se comportar e comunicar? (Ex: Formal, direto ao ponto, como um especialista)")
            formato_saida = st.text_area("4. Qual o formato do resultado que o novo agente deve entregar? (Ex: Tópicos, JSON, um parágrafo de texto)")
            
            fonte_conhecimento_map = {"Apenas Base de Conhecimento": "RAG_ONLY", "Apenas Busca na Web": "WEB_ONLY", "Híbrido (Base + Web)": "HYBRID"}
            fonte_conhecimento_display = st.selectbox("5. O agente dependerá de documentos, da web, ou ambos?", options=list(fonte_conhecimento_map.keys()))
            
            if st.form_submit_button("Gerar Sugestões de Abordagem", type="primary"):
                if not nome_persona: 
                    st.error("O nome da persona é obrigatório.")
                else:
                    access_level_selecionado = fonte_conhecimento_map[fonte_conhecimento_display]
                    diagnostico_data = {
                        "nome_persona": nome_persona, "objetivo_final": objetivo_final, "usuario_final": usuario_final,
                        "persona_e_tom": persona_e_tom, "formato_saida": formato_saida,
                        "fonte_conhecimento": fonte_conhecimento_display, "access_level": access_level_selecionado
                    }
                    with st.spinner("O Mestre Criador de Agentes (MeCA) está pensando nas abordagens..."):
                        st.session_state.diagnostico_data = diagnostico_data # Store for later steps
                        st.session_state.sugestoes_prompt = gerar_sugestoes(diagnostico_data)
                    st.rerun()

    # Etapas 2 & 3: Brainstorming e Execução
    if st.session_state.sugestoes_prompt and st.session_state.diagnostico_data:
        st.subheader("🤖 Assistente de Criação - Etapa 2: Brainstorming")
        st.caption("O assistente sugeriu as seguintes abordagens. Escolha uma para gerar o prompt final.")
        
        sugestoes = st.session_state.sugestoes_prompt.split('---')
        
        for i, sugestao in enumerate(sugestoes):
            if sugestao.strip():
                st.markdown(sugestao)
                # Extrai a primeira linha da sugestão para usar como diretriz
                diretriz_abordagem = sugestao.strip().split('\n')[0].strip()
                
                if st.button(f"Gerar Prompt com a Abordagem {i+1}", key=f"btn_abordagem_{i}"):
                    with st.spinner("O MeCA está finalizando o prompt com a abordagem escolhida..."):
                        prompt_final = gerar_prompt_final_com_abordagem(st.session_state.diagnostico_data, diretriz_abordagem)
                    
                    # Pre-fill the manual creation form
                    st.session_state.prefill_nome = st.session_state.diagnostico_data['nome_persona']
                    st.session_state.prefill_prompt = prompt_final
                    st.session_state.prefill_access_level = st.session_state.diagnostico_data['access_level']
                    
                    # Reset and exit assistant mode
                    st.session_state.assistant_mode = False
                    st.session_state.sugestoes_prompt = None
                    st.session_state.diagnostico_data = None
                    st.success("Prompt gerado! Revise e salve a nova persona abaixo.")
                    st.rerun()
        
        st.divider()
        if st.button("Voltar e refazer diagnóstico", key="refazer_diagnostico"):
            st.session_state.sugestoes_prompt = None
            st.session_state.diagnostico_data = None
            st.rerun()

# --- MODO MANUAL (SÓ APARECE SE O ASSISTENTE ESTIVER DESLIGADO) ---
if not st.session_state.assistant_mode:
    nome_default = st.session_state.get('prefill_nome', "")
    prompt_default = st.session_state.get('prefill_prompt', "")
    level_default = st.session_state.get('prefill_access_level', "RAG_ONLY")
    access_level_options = ["RAG_ONLY", "WEB_ONLY", "HYBRID"]
    default_index = access_level_options.index(level_default) if level_default in access_level_options else 0

    with st.expander("➕ Criar Nova Persona Manualmente", expanded=True):
        with st.form("nova_persona_form", clear_on_submit=False):
            novo_nome = st.text_input("Nome da Persona", value=nome_default) # <-- CORRIGIDO O ')' EXTRA
            novo_access_level = st.selectbox("Tipo de Acesso:", options=access_level_options, index=default_index, format_func=lambda x: {"RAG_ONLY": "Apenas Base de Conhecimento", "WEB_ONLY": "Apenas Busca na Web", "HYBRID": "Híbrido (Base + Web)"}.get(x, x))
            novo_prompt = st.text_area("Prompt da Persona", value=prompt_default, height=300)
            
            submitted = st.form_submit_button("Criar Persona")
            if submitted:
                if novo_nome and novo_prompt:
                    variaveis_ausentes = validar_prompt(novo_prompt, novo_access_level)
                    if not variaveis_ausentes:
                        try:
                            create_persona(novo_nome, novo_prompt, username, novo_access_level)
                            st.success(f"Persona '{novo_nome}' criada!")
                            st.session_state.prompt_invalido_info = None
                            if 'prefill_nome' in st.session_state: del st.session_state['prefill_nome']
                            if 'prefill_prompt' in st.session_state: del st.session_state['prefill_prompt']
                            if 'prefill_access_level' in st.session_state: del st.session_state['prefill_access_level']
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao criar persona: {e}.")
                    else:
                        st.session_state.prompt_invalido_info = {"tipo": "criar", "nome": novo_nome, "prompt": novo_prompt, "access_level": novo_access_level, "ausentes": variaveis_ausentes}
                else:
                    st.warning("Preencha o nome e o prompt.")

    if st.session_state.prompt_invalido_info and st.session_state.prompt_invalido_info['tipo'] == 'criar':
        info = st.session_state.prompt_invalido_info
        ausentes_str = ', '.join(info['ausentes'])
        st.warning(f"**Validação Pendente:** O prompt não contém `{ausentes_str}`.")
        if st.button("Adicionar Variáveis e Criar Mesmo Assim", key="criar_corrigido"):
            texto_correcao = gerar_texto_correcao(info['ausentes'])
            prompt_corrigido = info['prompt'] + texto_correcao
            try:
                create_persona(info['nome'], prompt_corrigido, username, info['access_level'])
                st.success(f"Persona '{info['nome']}' criada com o prompt corrigido!")
                st.session_state.prompt_invalido_info = None
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao criar persona: {e}.")

    st.divider()

    # --- SEÇÃO DE EDIÇÃO ---
    personas_db = fetch_personas()
    knowledge_sets = fetch_knowledge_sets()
    set_name_to_id = {name: data['id'] for name, data in knowledge_sets.items()}
    set_id_to_name = {data['id']: name for name, data in knowledge_sets.items()}

    if not personas_db:
        st.info("Nenhuma persona encontrada. Crie sua primeira ou carregue as personas padrão.")
        if st.button("Criar Personas Padrão"):
            create_default_personas(username)
            st.success("Personas padrão criadas com sucesso!")
            st.rerun()
    else:
        st.subheader("Editar Personas e Vincular Conhecimento")
        persona_selecionada_nome = st.selectbox("Selecione uma persona:", options=list(personas_db.keys()))
        
        # ... (O resto do código da seção de edição, que já estava funcionando)
    
    persona_data = personas_db.get(persona_selecionada_nome, {})
    persona_id = persona_data.get("id")
    prompt_atual = persona_data.get("prompt", "")
    access_level_atual = persona_data.get("access_level", "RAG_ONLY")
    
    access_level_options = ["RAG_ONLY", "WEB_ONLY", "HYBRID"]
    indice_atual = access_level_options.index(access_level_atual)

    access_level_editado = st.selectbox("Tipo de Acesso:", options=access_level_options, index=indice_atual, format_func=lambda x: {"RAG_ONLY": "Apenas Base de Conhecimento", "WEB_ONLY": "Apenas Busca na Web", "HYBRID": "Híbrido (Base + Web)"}.get(x, x), key=f"access_level_{persona_id}")
    
    editor_key = f"editor_{persona_id}"
    prompt_editado = st.text_area("Edite o prompt:", value=prompt_atual, height=200, key=editor_key)
    
    # --- HISTÓRICO DE ALTERAÇÕES ---
    with st.expander("Ver Histórico de Alterações"):
        historico = fetch_persona_history(persona_id)
        if not historico:
            st.info("Nenhuma alteração anterior registrada para esta persona.")
        else:
            for i, registro in enumerate(historico):
                # Formata a data para um formato mais legível
                data_formatada = registro.changed_at.strftime('%d/%m/%Y %H:%M:%S')
                st.markdown(f"**Versão de {data_formatada} por `{registro.changed_by}`**")
                st.code(registro.prompt, language='text')
                st.button(
                    "Restaurar esta versão", 
                    key=f"restore_v_{persona_id}_{i}",
                    on_click=restaurar_prompt_callback,
                    args=(persona_selecionada_nome, registro.prompt, registro.access_level, username, editor_key)
                )
                st.divider()

    st.divider()
    
    conjuntos_selecionados = []
    if access_level_editado in ["RAG_ONLY", "HYBRID"]:
        st.markdown("**Vincular Conjuntos de Conhecimento**")
        if not knowledge_sets:
            st.warning("Nenhum conjunto de conhecimento foi criado. Vá para o 'Gerenciador de Conhecimento'.")
        else:
            ids_vinculados = fetch_linked_sets_for_persona(persona_id)
            nomes_vinculados = [set_id_to_name.get(id) for id in ids_vinculados if id in set_id_to_name]
            conjuntos_selecionados = st.multiselect("Conjuntos de Conhecimento disponíveis:", options=list(knowledge_sets.keys()), default=nomes_vinculados, key=f"multiselect_{persona_id}")
    
    st.divider()
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        if st.button("Salvar Alterações", key=f"save_{persona_id}"):
            variaveis_ausentes = validar_prompt(prompt_editado, access_level_editado)
            if not variaveis_ausentes:
                update_persona(persona_selecionada_nome, prompt_editado, access_level_editado, username, save_history=True)
                if access_level_editado in ["RAG_ONLY", "HYBRID"] and knowledge_sets:
                    ids_para_vincular = [set_name_to_id[name] for name in conjuntos_selecionados]
                    link_persona_to_sets(persona_id, ids_para_vincular)
                else:
                    link_persona_to_sets(persona_id, [])
                st.success(f"Persona '{persona_selecionada_nome}' atualizada!")
                st.session_state.prompt_invalido_info = None
                st.rerun()
            else:
                st.session_state.prompt_invalido_info = {"tipo": "editar", "nome": persona_selecionada_nome, "prompt": prompt_editado, "access_level": access_level_editado, "ausentes": variaveis_ausentes, "conjuntos_selecionados": conjuntos_selecionados}

    with col2:
        if persona_selecionada_nome in PERSONAS_PADRAO:
            if st.button("Restaurar Padrão", key=f"restore_{persona_id}"):
                dados_padrao = PERSONAS_PADRAO[persona_selecionada_nome]
                update_persona(persona_selecionada_nome, dados_padrao['prompt'], dados_padrao['access_level'], username, save_history=True)
                st.success(f"Persona '{persona_selecionada_nome}' restaurada para o padrão!")
                st.session_state.prompt_invalido_info = None
                st.rerun()

    with col3:
        if st.button("❌ Deletar", type="primary", key=f"delete_{persona_id}"):
            delete_persona(persona_selecionada_nome)
            st.success(f"Persona '{persona_selecionada_nome}' deletada!")
            st.session_state.prompt_invalido_info = None
            st.rerun()

    if st.session_state.prompt_invalido_info and st.session_state.prompt_invalido_info['tipo'] == 'editar' and st.session_state.prompt_invalido_info['nome'] == persona_selecionada_nome:
        info = st.session_state.prompt_invalido_info
        ausentes_str = ', '.join(info['ausentes'])
        st.warning(f"**Validação Pendente:** O prompt não contém `{ausentes_str}`.")
        
        if st.button("Adicionar Variáveis e Salvar Mesmo Assim", key="editar_corrigido"):
            texto_correcao = gerar_texto_correcao(info['ausentes'])
            prompt_corrigido = info['prompt'] + texto_correcao
            update_persona(info['nome'], prompt_corrigido, info['access_level'], username, save_history=True)
            
            if info['access_level'] in ["RAG_ONLY", "HYBRID"] and knowledge_sets:
                ids_para_vincular = [set_name_to_id[name] for name in info['conjuntos_selecionados']]
                link_persona_to_sets(persona_id, ids_para_vincular)

            st.success(f"Persona '{info['nome']}' atualizada com o prompt corrigido!")
            st.session_state.prompt_invalido_info = None
            st.rerun()
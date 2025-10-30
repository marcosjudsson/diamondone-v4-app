# src/database.py (VERSÃO FINAL, COMPLETA E VALIDADA PARA PERMISSÕES)

import os
from sqlalchemy import create_engine, text
import streamlit as st
from dotenv import load_dotenv

# --- DADOS PADRÃO ---
PERSONAS_PADRAO = {
    "Consultor Geral": {
        "prompt": """Você é um consultor especialista no sistema DiamondOne para indústrias de manufatura. Sua tarefa é responder à pergunta do usuário de forma clara, profissional e objetiva. Baseie sua resposta estritamente no seguinte contexto extraído da documentação:\n<context>{context}</context>\nPergunta: {input}""",
        "access_level": "RAG_ONLY"
    },
    "Estrategista de Marketing": {
        "prompt": """Você é o "Marketer DiamondOne", um especialista em marketing de produto B2B para a indústria de manufatura. Sua missão é traduzir características técnicas em benefícios de negócio claros e atraentes, usando uma linguagem persuasiva e autêntica. Para estabelecer credibilidade, incorpore termos do léxico da indústria de forma natural em sua comunicação.\n<context>{context}</context>\nTarefa de Marketing: {input}""",
        "access_level": "RAG_ONLY"
    },
    "Analista de Implementação": {
        "prompt": """Você é um Analista de Implementação Sênior do DiamondOne. Sua tarefa é fornecer respostas técnicas, precisas e em formato de passo-a-passo ou lista, quando apropriado. Seja direto e foque nos detalhes técnicos da implementação, evitando linguagem de marketing ou opiniões. Baseie sua resposta estritamente no seguinte contexto extraído da documentação:\n<context>{context}</context>\nPergunta Técnica: {input}""",
        "access_level": "RAG_ONLY"
    },
    "Analista de Conhecimento (Híbrido)": {
        "prompt": """Você é um "Analista de Conhecimento" sênior. Sua tarefa é criar uma definição robusta e otimizada para um termo técnico, baseando-se em múltiplas fontes.\n**Processo de 4 Passos:**\n1.  **Análise Primária:** Leia a definição inicial fornecida no "Texto para Análise".\n2.  **Contexto Interno:** Verifique o "Contexto do Glossário Atual" para ver se o termo já existe ou se há termos relacionados.\n3.  **Pesquisa Externa:** Use os "Resultados da Busca na Web" para obter definições alternativas, contexto adicional e exemplos de uso.\n4.  **Síntese Final:** Com base em TODAS as fontes, escreva uma única e clara "Definição Otimizada". Esta definição deve ser completa, fácil de entender e estruturada para ser facilmente utilizada por um sistema de IA no futuro. Se as fontes conflitarem, use seu julgamento para criar a melhor definição possível.\n**Contexto do Glossário Atual:**\n<context>{context}</context>\n**Resultados da Busca na Web:**\n<web_search_results>{web_search_results}</web_search_results>\n**Texto para Análise:** {input}\n**Definição Otimizada:**""",
        "access_level": "HYBRID"
    }
}


# --- CONEXÃO COM O BANCO ---
@st.cache_resource
def get_db_engine():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url: st.error("FATAL: URL do Banco de Dados não encontrada."); st.stop()
    
    # Argumentos para manter a conexão ativa, essencial para DBs serverless como o Neon
    connect_args = {
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
    
    return create_engine(
        db_url, 
        pool_pre_ping=True, 
        pool_recycle=300,
        connect_args=connect_args
    )

# --- FUNÇÕES DE ESTRUTURA (TABELAS) ---
def create_tables():
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE NOT NULL, name VARCHAR(100), password VARCHAR(255) NOT NULL, role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'gerente', 'usuario')));
        """))
        connection.commit()
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS personas (id SERIAL PRIMARY KEY, nome VARCHAR(100) UNIQUE NOT NULL, prompt TEXT NOT NULL, criado_por VARCHAR(50), access_level VARCHAR(20) NOT NULL DEFAULT 'RAG_ONLY' CHECK (access_level IN ('RAG_ONLY', 'WEB_ONLY', 'HYBRID')));
        """))
        connection.commit()
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_history (id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id) ON DELETE SET NULL, persona_id INTEGER REFERENCES personas(id) ON DELETE SET NULL, session_id VARCHAR(100), question TEXT NOT NULL, answer TEXT, context TEXT, feedback SMALLINT, timestamp TIMESTAMPTZ DEFAULT NOW());
        """))
        connection.commit()
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS knowledge_sets (id SERIAL PRIMARY KEY, name VARCHAR(100) UNIQUE NOT NULL, description TEXT, created_by VARCHAR(50));
        """))
        connection.commit()
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS documents (id SERIAL PRIMARY KEY, filename VARCHAR(255) NOT NULL, set_id INTEGER REFERENCES knowledge_sets(id) ON DELETE CASCADE, indexed_at TIMESTAMPTZ DEFAULT NOW(), UNIQUE (filename, set_id));
        """))
        connection.commit()
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS persona_knowledge_links (persona_id INTEGER REFERENCES personas(id) ON DELETE CASCADE, set_id INTEGER REFERENCES knowledge_sets(id) ON DELETE CASCADE, PRIMARY KEY (persona_id, set_id));
        """))
        connection.commit()
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS persona_history (
                id SERIAL PRIMARY KEY,
                persona_id INTEGER REFERENCES personas(id) ON DELETE CASCADE,
                prompt TEXT NOT NULL,
                access_level VARCHAR(20) NOT NULL,
                changed_by VARCHAR(50),
                changed_at TIMESTAMPTZ DEFAULT NOW()
            );
        """))
        connection.commit()

# --- FUNÇÕES DE USUÁRIOS ---
def fetch_all_users(): # <-- FUNÇÃO QUE ESTAVA FALTANDO
    engine = get_db_engine()
    users = {}
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT username, name, password FROM users;"))
            for row in result:
                users[row.username] = {'name': row.name, 'password': row.password}
            return users
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")
        return {}

def create_admin_user(username, name, hashed_password): # <-- FUNÇÃO QUE ESTAVA FALTANDO
    engine = get_db_engine()
    with engine.connect() as connection:
        # Busca o ID do perfil 'admin'
        role_id_result = connection.execute(text("SELECT id FROM roles WHERE name = 'admin'")).scalar_one()
        connection.execute(text("INSERT INTO users (username, name, password, role_id) VALUES (:user, :name, :pwd, :rid);"), 
                           {"user": username, "name": name, "pwd": hashed_password, "rid": role_id_result})
        connection.commit()

def get_user_id(username):
    engine = get_db_engine()
    with engine.connect() as connection:
        return connection.execute(text("SELECT id FROM users WHERE username = :user"), {"user": username}).scalar_one_or_none()

def get_user_role(username):
    """Busca o nome do perfil (role) de um usuário."""
    engine = get_db_engine()
    with engine.connect() as connection:
        # Esta query busca o nome do perfil associado ao username
        query = text("""
            SELECT r.name 
            FROM roles r
            JOIN users u ON u.role_id = r.id
            WHERE u.username = :user;
        """)
        result = connection.execute(query, {"user": username})
        return result.scalar_one_or_none()

def get_user_role_name(username):
    engine = get_db_engine()
    with engine.connect() as connection:
        query = text("SELECT r.name FROM roles r JOIN users u ON u.role_id = r.id WHERE u.username = :user;")
        return connection.execute(query, {"user": username}).scalar_one_or_none()

@st.cache_data(ttl=60)
def fetch_all_user_details():
    engine = get_db_engine()
    with engine.connect() as connection:
        query = text("SELECT u.id, u.username, u.name, r.name as role_name FROM users u JOIN roles r ON u.role_id = r.id ORDER BY u.username;")
        return connection.execute(query).fetchall()

def create_user(username, name, password, role_name):
    engine = get_db_engine()
    with engine.connect() as connection:
        role_id_result = connection.execute(text("SELECT id FROM roles WHERE name = :name"), {"name": role_name}).scalar_one_or_none()
        if not role_id_result: raise ValueError(f"Perfil '{role_name}' não encontrado.")
        connection.execute(text("INSERT INTO users (username, name, password, role_id) VALUES (:user, :name, :pwd, :rid);"), 
                           {"user": username, "name": name, "pwd": password, "rid": role_id_result})
        connection.commit()
    st.cache_data.clear()


def update_user_role(username, new_role):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("UPDATE users SET role = :role WHERE username = :user;"), {"role": new_role, "user": username})
        connection.commit()
    st.cache_data.clear()

def update_user_password(username, new_password):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("UPDATE users SET password = :pwd WHERE username = :user;"), {"pwd": new_password, "user": username})
        connection.commit()
    st.cache_data.clear()

def delete_user(username):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users WHERE username = :user;"), {"user": username})
        connection.commit()
    st.cache_data.clear()

# --- FUNÇÕES DE PERFIS E PERMISSÕES ---
@st.cache_data(ttl=300)
def get_user_permissions(username):
    engine = get_db_engine()
    with engine.connect() as connection:
        query = text("SELECT p.name FROM permissions p JOIN role_permissions rp ON p.id = rp.permission_id JOIN users u ON rp.role_id = u.role_id WHERE u.username = :user;")
        result = connection.execute(query, {"user": username})
        return {row.name for row in result}

@st.cache_data(ttl=300)
def fetch_all_roles():
    engine = get_db_engine()
    with engine.connect() as connection:
        return connection.execute(text("SELECT id, name FROM roles ORDER BY name;")).fetchall()

@st.cache_data(ttl=300)
def fetch_all_permissions():
    engine = get_db_engine()
    with engine.connect() as connection:
        return connection.execute(text("SELECT id, name, description FROM permissions ORDER BY name;")).fetchall()

@st.cache_data(ttl=300)
def fetch_permissions_for_role(role_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT permission_id FROM role_permissions WHERE role_id = :rid;"), {"rid": role_id})
        return {row.permission_id for row in result}

def update_role_permissions(role_id, new_permission_ids):
    engine = get_db_engine()
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            connection.execute(text("DELETE FROM role_permissions WHERE role_id = :rid;"), {"rid": role_id})
            if new_permission_ids:
                params = [{"rid": role_id, "pid": pid} for pid in new_permission_ids]
                connection.execute(text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:rid, :pid);"), params)
            trans.commit()
        except Exception as e:
            trans.rollback(); raise e
    st.cache_data.clear()

@st.cache_data(ttl=600)
def fetch_personas():
    engine = get_db_engine()
    personas = {}
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, nome, prompt, access_level FROM personas ORDER BY nome;"))
        for row in result:
            personas[row.nome] = {"id": row.id, "prompt": row.prompt, "access_level": row.access_level}
    return personas

def create_persona(nome, prompt, criador, access_level):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("INSERT INTO personas (nome, prompt, criado_por, access_level) VALUES (:nome, :prompt, :criador, :level);"), {"nome": nome, "prompt": prompt, "criador": criador, "level": access_level})
        connection.commit()
    st.cache_data.clear()

def update_persona(nome, prompt, access_level, changed_by, save_history=True):
    engine = get_db_engine()
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            if save_history:
                # Busca o estado atual da persona
                current_persona = connection.execute(text("SELECT id, prompt, access_level FROM personas WHERE nome = :nome"), {"nome": nome}).first()
                if current_persona:
                    # Insere o estado atual no histórico
                    connection.execute(text("""INSERT INTO persona_history (persona_id, prompt, access_level, changed_by)
                        VALUES (:pid, :prompt, :level, :user);"""), 
                        {"pid": current_persona.id, "prompt": current_persona.prompt, "level": current_persona.access_level, "user": changed_by})
            
            # Atualiza a persona
            connection.execute(text("UPDATE personas SET prompt = :prompt, access_level = :level WHERE nome = :nome;"), {"prompt": prompt, "level": access_level, "nome": nome})
            trans.commit()
        except Exception as e:
            trans.rollback()
            raise e
    st.cache_data.clear()

def delete_persona(nome):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM personas WHERE nome = :nome;"), {"nome": nome})
        connection.commit()
    st.cache_data.clear()

def fetch_persona_history(persona_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        query = text("""SELECT prompt, access_level, changed_by, changed_at 
                    FROM persona_history 
                    WHERE persona_id = :pid 
                    ORDER BY changed_at DESC;""")
        return connection.execute(query, {"pid": persona_id}).fetchall()

def create_default_personas(criador):
    engine = get_db_engine()
    with engine.connect() as connection:
        for nome, data in PERSONAS_PADRAO.items():
            connection.execute(text("INSERT INTO personas (nome, prompt, criado_por, access_level) VALUES (:nome, :prompt, :criador, :level) ON CONFLICT (nome) DO NOTHING;"), {"nome": nome, "prompt": data['prompt'], "criador": criador, "level": data['access_level']})
        connection.commit()
    st.cache_data.clear()

# --- FUNÇÕES DE CONHECIMENTO ---
@st.cache_data(ttl=600)
def fetch_knowledge_sets():
    engine = get_db_engine()
    sets = {}
    with engine.connect() as connection:
        result = connection.execute(text("SELECT id, name, description FROM knowledge_sets ORDER BY name;"))
        for row in result:
            sets[row.name] = {"id": row.id, "description": row.description}
    return sets

def create_knowledge_set(name, description, creator):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("INSERT INTO knowledge_sets (name, description, created_by) VALUES (:name, :desc, :creator);"), {"name": name, "desc": description, "creator": creator})
        connection.commit()
    st.cache_data.clear()

def delete_knowledge_set(set_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM knowledge_sets WHERE id = :id;"), {"id": set_id})
        connection.commit()
    st.cache_data.clear()

def add_document_record(filename, set_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("INSERT INTO documents (filename, set_id) VALUES (:fname, :sid) ON CONFLICT (filename, set_id) DO NOTHING;"), {"fname": filename, "sid": set_id})
        connection.commit()
    st.cache_data.clear()

@st.cache_data(ttl=60)
def list_documents_in_set(set_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT filename FROM documents WHERE set_id = :sid ORDER BY filename;"), {"sid": set_id})
        return [row.filename for row in result]

def delete_document_record(filename, set_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM documents WHERE filename = :fname AND set_id = :sid;"), {"fname": filename, "sid": set_id})
        connection.commit()
    st.cache_data.clear()

def link_persona_to_sets(persona_id, set_ids):
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM persona_knowledge_links WHERE persona_id = :pid;"), {"pid": persona_id})
        for set_id in set_ids:
            connection.execute(text("INSERT INTO persona_knowledge_links (persona_id, set_id) VALUES (:pid, :sid);"), {"pid": persona_id, "sid": set_id})
        connection.commit()
    st.cache_data.clear()

@st.cache_data(ttl=600)
def fetch_linked_sets_for_persona(persona_id):
    engine = get_db_engine()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT set_id FROM persona_knowledge_links WHERE persona_id = :pid;"), {"pid": persona_id})
        return [row.set_id for row in result]

# --- FUNÇÕES DE HISTÓRICO E FEEDBACK ---
def log_chat_interaction(user_id, persona_id, session_id, question, answer, context):
    engine = get_db_engine()
    with engine.connect() as connection:
        context_str = "\n---\n".join([f"Fonte: {doc.metadata.get('source', 'N/A')}\n\n{doc.page_content}" for doc in context]) if context else ""
        result = connection.execute(text("INSERT INTO chat_history (user_id, persona_id, session_id, question, answer, context) VALUES (:uid, :pid, :sid, :q, :a, :c) RETURNING id;"), 
                                      { "uid": user_id, "pid": persona_id, "sid": session_id, "q": question, "a": answer, "c": context_str })
        connection.commit()
        return result.scalar_one()

# Em src/database.py, substitua a função register_feedback

def register_feedback(interaction_id, feedback_score, comment=None):
    """
    Registra o feedback e um comentário opcional para uma interação.
    """
    engine = get_db_engine()
    with engine.connect() as connection:
        connection.execute(text("""
            UPDATE chat_history 
            SET feedback = :score, feedback_comment = :comment 
            WHERE id = :interaction_id;
        """), {
            "score": feedback_score, 
            "comment": comment, 
            "interaction_id": interaction_id
        })
        connection.commit()
    st.cache_data.clear()

# Em src/database.py, substitua a função fetch_full_chat_history

@st.cache_data(ttl=300)
def fetch_full_chat_history():
    """Busca o histórico completo, agora incluindo o comentário do feedback."""
    engine = get_db_engine()
    query = text("""
        SELECT
            ch.id, ch.session_id, u.username, p.nome as persona_name,
            ch.question, ch.answer, ch.context, ch.feedback, 
            ch.feedback_comment, ch.timestamp
        FROM chat_history ch
        JOIN users u ON ch.user_id = u.id
        JOIN personas p ON ch.persona_id = p.id
        ORDER BY ch.timestamp DESC;
    """)
    try:
        with engine.connect() as connection:
            result = connection.execute(query)
            return result.fetchall()
    except Exception as e:
        st.error(f"Erro ao buscar o histórico de chat: {e}")
        return []
        
# Adicione esta função no final de src/database.py

def fetch_all_document_paths():
    """
    Busca o caminho de todos os arquivos registrados no banco.
    (Por enquanto, assumimos que os arquivos estão em uma pasta local 'temp_uploaded_files')
    """
    engine = get_db_engine()
    with engine.connect() as connection:
        # Esta query busca o nome de cada arquivo e o ID do seu conjunto
        result = connection.execute(text("SELECT filename, set_id FROM documents;"))
        # Retornamos uma lista de tuplas (caminho_do_arquivo, set_id)
        # ASSUMINDO que os arquivos estão todos na pasta 'temp_uploaded_files'
        base_path = "temp_uploaded_files"
        return [(os.path.join(base_path, row.filename), row.set_id) for row in result]
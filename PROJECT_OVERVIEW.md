# Plataforma BinahSys: Visão Geral do Projeto

## 1. Missão Principal

Criar um **sistema de entendimento** baseado em Inteligência Artificial que sirva como pilar estratégico para a empresa. A missão do BinahSys é ir além de um simples assistente, atuando em três frentes principais:

1.  **Eficiência Operacional:** Automatizar processos como a elaboração de documentos complexos (BBP, Handover, etc.) e centralizar o conhecimento de projetos, tornando o acesso à informação rápido e preciso.
2.  **Capacitação e Suporte On-Demand:** Atuar como uma plataforma de treinamento escalável, criando "Tutores Virtuais" para capacitar novos colaboradores, clientes e consultores sobre os processos e sistemas da empresa, 24/7.
3.  **Inteligência de Negócios Proativa:** Evoluir para um parceiro estratégico que analisa dados quantitativos (de ERPs, bancos de dados, etc.) para identificar tendências, gerar insights e propor otimizações que aumentem a lucratividade e a competitividade da empresa.

## 2. Módulos da Aplicação

A plataforma é construída de forma modular, com cada arquivo na pasta `pages/` representando uma funcionalidade chave:

- **`app.py` (Aplicação Principal):**
  - Gerencia o login, a autenticação e a criação do primeiro usuário administrador. Direciona o usuário para a página principal após o login.

- **`1_Chat_com_Especialista.py`:**
  - É a interface principal onde os colaboradores interagem com as Personas de IA.
  - Permite selecionar uma Persona, conversar com ela e visualizar o histórico da conversa.
  - Inclui um sistema de feedback (👍/👎) para cada resposta da IA, com a possibilidade de deixar comentários, o que é crucial para a evolução do sistema.
  - Exibe as fontes de conhecimento que a IA utilizou para gerar a resposta (em Personas do tipo RAG).

- **`2_Gerenciador_de_Personas.py`:**
  - O painel de controle para criar, editar, deletar e configurar as Personas.
  - Inclui um "Assistente de Criação" que, através de um formulário de diagnóstico, ajuda a gerar prompts complexos e eficazes para novas Personas.
  - Permite vincular "Conjuntos de Conhecimento" a uma Persona, definindo sua base de especialização.
  - Suporta 3 tipos de Persona:
    - **RAG_ONLY:** Responde usando apenas a base de conhecimento interna.
    - **WEB_ONLY:** Responde usando buscas na internet em tempo real.
    - **HYBRID:** Usa tanto a base de conhecimento quanto a busca na web.

- **`3_Gerenciador_de_Conhecimento.py`:**
  - Permite a criação de "Conjuntos de Conhecimento".
  - Os usuários autorizados podem fazer upload de documentos (`.pdf`, `.docx`, `.txt`) para esses conjuntos.
  - Os arquivos são processados e transformados em uma base de vetores (usando FAISS) que a IA utiliza para responder (processo de RAG).
  - Possui uma função crítica de "Reconstruir Base de Conhecimento" para manter os dados atualizados.

- **`4. Dashboard_de_Análise.py`:**
  - Coleta e exibe métricas de uso da plataforma.
  - Mostra KPIs como total de interações, usuários ativos, persona mais utilizada e contagem de feedbacks.
  - Apresenta gráficos sobre as perguntas mais frequentes e o engajamento dos usuários.
  - Possui uma seção dedicada para revisar as interações que receberam feedback negativo, permitindo a análise e melhoria contínua dos prompts e da base de conhecimento.

- **`5_Gerenciador_de_Usuários.py`:**
  - Página de administração para criar, editar e remover usuários da plataforma.
  - Permite associar usuários a diferentes "Perfis" de acesso.

- **`6_Gerenciador_de_Perfis.py`:**
  - Permite que o administrador do sistema defina as permissões para cada "Perfil" (ex: 'admin', 'gerente', 'usuario').
  - É possível configurar quais perfis podem gerenciar personas, ver o dashboard, gerenciar conhecimento, etc.

## 3. Pilha Tecnológica (Tecnologias Utilizadas)

- **Frontend:** Streamlit
- **IA / LLM:** LangChain, Google Generative AI, Sentence Transformers, Hugging Face
- **Banco de Vetores (Vector Store):** FAISS (para a funcionalidade de RAG)
- **Banco de Dados Relacional:** SQLAlchemy com Psycopg2 (indicando uso de PostgreSQL para armazenar usuários, perfis, personas, logs de chat, etc.)
- **Autenticação:** Bcrypt para hashing de senhas
- **Análise de Dados:** Pandas (no Dashboard)

## 4. Próximos Passos e Evolução

Esta seção pode ser usada para definir o roadmap do projeto, priorizar novas funcionalidades e registrar ideias para a evolução da plataforma.

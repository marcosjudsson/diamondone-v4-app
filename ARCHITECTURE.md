# Arquitetura do Sistema DiamondOne

Este documento descreve a arquitetura de alto nível da plataforma DiamondOne, seus principais componentes e como eles interagem.

---

## Diagrama de Componentes

O diagrama abaixo ilustra a interação entre a interface do usuário, a lógica de backend, a base de dados e as APIs externas.

```mermaid
graph TD
    subgraph "Usuário"
        U(Usuário Final)
    end

    subgraph "Interface (Streamlit)"
        UI_Login["app.py - Login"]
        UI_Chat["1_Chat.py"]
        UI_Personas["2_Gerenciador_Personas.py"]
        UI_Conhecimento["3_Gerenciador_Conhecimento.py"]
        UI_Dashboard["4_Dashboard.py"]
        UI_Usuarios["5_Gerenciador_Usuarios.py"]
        UI_Perfis["6_Gerenciador_Perfis.py"]
    end

    subgraph "Backend Logic (src/)"
        Auth["C_auth.py"]
        ChatLogic["chat_logic.py"]
        KnowledgeLogic["knowledge_logic.py"]
        DB_Module["database.py"]
    end

    subgraph "Dados & Conhecimento"
        DB["Banco de Dados (PostgreSQL)"]
        FAISS["Índice Vetorial (FAISS)"]
    end

    subgraph "APIs & Serviços Externos"
        LLM["Google Generative AI"]
        Tavily["Tavily Search"]
        GDrive["Google Drive API (Futuro)"]
    end

    U --> UI_Login
    U --> UI_Chat
    U --> UI_Personas
    U --> UI_Conhecimento

    UI_Login --> Auth
    UI_Usuarios --> Auth
    UI_Perfis --> Auth
    Auth --> DB_Module

    UI_Chat --> ChatLogic
    ChatLogic --> LLM
    ChatLogic --> Tavily
    ChatLogic --> FAISS

    UI_Conhecimento --> KnowledgeLogic
    KnowledgeLogic --> FAISS
    KnowledgeLogic --> GDrive

    DB_Module --> DB
```

## Descrição dos Componentes

- **Interface (Streamlit):** É a camada de apresentação com a qual o usuário interage. Cada página é um módulo distinto que lida com uma funcionalidade específica (gerenciar personas, conversar com a IA, etc.).

- **Backend Logic (src/):** Contém a lógica de negócio da aplicação. Separa as responsabilidades, como autenticação, lógica do chat e gerenciamento da base de conhecimento.

- **Dados & Conhecimento:**
    - **PostgreSQL:** Armazena dados estruturados como usuários, perfis, personas, logs de conversas e metadados de documentos.
    - **FAISS:** Um índice vetorial local que armazena os "embeddings" dos documentos para permitir buscas semânticas rápidas (a base do RAG).

- **APIs & Serviços Externos:**
    - **Google Generative AI:** O serviço de LLM que provê a inteligência para gerar respostas.
    - **Tavily Search API:** Utilizada pelas personas do tipo "WEB_ONLY" e "HYBRID" para realizar buscas na internet em tempo real.
    - **Google Drive API:** Planejado para futuras implementações, permitirá a sincronização automática de documentos.

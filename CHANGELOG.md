# Changelog - BinahSys

## 30 de outubro de 2025

### Atividades do Dia

- **Correção de Bugs e Depreciações:**
    - Corrigido um `IndentationError` crítico na página "Gerenciador de Conhecimento" que impedia sua execução.
    - Resolvidos múltiplos `ModuleNotFoundError` e `ImportError` relacionados à atualização da biblioteca `langchain` para a v1.0. Este foi um processo complexo que envolveu:
        - Reinstalação completa dos pacotes `langchain`.
        - Adição das novas dependências `langchain-classic` e `langchain-text-splitters`.
        - Mapeamento e correção dos novos caminhos de importação para as funções de `chains` e `text_splitter`.
    - Corrigido o aviso de depreciação da ferramenta `TavilySearchResults`, substituindo-a pela nova implementação do pacote `langchain-tavily`.
    - Resolvido o aviso de `USER_AGENT` não definido ao adicionar um cabeçalho de identificação nas requisições feitas pelo `WebBaseLoader`.

- **Testes e Validação:**
    - Executados os testes automatizados com `pytest`, que passaram com sucesso, validando a estabilidade do sistema após as correções.

- **Planejamento e Documentação:**
    - Discutida a implementação de uma memória de longo prazo para o agente, permitindo sua evolução contínua.
    - Adicionada a **Fase 4: Memória e Evolução do Agente** ao `ROADMAP.md` para refletir essa nova visão de futuro.
    - Criado este `CHANGELOG.md` para registrar o progresso diário do projeto.

### Atividades da Tarde (Continuação)

- **Correção de Bug Crítico:**
    - Corrigido um `sqlalchemy.exc.IntegrityError` que impedia a exclusão de personas. A função `delete_persona` foi refatorada para remover todos os vínculos de uma persona (com bases de conhecimento, histórico, etc.) antes de deletar a persona em si, garantindo a integridade do banco de dados.

- **Implantação e Pós-Deploy:**
    - Realizado o primeiro deploy da aplicação no Streamlit Community Cloud.
    - O código foi versionado com Git e enviado para um repositório público no GitHub.
    - Diagnosticado e resolvido o erro `FATAL: URL do Banco de Dados não encontrada` na aplicação publicada, instruindo sobre a configuração correta dos "Secrets" no painel do Streamlit.
    - **Alerta Crítico de Segurança:** Identificada a exposição de chaves de API e credenciais de banco de dados. O usuário foi imediatamente alertado sobre o risco e instruído a revogar e substituir todas as chaves expostas.
    - Resolvido o erro `Base de conhecimento não criada`, explicando a necessidade de recriar os conjuntos de conhecimento e fazer o upload dos documentos na plataforma online, já que o índice FAISS e os arquivos não são enviados pelo Git.

- **Esclarecimentos e Planejamento de Evolução:**
    - Esclarecido o funcionamento do botão "Reconstruir Base de Conhecimento" e o fluxo correto para adicionar novos documentos na aplicação publicada.
    - Discutido e validado o funcionamento flexível das personas, que podem operar com base de conhecimento, busca na web ou de forma híbrida.
    - Registradas novas e importantes funcionalidades no `ROADMAP.md`, detalhando os objetivos e os detalhes de implementação para cada uma:
        - Adicionada à Fase 3: "Página de Perfil e Alteração de Senha pelo Usuário".
        - Adicionada à Fase 3: "Página de Chat Simplificada e Compartilhável por Persona".
        - Adicionada à Fase 4: "Sincronização Automática de Documentos do Google Drive".
    - Esclarecido o funcionamento do Git, GitHub e o significado do botão "Compare & pull request".
    - Detalhada a dinâmica de interação entre o usuário e a IA (Gemini), explicando como os comandos são executados no ambiente local e as limitações de acesso ao ambiente de nuvem.

- **Feedback da Apresentação e Estratégia de Tangibilização:**
    - Recebido feedback do diretor técnico sobre a necessidade de demonstrar resultados, ganhos e valor tangíveis do BinahSys.
    - A falha na demonstração ao vivo (devido à base de conhecimento não configurada) gerou a impressão de foco excessivo na visão e pouca entrega de valor imediato.
    - Definida a estratégia "Operação Tese": focar na construção de um caso de uso de alto impacto e baixa complexidade para demonstrar o valor do BinahSys de forma inquestionável.
    - O plano inclui: escolher um caso de uso (ex: Capacitação/Onboarding), construir uma "Persona-Tutor" dedicada e preparar uma demonstração "Uau" com métricas de valor claras.

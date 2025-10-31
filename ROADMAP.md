# Roadmap de Evolução da Plataforma BinahSys

Este documento descreve o plano de desenvolvimento e a sequência de implementação de novas funcionalidades para a plataforma.

---

### **Fase 1: Fundamentos e Usabilidade (Curto Prazo)**
*O objetivo aqui é gerar valor imediato e melhorar a experiência do dia a dia com baixo esforço de desenvolvimento.*

1.  **Botões "Copiar Resposta" e "Limpar Histórico":** Implementar botões na interface de chat para copiar o conteúdo gerado pela IA e para limpar o histórico da conversa atual.
2.  **Modo Escuro (Dark Mode):** Oferecer uma opção para alternar o tema da interface, melhorando o conforto visual.

---

### **Fase 2: Robustez e Expansão do Núcleo (Médio Prazo)**
*O foco é tornar o sistema mais seguro para experimentação e mais poderoso em suas funções principais, preparando o terreno para o futuro.*

1.  **Criação de Testes Automatizados:** Introduzir um framework como `pytest` para criar uma rede de segurança que garanta a estabilidade do projeto conforme ele cresce.
2.  **Versionamento de Prompts:** No "Gerenciador de Personas", criar um histórico de alterações nos prompts para permitir reversões, incentivando a experimentação segura.
3.  **Upload de Documentos Temporários no Chat:** Permitir o upload de arquivos diretamente na tela de chat para análise e discussão em uma sessão específica, sem adicioná-los à base de conhecimento global.
4.  **Suporte a URLs no Gerenciador de Conhecimento:** Expandir a capacidade de RAG para que a IA possa aprender a partir de links da web, além de arquivos.

---

### **Fase 3: Implementação da Visão Estratégica (Longo Prazo)**
*Com a base sólida e robusta, partimos para as funcionalidades que transformarão o modo de trabalho.*

1.  **Verificação de Existência de Arquivos no Gerenciador de Conhecimento:** Adicionar uma verificação para garantir que os arquivos registrados no banco de dados realmente existam no disco, exibindo um aviso caso estejam ausentes.
2.  **Resumo de Conversas:** Adicionar uma funcionalidade de IA para gerar resumos de conversas longas no chat.
3.  **Criação e Exportação de Documentos:** Implementar um fluxo onde o usuário pode pegar uma resposta da IA, ajustá-la em um editor e exportá-la como um documento formal (`.docx`, `.pdf`).
4.  **Módulo de Treinamento Interativo:** Criar uma nova página dedicada onde uma persona atua como um tutor para processos ou ferramentas internas.
5.  **Página de Perfil e Alteração de Senha pelo Usuário:**
    -   **Objetivo:** Aumentar a segurança e a autonomia do usuário.
    -   **Detalhes:** Criar uma nova página "Meu Perfil", acessível pelo usuário logado, onde ele possa alterar sua própria senha. A página exigirá que o usuário digite a senha atual e a nova senha duas vezes para confirmação.
6.  **Página de Chat Simplificada e Compartilhável por Persona:**
    -   **Objetivo:** Facilitar o acesso de equipes de projeto a personas específicas, sem a complexidade da interface de gerenciamento.
    -   **Detalhes:** No "Gerenciador de Personas", adicionar um botão "Compartilhar" que gera uma URL única para cada persona. Essa URL levará a uma página de chat limpa, pré-carregada com a persona selecionada, focada apenas na conversação, e com as ferramentas de exportação de documentos.
7.  **Workflows de Agentes (Agent Chaining):** A funcionalidade mais avançada, permitindo a criação de fluxos de trabalho que executam tarefas em sequência, utilizando múltiplas personas para automatizar processos complexos de ponta a ponta.

---

### **Fase 4: Memória e Evolução do Agente (Visão de Futuro)**
*O objetivo é dotar o agente de uma memória persistente e capacidade de aprendizado contínuo a partir das interações.*

1.  **Implementação de Memória de Longo Prazo:** Desenvolver um sistema onde o agente extrai, estrutura e armazena conhecimentos de cada conversa para utilizá-los em interações futuras, permitindo sua evolução e amadurecimento contínuo.
2.  **Sincronização Automática de Documentos do Google Drive:**
    -   **Objetivo:** Manter a base de conhecimento das personas constantemente atualizada com o mínimo de intervenção manual.
    -   **Detalhes:** Implementar uma integração com a API do Google Drive. O administrador poderá vincular um "Conjunto de Conhecimento" a uma pasta específica do Google Drive. Um processo automatizado (rodando em background) irá periodicamente verificar a pasta por arquivos novos ou modificados, baixá-los e adicioná-los automaticamente à base de vetores da persona correspondente.

---

### **Fase 5: IA Proativa e Análise de Negócios (Visão de Futuro Avançada)**
*O objetivo aqui é transformar o BinahSys de um sistema de conhecimento em um parceiro estratégico proativo, capaz de analisar dados quantitativos e gerar insights para otimização de negócios.*

1.  **Integração com Fontes de Dados Quantitativos:**
    -   **Objetivo:** Permitir que a IA acesse dados de performance, financeiros e operacionais.
    -   **Detalhes:** Desenvolver conectores para bancos de dados (ERPs, MES), planilhas (Excel, Google Sheets) e APIs de sistemas internos.

2.  **Desenvolvimento de Personas Analíticas:**
    -   **Objetivo:** Criar agentes capazes de analisar dados, identificar tendências e gerar hipóteses.
    -   **Detalhes:** Equipar as personas com ferramentas de análise de dados, como a capacidade de executar scripts Python em um ambiente seguro (Code Interpreter) para realizar cálculos estatísticos e gerar visualizações.

3.  **Implementação de Relatórios Autônomos e Alertas Inteligentes:**
    -   **Objetivo:** Fazer com que a IA trabalhe de forma autônoma para o negócio.
    -   **Detalhes:** Configurar rotinas onde a IA gera e envia relatórios de performance semanais, e monitora dados em tempo real para enviar alertas inteligentes sobre anomalias ou oportunidades de otimização.

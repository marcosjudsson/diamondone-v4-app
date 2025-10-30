# Roadmap de Evolução da Plataforma DiamondOne

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

1.  **Resumo de Conversas:** Adicionar uma funcionalidade de IA para gerar resumos de conversas longas no chat.
2.  **Criação e Exportação de Documentos:** Implementar um fluxo onde o usuário pode pegar uma resposta da IA, ajustá-la em um editor e exportá-la como um documento formal (`.docx`, `.pdf`).
3.  **Módulo de Treinamento Interativo:** Criar uma nova página dedicada onde uma persona atua como um tutor para processos ou ferramentas internas.
4.  **Workflows de Agentes (Agent Chaining):** A funcionalidade mais avançada, permitindo a criação de fluxos de trabalho que executam tarefas em sequência, utilizando múltiplas personas para automatizar processos complexos de ponta a ponta.

---

### **Fase 4: Memória e Evolução do Agente (Visão de Futuro)**
*O objetivo é dotar o agente de uma memória persistente e capacidade de aprendizado contínuo a partir das interações.*

1.  **Implementação de Memória de Longo Prazo:** Desenvolver um sistema onde o agente extrai, estrutura e armazena conhecimentos de cada conversa para utilizá-los em interações futuras, permitindo sua evolução e amadurecimento contínuo.

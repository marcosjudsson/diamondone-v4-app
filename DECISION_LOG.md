# Registro de Decisões de Arquitetura (ADR)

Este documento registra as decisões de arquitetura importantes tomadas durante o desenvolvimento do projeto DiamondOne.

---

## ADR-001: Criação de Documentação Estruturada

*   **Data:** 30 de outubro de 2025
*   **Status:** Decidido

### Contexto

Durante a fase inicial de desenvolvimento e implantação, percebemos a necessidade de uma estrutura de documentação mais robusta para garantir a consistência, o alinhamento e a capacidade de evolução do projeto a longo prazo. A natureza volátil da memória da IA entre as sessões de trabalho exige um "cérebro persistente" para o projeto.

### Decisão

Decidimos criar e manter os seguintes documentos como a "única fonte da verdade" do projeto:
*   **`ARCHITECTURE.md`:** Para documentar a arquitetura do sistema de forma visual e descritiva.
*   **`DECISION_LOG.md`:** Para registrar o "porquê" por trás das nossas decisões técnicas.
*   **`CHANGELOG.md`:** Para manter um diário de bordo detalhado das atividades.
*   **`ROADMAP.md`:** Para o planejamento estratégico de alto nível.

Também foi decidido adotar um fluxo de trabalho baseado em sessões (início e fim) para garantir que esses documentos sejam sempre consultados e atualizados, e integrar o Obsidian como a ferramenta principal para visualização e gerenciamento dessa base de conhecimento.

### Consequências

*   **Positivas:**
    *   Maior clareza e alinhamento sobre o estado e a direção do projeto.
    *   Cria uma base de conhecimento persistente que acelera a retomada do trabalho entre sessões.
    *   Facilita a manutenção e a evolução do sistema a longo prazo.
    *   Atende à preferência do usuário por uma abordagem visual e estruturada.
*   **Negativas:**
    *   Exige uma disciplina maior para manter os documentos atualizados ao final de cada sessão de trabalho.

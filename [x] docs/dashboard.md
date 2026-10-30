# **DOSSIÊ TÉCNICO DE ENGENHARIA DE FRONT-END**

## **PROJETO INTEGRADOR: SISTEMA INTELIGENTE DE MONITORAMENTO DE DATA CENTER**

**Instituição:** Faculdade Anhanguera  
**Disciplinas Integradas:** Arquitetura de Computadores • Sistemas Distribuídos • Engenharia de Software  
**Docente Orientador:** Prof. Marcio João  
**Escopo:** Interface de Monitoramento Analítico do Data Center (Front-end)

## **1\. SUMÁRIO EXECUTIVO E OBJETIVOS DO SISTEMA**

Este documento constitui a documentação técnica definitiva de engenharia de Front-end do Dashboard de Monitoramento Analítico de Data Center. O propósito central deste projeto foi projetar, arquitetar e homologar uma interface web de alta performance voltada ao acompanhamento operacional, visualização de métricas críticas e emissão de alertas em tempo real para infraestruturas computacionais distribuídas.  
A solução foi desenvolvida de forma desacoplada (decoupled) das camadas de Back-end e Banco de Dados nesta primeira etapa, garantindo total autonomia técnica no processo de validação de usabilidade, na estabilidade do Document Object Model (DOM) e na eficiência da renderização gráfica via cliente. Esta documentação consolida exclusivamente a especificação dos componentes web, a fundamentação ergonômica da interface, os critérios de adoção de Inteligência Artificial Generativa nas frentes do projeto, a governança ágil da equipe e o protocolo completo de Quality Assurance (QA).

## **2\. STACK TECNOLÓGICA E ECOSSISTEMA WEB**

A arquitetura do Front-end foi estruturada rigorosamente sob os padrões abertos da Web (W3C), garantindo modularidade, legibilidade do código, facilidade de manutenção e compatibilidade cross-browser.

### **2.1 Descrição Textual da Arquitetura em Camadas**

A camada de apresentação do sistema organiza-se hierarquicamente da seguinte forma:

> * **Base de Estruturação e Estilização (HTML5, CSS3 e Bootstrap 5):** O HTML5 Semântico fornece a estrutura fundamental do DOM e marcações de acessibilidade ARIA. O CSS3 customizado gerencia a identidade visual baseada em tons pastéis. O framework Bootstrap 5 provê o sistema de grid flexível para alinhamento responsivo.  
> * **Camada de Lógica e Processamento no Cliente (JavaScript ES6+):** O JavaScript atua como o intermediário central, realizando a manipulação dinâmica do DOM, o gerenciamento de eventos da interface e o processamento dos dados recebidos via arquivos JSON estáticos (mock datasets).  
> * **Camada de Visualização Analítica (Chart.js Engine):** No nível de renderização gráfica, o motor da biblioteca Chart.js consome os dados processados pelo JavaScript e desenha as métricas operacionais diretamente no elemento HTML5 \<canvas\>.

### **2.2 Detalhamento dos Componentes Tecnológicos**

> 1. **HTML5 (W3C Standard):**  
   * Função: Estruturação semântica da página.  
   * Aplicação: Emprego de tags estruturais (\<main\>, \<section\>, \<header\>, \<article\>, \<nav\>)   e do elemento nativo \<canvas\> para ancorar as instâncias gráficas. Adoção de atributos WAI-ARIA para assegurar parâmetros fundamentais de acessibilidade.  
> 2. **CSS3 (Cascading Style Sheets \- Level 3):**  
   * Função: Estilização visual, identidade de marca e ergonomia da interface.  
   * Aplicação: Utilização de CSS Custom Properties (variáveis globais) para gerenciamento da paleta cromática em tons pastéis, controle do modelo de caixas (box-sizing: border-box), animações de transição (transition, transform) e sobrescrita limpa dos estilos padrão do framework.  
> 3. **JavaScript (ECMAScript 2022 / ES6+):**  
   * Função: Programação da lógica de negócios no lado do cliente (Client-Side Logic).  
   * Aplicação: Manipulação assíncrona do DOM, gerenciadores de eventos (event listeners), processamento de payloads JSON estáticos (mock datasets) e encapsulamento em módulos para evitar a poluição do escopo global.  
> 4. **Bootstrap 5 (Framework CSS & Grid System):**  
   * Função: Diagramação responsiva e alinhamento de componentes.  
   * Aplicação: Organização da tela através do sistema de Grid Layout flexível de 12 colunas, combinado com seletores utilitários de espaçamento (gap, margin, padding) e pontos de quebra (col-xl-\*, col-lg-\*, col-md-\*) para garantir o alinhamento das métricas em monitores Desktop.  
> 5. **Chart.js (HTML5 Canvas Engine):**  
   * Função: Motor gráfico para visualização analítica de dados.  
   * Aplicação: Renderização de gráficos de linhas (tendências de CPU e RAM), barras (tráfego de rede) e rosca (alocação de armazenamento e status de servidores). Configuração de tooltips informativos e ciclos de atualização dinâmica.

## **3\. ENGENHARIA DE UX/UI, ERGONOMIA COGNITIVA E DESIGN SYSTEM**

A interface foi reformulada para superar gargalos de usabilidade observados nos primeiros esboços do sistema.

### **3.1 Transição para Layout Horizontal Contínuo**

> * **Problema Encontrado:** O esboço inicial previa menus no formato accordion e navegação fragmentada por abas verticais escondidas. Esse formato exigia múltiplos cliques do operador para alternar entre relatórios, elevando a carga cognitiva (cognitive load) e dificultando a correlação de métricas em tempo real.  
> * **Solução Adotada:** Unificação do painel em um Layout de Fluxo Contínuo Horizontal. Todos os indicadores estratégicos (KPIs de status, gráficos de utilização e alertas) foram dispostos em um painel panorâmico com rolagem fluida.  
> * **Ganho Operacional:** Visibilidade contínua do estado geral do Data Center, eliminação de trocas desnecessárias de tela e tomada de decisão mais rápida durante incidentes.

### **3.2 Design System e Prevenção da Astenopia Ocupacional**

> * **Problema Encontrado:** Interfaces de monitoramento com alto contraste ou cores saturadas causam fadiga visual rápida em operadores que trabalham por longos períodos em salas de controle (NOC).  
> * **Solução Adotada:** Implementação de um Design System fundamentado em Tons Pastéis de Baixa Saturação.  
> * **Fundamentação Ergonômica:** As tonalidades pastéis suavizam a luminância emitida pelo monitor, prevenindo o estresse ocular e a astenopia ocupacional (cansaço visual prolongado), sem perder o contraste necessário para a identificação de alertas.

## **4\. DECLARAÇÃO DO USO DE INTELIGÊNCIA ARTIFICIAL GENERATIVA**

Em conformidade com as Regras Globais do Projeto Integrador (especificamente as seções 22 e 23 da diretriz acadêmica), declara-se formalmente o uso de ferramentas de Inteligência Artificial Generativa como apoio ao processo de desenvolvimento técnico, conceituação e documentação. A IA atuou como aceleradora de processos, sendo todo o resultado revisado e validado pela equipe humana.

### **4.1 Descrição do Ciclo de Governança e Validação (Human-in-the-Loop)**

O fluxo de utilização de Inteligência Artificial seguiu quatro etapas estritas de controle:

> 1. **Definição do Prompt ou Demanda:** Formulação clara da necessidade técnica pela equipe (ex.: configuração de eixos no Chart.js, estrutura de documentação ou cenários de teste).  
> 2. **Geração Assistida via IA:** Produção do rascunho inicial do código JavaScript, trecho de estilização ou minuta de texto pela ferramenta de IA.  
> 3. **Revisão e Validação Humana (Peer Code Review / QA):** Submissão do código ou texto gerado à análise criteriosa dos integrantes do time, verificando segurança, coerência semântica e desempenho.  
> 4. **Homologação e Incorporação:** Inclusão formal do artefato validado na base do projeto somente após aprovação da equipe.

### **4.2 Aplicação Detalhada por Frente de Trabalho**

> * **A. Programação e Configuração do Chart.js:**  
  * Ajuste Matemático de Eixos e Ticks: Acelerou a construção de algoritmos de escalonamento dinâmico , garantindo a exibição adequada das métricas de porcentagem de uso de CPU e memória RAM.  
  * Gradientes em Elementos Canvas: Auxiliou na implementação de funções em JavaScript para aplicar gradientes de preenchimento suave nas áreas sob os gráficos de linha.  
  * Geração de Datasets de Teste (Mock Data): Utilizada na criação das estruturas em formato JSON que simulam payloads recebidos de servidores monitorados (ex.: porcentagens de consumo, status de conexões e registros de logs).  
> * **B. Design e Conceituação de UX/UI:**  
  * Esboço Inicial e Wireframing: A IA auxiliou a equipe de UX/UI no levantamento de referências de organização visual, sugerindo componentes para manter métricas críticas acessíveis em uma única visualização panorâmica.  
  * Definição de Paleta Cromática: Apoiou o mapeamento dos códigos hexadecimais em tons pastéis, garantindo contraste suficiente para indicar estados normais (verde pastel), de atenção (amarelo pastel) e críticos (vermelho suave).  
> * **C. Documentação Técnica e Revisão do Texto:**  
  * Refinamento da Escrita: A IA ajudou a estruturar os tópicos da documentação técnica, sugerindo termos de engenharia e eliminando redundâncias.  
  * Verificação de Coerência: Auxiliou no cruzamento de dados entre os requisitos das disciplinas e o escopo entregue pela equipe.  
> * **D. Quality Assurance (QA) e Testes:**  
  * Cenários de Teste: Utilizada para mapear cenários de teste estático e casos de borda relacionados ao comportamento da interface em diferentes resoluções.

### **4.3 Governança e Revisão Humana**

Nenhum código ou texto gerado por Inteligência Artificial foi incorporado ao projeto de forma automatizada. Todo o material produzido passou por Revisão por Pares (Peer Code Review) e validações no navegador para garantir segurança, ausência de redundâncias e aderência total aos objetivos pedagógicos da disciplina.

## **5\. ESTRUTURA E GOVERNANÇA DA SQUAD**

A condução do projeto seguiu um modelo híbrido baseado em Scrum e Kanban, organizado em ciclos curtos de desenvolvimento (Sprints) para garantir acompanhamento contínuo e transparência nas entregas.

### **5.1 Organização da Equipe por Frentes de Atuação**

> 1. **UX (Experiência do Usuário):** Responsáveis por estudos de experiência, usabilidade, fluxos de navegação e interface. (Integrantes: Thiago, Ismael, Nicolly)  
> 2. **Desenvolvimento:** Responsáveis pela implementação, manutenção e evolução das funcionalidades do projeto. (Integrantes: Gabriel, Adrian, Givanilton, Arthur, Pedro)  
> 3. **QA (Quality Assurance):** Responsáveis pelos testes, validação de funcionalidades, homologação e garantia da qualidade das entregas. (Integrantes: Cleber, Gabriel Putov)  
> 4. **Documentação:** Responsáveis pela elaboração, atualização e manutenção da documentação técnica e funcional do projeto. (Integrantes: Kauã, Adrian)

### **5.2 Matriz de Responsabilidades da Squad**

| Frente de Atuação | Descrição da Responsabilidade | Integrantes do Time   |
| :---- | :---- | :---- |
| **UX (User Experience)** | Estudos de experiência, usabilidade, fluxos de navegação e interface. | Thiago, Ismael, Nicolly |
| **Desenvolvimento** | Implementação, manutenção e evolução das funcionalidades do projeto. | Gabriel, Givanilton, Arthur, Pedro, Adrian |
| **QA (Quality Assurance)** | Testes, validação de funcionalidades, homologação e garantia da qualidade das entregas. | Cleber, Gabriel Putov |
| **Documentação** | Elaboração, atualização e manutenção da documentação técnica e funcional do projeto. | Kauã, Adrian |

## **6\. QUALITY ASSURANCE (QA) E MATRIZ DE TESTES**

A homologação da interface do Front-end foi realizada em ambiente isolado, consumindo dados estáticos via payloads JSON para validar o comportamento da tela sem dependências do Back-end.

### **6.1 Matriz de Testes Estáticos e Comportamentais**

| ID | Caso de Teste | Requisito Avaliado | Resultado Esperado | Status   |
| :---- | :---- | :---- | :---- | :---- |
| T1 | Responsividade até 1024px | Ajuste do Grid Bootstrap | Reorganização automática dos cards de métricas em telas de até 1024px, mantendo a leitura clara. | Aprovado |
| T2 | Renderização dos Gráficos via Canvas | Inicialização do Chart.js | Exibição correta dos gráficos de consumo de CPU, RAM e tráfego de rede sem distorções visuais. | Aprovado |
| T3 | Consumo de Payloads JSON | Leitura de Mock Data | Leitura dos arquivos JSON estáticos e conversão dos dados nos componentes visuais do dashboard. | Aprovado |
| T4 | Ergonomia e Layout Horizontal | Usabilidade do Painel | Rolagem horizontal limpa e acesso visual contínuo aos KPIs primários do Data Center. | Aprovado |
| T5 | Gestão de Memória no Canvas | Ciclo de Vida do Chart.js | Destruição e recriação adequada das instâncias gráficas ao atualizar dados, evitando vazamentos de memória (memory leaks). | Aprovado |
| T6 | Compatibilidade de Resolução Desktop | Exibição em HD e Full HD | Manutenção do alinhamento geométrico nas resoluções 1280x720 e 1920x1080 sem quebra de elementos. | Aprovado |

### **6.2 Detalhes dos Achados de QA**

> * **Isolamento de Erros:** O uso de dados simulados em JSON permitiu identificar e corrigir falhas exclusivamente na camada visual (CSS/JS) antes de iniciar a integração com APIs.  
> * **Desempenho no Canvas:** A gestão correta dos métodos .destroy() e .update() do Chart.js garantiu estabilidade na taxa de quadros da página durante interações no navegador.

## **7\. CONSIDERAÇÕES FINAIS**

A entrega da camada de Front-end cumpriu rigorosamente os objetivos propostos para esta etapa do Projeto Integrador da Faculdade Anhanguera. A solução unificou os conceitos teóricos de Engenharia de Software (organização de requisitos, gestão ágil e testes), Arquitetura de Computadores e Sistemas Distribuídos na interface de visualização. Com o Front-end totalmente homologado, o sistema encontra-se preparado para a próxima fase de integração com as APIs de Back-end e Banco de Dados.

* 

---


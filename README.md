# 🖥️ Sistema Inteligente de Monitoramento de Data Center

> Projeto Integrador - 2026 | Anhanguera
> Sistema distribuído para monitoramento, coleta, processamento, armazenamento e apresentação de métricas de uma infraestrutura de Data Center.

## 📋 1. Sobre o Projeto
Este projeto tem como objetivo identificar falhas, indisponibilidades e situações que possam comprometer o desempenho dos recursos computacionais de um Data Center. O sistema coleta dados dos servidores (CPU, Memória, Disco e Rede), processa essas métricas via API e exibe alertas em um Dashboard em tempo real. 

*Regras de Negócio Oficiais:*
* ⚠️ *ALERTA:* Disparado caso o uso de CPU, Memória ou Disco ultrapasse *85%*.
* 🔴 *OFFLINE (CRÍTICO):* Disparado se um servidor ficar mais de *2 minutos* sem enviar dados (falha de comunicação).

## 🛠️ 2. Arquitetura e Tecnologias
O sistema segue uma arquitetura distribuída e modular:
* *Infraestrutura e Virtualização:* Oracle VirtualBox / VMware (Rede Host-Only: 192.168.56.x)
* *Sistema Operacional:* Ubuntu Server 22.04 LTS
* *Agentes de Coleta (G1/G2):* Python (psutil, requests) via systemd/cron
* *Backend e API (G3):* Python com framework Flask
* *Banco de Dados:* MySQL / SQLite
* *Frontend / Dashboard (G4):* HTML, CSS, JavaScript (Bootstrap e Chart.js)

## 📁 3. Estrutura do Repositório
A organização das pastas reflete a separação de responsabilidades das equipes:

- /agente - Scripts Python de coleta de dados locais nos servidores.
- /backend - Código da API em Flask para recebimento e processamento.
- /dashboard - Arquivos de interface gráfica (HTML, CSS, JS).
- /banco - Scripts de modelagem e criação do banco de dados.
- /docs - Documentação oficial, diagramas UML e manuais.
- /testes - Roteiros de testes de integração e simulação de falhas.

## 🚀 4. Como Executar o Projeto
Atenção: Consulte a pasta /docs para o Manual de Instalação completo.

*Passos básicos:*
1. Configure as VMs no VirtualBox utilizando Ubuntu Server 22.04 e defina a rede como Host-Only.
2. Clone o repositório:
   ```bash
   git clone [https://github.com/SEU-USUARIO/monitoramento-data-center.git](https://github.com/SEU-USUARIO/monitoramento-data-center.git)

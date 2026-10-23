# Registro de alterações — Grupo 3 (API, backend e banco)

**Base:** `datacenter-monitoring-backend-ssh-4-vms.zip` (versão anterior).
**Referência:** *Guia Prático de Implementação — Máquinas Virtuais*, professor
Marcio João, páginas 1, 4–6 e 8–9.

## Alterações feitas, arquivo a arquivo

| Arquivo | Alteração | Motivo |
| --- | --- | --- |
| `app.py` | Registra nova rota de eventos; inicia API na porta **80** sem debug padrão | Centralizar endpoints; porta 80 solicitada (guia usa 5000) |
| `config.py` | Acrescenta parâmetros de disponibilidade, desliga debug, melhora URI do MySQL e falha em configuração incompleta | Evitar SQLite acidental, proteger configurações |
| `services/monitoring_service.py` | Valida JSON e percentuais, grava `last_check` quando recebe POST válido, atualiza histórico/alertas, resolve disponibilidade e registra recuperação | Separar horário de coleta do horário de recebimento; restaurar ONLINE |
| `services/alert_service.py` | Mantém limites 85%, impede duplicatas, adiciona `AVAILABILITY`/`CRITICAL` e resolução na volta | Detectar quedas além de consumo de recursos |
| **`services/availability_service.py`** | **Novo:** identifica servidores sem leitura válida após 120 segundos, registra OFFLINE/evento/alerta | Exigência explícita do guia |
| **`availability_worker.py`** | **Novo:** tarefa periódica independente que executa o serviço a cada 15 segundos | Identificar ausência sem depender de nova requisição |
| `routes/monitoring.py` | Mantém `/monitoramento`; valida objeto JSON e adiciona limite de consulta ao histórico | Contrato do agente + consultas eficientes |
| `routes/servers.py` | Adiciona `/resumo` e `/summary`, preserva lista/detalhe | Indicadores do dashboard |
| `routes/alerts.py` | Filtra tipos de status; impede resolver indisponibilidade com VM OFFLINE | Evitar ocultar falhas |
| **`routes/events.py`** | **Novo:** `GET /eventos`/`/events` para visualizar quedas e recuperações | Expor histórico para integração |
| `collector.py` | Modo SSH passa a considerar **três** VMs, não quatro; SSH opcional; falha SSH vira somente evento de diagnóstico | A `.20` é VM central; SSH falho não significa VM desligada |
| `.env.example` | Diferencia IPs monitorados `.11–.13` do central `.20`; documenta timeouts, MySQL e SSH opcional | Configuração alinhada ao guia |
| `requirements.txt` | Mantém dependências somente da API; Paramiko opcional em `requirements-ssh.txt` | O agente HTTP não precisa de SSH |
| `requirements-ssh.txt` | **Novo:** dependências do modo opcional SSH | Instalação separada |
| `sql/alerts.sql` | ENUM do MySQL aceita `AVAILABILITY` | Persistência do alerta crítico |
| **`sql/migrations/001_availability_alert.sql`** | **Novo:** `ALTER TABLE` para bancos MySQL antigos | `create_all()` não migra ENUM existente |
| `sql/indexes.sql` | Índices por servidor, timestamp, status e tipo | Facilitar consulta do histórico |
| `.gitignore` | Ignora `venv`, `.env`, chaves, cache e SQLite local | Evitar publicar configurações e artefatos locais |
| `README.md` | Reescrito em português com arquitetura real, IPs, rotas, execução, testes e limites | Servir como documento de entrega e integração |
| `SSH_SETUP.md` | Atualizado para explicar que SSH é opcional e não deve duplicar HTTP | Preservar implementação anterior sem conflitar com o professor |
| **`tests/test_api.py`** | **Novo:** testes de HTTP + banco em memória, alertas, offline e recuperação | Evidenciar entrega do Grupo 3 |
| `tests/test_ssh_parsers.py` | Preservado | Assegurar que parsers opcionais continuam testáveis |

Modelos `Server`, `Metric`, `Alert`, `Service`, `Event` e scripts SQL de servidores,
métricas, eventos, serviços e banco foram preservados em suas estruturas
principais. O modelo ORM usa `String` para o tipo de alerta; o SQL MySQL usa
`ENUM`, por isso requer a migração se o banco já foi criado antes.

## Fluxo atual: backend/API/banco

### Fluxo A — novo dado de CPU, RAM e disco

1. Agente do **Grupo 2**, executando em `.11`, `.12` ou `.13`, lê recursos
   com `psutil`, organiza JSON e envia a `http://192.168.56.20/monitoramento`.
2. **`app.py`** recebe o HTTP no Flask; `routes/monitoring.py` verifica se
   o corpo é um objeto JSON.
3. **`monitoring_service.process_monitoring()`** valida servidor/IP e
   percentuais 0–100. Aceita nomes de campos em português e inglês.
4. Procura `Server` pelo IP (identidade fixa). Se não existe, cadastra.
   Se existe, atualiza seu nome/SO, status ONLINE e **last_check=agora UTC**.
5. Cria `Metric` com CPU, RAM, disco, rede (se enviada) e timestamp.
6. **`alert_service.sync_metric_alerts()`** verifica 85% e cria ou resolve
   alertas de CPU/MEMORY/DISK sem duplicar ativos.
7. Caso o servidor estivesse OFFLINE, cria `Event` de recuperação e resolve
   alertas ativos de indisponibilidade.
8. `db.session.commit()` confirma as alterações em uma transação. O Flask
   retorna HTTP **201** com `server_id` e contadores de alertas.

### Fluxo B — uma VM deixa de enviar dados

1. `availability_worker.py` executa na central (separado do processo da API).
2. A cada 15 s, `availability_service.mark_stale_servers()` consulta
   `Server.last_check` (horário do **POST aceito**, não a hora declarada pelo agente).
3. Se um servidor ONLINE está há **mais de 120 segundos** sem comunicação:
   muda status para OFFLINE, adiciona evento `unavailable=true` e abre alerta
   de tipo `AVAILABILITY`, nível `CRITICAL`.
4. Uma segunda verificação não gera evento/alerta duplicado: o servidor já
   está OFFLINE. A API e o banco preservam as últimas métricas existentes.
5. Quando um novo POST válido chega, o **Fluxo A** reverte o status e resolve
   o alerta crítico. Essa é a recuperação automática.

### Fluxo C — consumo pelo dashboard (Grupo 4)

1. O frontend faz GET de `http://192.168.56.20/resumo`,
   `/servidores`, `/metricas`, `/alertas` e, se necessário, `/eventos`.
2. As rotas consultam os modelos SQLAlchemy, que geram as consultas ao MySQL
   ou ao SQLite local.
3. Flask serializa os registros em JSON e responde HTTP 200 (ou 404/400).
4. O frontend exibe indicadores, gráficos, alertas críticos e histórico.

### Fluxo D — comandos e componentes opcionais

- `ssh_diagnostics.py` consulta por SSH sem persistir e pode rodar junto do HTTP.
- `collector.py` + `ssh_service.py` via Paramiko fazem coleta alternativa;
  não devem funcionar simultaneamente com agentes HTTP nas mesmas VMs.
- `Service`/`sql/services.sql` já preparam uma tabela de serviços, mas ainda
  não expõem coleta nem rotas específicas de SSH/HTTP/Docker/serviços.

## Banco de dados

| Tabela | Campo central | Finalidade |
| --- | --- | --- |
| `servers` | `ip` (único), `status`, `last_check` | Identifica máquinas e verifica ausência de POST |
| `metrics` | `server_id`, `timestamp`, `cpu_percent`, `memory_percent`, `disk_percent`, `network_percent` | Armazena histórico |
| `alerts` | `server_id`, `alert_type`, `level`, `status` | Alertas por consumo e indisponibilidade |
| `events` | `server_id`, `history`, `unavailable`, `timestamp` | Audita quedas e recuperações |
| `services` | `server_id`, `service_name`, `status` | Estrutura futura para status de serviços |

`SQLAlchemy` coordena persistência e consultas; `PyMySQL` é o driver no MySQL.
SQLite é fallback **somente quando MySQL não foi configurado**. O esquema novo
aceita `AVAILABILITY`; bancos MySQL antigos com ENUM restrito requerem a
migração `sql/migrations/001_availability_alert.sql`.

## Escopo de entrega e testes ainda necessários no laboratório

- **Entregue no código:** API, banco/modelos, métricas, alertas 85%, OFFLINE
  por ausência de dados, recuperação, eventos, resumo e testes locais.
- **Validação externa pendente:** agentes HTTP reais, rede host-only,
  MySQL na central, integração com dashboard e desligamento/retorno da VM.
- A prova final será executar API + worker, receber POSTs, consultar MySQL,
  provocar CPU alta e desligar/religar `srv-monitor-03` para observar
  `AVAILABILITY / CRITICAL` e recuperação.

## Verificações realizadas nesta entrega

- Todos os arquivos `.py` passaram por compilação/análise sintática com Python 3.13.
- Os **5 testes independentes de Flask** passaram: 3 de parsing SSH e 2 de diagnóstico SSH (configuração/3 IPs).
- Foi conferida a consistência dos três IPs monitorados, central `.20`,
  dependências, arquivos do ZIP e presença do tipo `AVAILABILITY` no SQL.
- **Os testes de integração da API ainda não foram executados neste ambiente:**
  os pacotes Flask e Flask-SQLAlchemy não estavam instalados e não foi possível
  baixá-los daqui. Os testes estão prontos em `tests/test_api.py` e devem ser
  executados após `pip install -r requirements.txt`.
- **Não** houve acesso real às VMs, à rede Host-Only ou ao MySQL da central.

### Finalização: porta 80 e SSH como funcionalidade adicional

- `app.py` / `config.py`: a execução local do Flask usa `API_PORT=80` por padrão.
- `deploy/nginx-monitor-central.conf.example`: proxy HTTP/80 para a aplicação
  WSGI interna/5000 na VM Ubuntu, sem executar Flask como root.
- `ssh_diagnostics.py`: nova consulta SSH sem persistência de dados, que pode
  conviver com os agentes HTTP sem mascarar a regra de 120s.
- `collector.py`: permanece como coleta via SSH alternativa, não simultânea.
- `README.md`/`SSH_SETUP.md`/`.env.example`: nova porta externa 80, três VMs
  monitoradas, central no `.20`, configuração e procedimentos de teste.

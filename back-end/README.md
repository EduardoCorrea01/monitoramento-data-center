# Data Center Monitoring — Backend, API e Banco (Grupo 3)

Projeto integrador Anhanguera — *Sistema Inteligente de Monitoramento de Data Center*.
Esta pasta contém **a entrega do Grupo 3**: API REST central, validação de dados,
banco relacional, histórico, alertas por consumo e detecção de servidor OFFLINE.
O código está em inglês; as rotas possuem os aliases em português do guia.

## 1. Arquitetura definida pelo guia do professor

| VM | IP fixo | Responsável |
| --- | --- | --- |
| `srv-monitor-01` | `192.168.56.11` | Agente de métricas (Grupo 2) |
| `srv-monitor-02` | `192.168.56.12` | Agente de métricas (Grupo 2) |
| `srv-monitor-03` | `192.168.56.13` | Agente de métricas e teste de falha (Grupo 2) |
| `monitor-central` | `192.168.56.20` | **API HTTP:80, banco e dashboard** |

**São três VMs monitoradas e uma central**; o IP `.20` **não** deve aparecer
como quarta VM monitorada. A porta externa **80** foi solicitada para esta
entrega (o guia original sugere 5000). SSH continua na porta **22** e pertence
à infraestrutura (Grupo 1).

```text
VM .11: agente --\
VM .12: agente ---- POST http://192.168.56.20/monitoramento
VM .13: agente --/                 |
                                    v
                          Flask / routes/monitoring.py
                                    |
                                    v
                   services/monitoring_service.py
                      |           |           |
                      v           v           v
                  servers      metrics    alert_service
                      \           |          /
                              MySQL
                                |
                 GET /servidores, /metricas, /alertas,
                     /eventos, /resumo  -> Grupo 4

Em paralelo na central:
availability_worker.py -> availability_service.py
       -> last_check atrasado > 120s -> OFFLINE + evento + alerta CRITICAL
       -> novo POST válido          -> ONLINE + evento + alerta resolvido
```

### Repartição de responsabilidades

- **Grupo 1:** virtualização, IPs, rede, acesso SSH.
- **Grupo 2:** agente Python + `psutil` + `requests`; envio HTTP periódico.
- **Grupo 3 (este repositório):** API, validação, persistência, consultas, alertas e disponibilidade.
- **Grupo 4:** dashboard consumindo os JSONs retornados por esta API.
- **Grupo 5:** integração, cenários de falha, evidências e documentação global.

## 2. Tecnologias e arquivos

- Python 3.10+, Flask, Flask-CORS, Flask-SQLAlchemy (ORM), PyMySQL, python-dotenv.
- **MySQL** é o banco previsto para integração. **SQLite** só é usado sem
  configurações de MySQL, para desenvolvimento local.
- `paramiko` é **opcional**; não participa do fluxo exigido pelo professor.

```text
datacenter-monitoring-backend-main/
├── app.py                       # API HTTP na porta 80
├── config.py                    # banco, CORS, timeouts, debug
├── availability_worker.py       # verificação periódica de agentes sem dados
├── collector.py                 # coleta SSH ALTERNATIVA (não usar junto ao agente)
├── ssh_diagnostics.py           # leitura SSH adicional, sem salvar no banco
├── .env.example                 # modelo de configuração, sem segredos
├── requirements.txt             # dependências do Grupo 3
├── requirements-ssh.txt         # dependências opcionais para SSH
├── requirements-server.txt      # Gunicorn (Ubuntu, com proxy na porta 80)
├── deploy/
│   └── nginx-monitor-central.conf.example   # Nginx na porta HTTP 80
├── README.md                    # este guia
├── ALTERACOES_E_FLUXO.md        # histórico das mudanças e caminho dos dados
├── SSH_SETUP.md                 # modo SSH opcional
├── database/db.py               # instância SQLAlchemy
├── models/
│   ├── server.py                # servidores e última comunicação
│   ├── metric.py                # histórico de métricas
│   ├── alert.py                 # alertas
│   ├── event.py                 # quedas e recuperações
│   └── service.py               # tabela de serviços (sem endpoints ainda)
├── routes/
│   ├── monitoring.py            # POST e histórico de métricas
│   ├── servers.py               # GET servidores e resumo
│   ├── alerts.py                # GET e resolução manual de alertas
│   └── events.py                # histórico de eventos
├── services/
│   ├── monitoring_service.py    # valida, cadastra, persiste, registra recuperação
│   ├── alert_service.py         # limite 85% e indisponibilidade crítica
│   ├── availability_service.py  # marca offline depois de 2 min sem POST
│   └── ssh_service.py           # SSH opcional
├── sql/
│   ├── database.sql             # cria database monitoring
│   ├── servers.sql, metrics.sql, alerts.sql, services.sql, events.sql
│   ├── indexes.sql              # índices opcionais (executar uma vez)
│   └── migrations/001_availability_alert.sql  # MySQL legado
└── tests/
    ├── test_api.py              # testes completos de integração via SQLite
    └── test_ssh_parsers.py      # testes do coletor opcional
```

## 3. Configuração inicial (Windows PowerShell)

**Abra o terminal dentro desta pasta**, onde estão `app.py` e `requirements.txt`.
Python 3.10+ deve estar instalado. Se `python` não for encontrado no Windows,
experimente `py` e reabra o terminal após instalar o Python.

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Se o PowerShell bloquear a ativação, execute **nesta sessão somente**:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Edite `.env` para configurar o banco. **Não envie `.env` nem senhas ao Git**.
Se deixar todas as variáveis de MySQL comentadas, a aplicação cria um SQLite
local. O SQLite gerado pelo Flask normalmente fica em `instance/monitoring.db`.

### Ubuntu na VM central `.20` (ambiente do guia)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env antes de executar (especialmente se usar MySQL).
```

### Banco MySQL para a integração

1. Na central, instale/configure MySQL e execute `sql/database.sql` para criar a
   base `monitoring`. Exemplo no terminal com cliente MySQL instalado:

   ```bash
   mysql -u root -p < sql/database.sql
   ```

2. Crie um usuário do MySQL com privilégios adequados **somente** para a base
   `monitoring` e preencha **todos** os campos abaixo no `.env`:

   ```dotenv
   DB_USER=monitoring
   DB_PASSWORD=substituir_por_senha_local
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_NAME=monitoring
   ```

3. Inicie a API. SQLAlchemy `db.create_all()` cria tabelas que ainda não
   existem, mas **não atualiza estruturas existentes**.

4. **Somente se já existe MySQL antigo criado via `sql/alerts.sql` anterior**,
   faça backup e execute uma vez a migração para permitir `AVAILABILITY`:

   ```bash
   mysql -u root -p monitoring < sql/migrations/001_availability_alert.sql
   ```

5. As tabelas são `servers`, `metrics`, `alerts`, `services`, `events`.
   Índices extras opcionais estão em `sql/indexes.sql`: execute uma única vez,
   depois da criação do banco. Os scripts SQL representam **MySQL**, não SQLite.

**Atenção:** uma configuração de MySQL parcialmente preenchida gera erro de
configuração, em vez de mudar silenciosamente para SQLite.

### Porta HTTP 80: Windows (teste) e Ubuntu (integração)

O padrão do projeto é `API_PORT=80` no `.env`; **SSH continua na porta 22**.
No **Windows PowerShell**, após instalar as dependências, `python app.py`
atenderá em `http://localhost/` (porta 80), desde que essa porta esteja livre.
Em sistemas Linux, portas inferiores a 1024 exigem privilégios, portanto **não
execute o Flask como root para abrir a porta 80**.

Na **VM Ubuntu monitor-central**, o procedimento recomendado é:

1. Instale Nginx (`sudo apt install -y nginx`) e as dependências extras
   (`pip install -r requirements-server.txt`).
2. Inicie a API na **interface local** `127.0.0.1:5000` usando Gunicorn:

   ```bash
   gunicorn -w 2 -b 127.0.0.1:5000 'app:app'
   ```

3. Copie o exemplo e habilite o site na central:

   ```bash
   sudo cp deploy/nginx-monitor-central.conf.example /etc/nginx/sites-available/datacenter-api
   sudo ln -s /etc/nginx/sites-available/datacenter-api /etc/nginx/sites-enabled/datacenter-api
   # Se necessário, desative o site default quando ele também usar a porta 80:
   sudo rm /etc/nginx/sites-enabled/default
   sudo nginx -t
   sudo systemctl reload nginx
   ```

   Esses comandos pressupõem uma instalação nova do Nginx na VM de laboratório.
   Caso já existam outros sites configurados, preserve-os e ajuste o conflito
   de porta sem remover configurações necessárias.
4. Mantenha a API e `availability_worker.py` em execução (idealmente cada
   processo gerenciado por um serviço `systemd`). **Não use Gunicorn +
   `python app.py` ao mesmo tempo na porta interna 5000.**

O frontend e os agentes **sempre** utilizam a URL pública
`http://192.168.56.20/` (porta 80). O endereço `127.0.0.1:5000` é apenas
o backend local por trás do Nginx. Em qualquer modo, mantenha a API restrita
à rede de laboratório; o recebimento não possui autenticação por padrão.

## 4. Execução: DOIS processos na central

**Terminal 1 — API** (porta HTTP 80):

```bash
python app.py
```

**Terminal 2 — supervisão de ausência de dados:**

```bash
python availability_worker.py
```

Ative o mesmo ambiente virtual nos dois terminais. Deixe os dois processos
rodando na máquina central. O worker verifica a cada **15 segundos** e marca
OFFLINE após **120 segundos** sem métricas válidas. Ajuste no `.env`:

```dotenv
OFFLINE_AFTER_SECONDS=120
AVAILABILITY_CHECK_INTERVAL=15
```

O worker é separado do processo web para não depender de requisições do
dashboard nem iniciar múltiplas rotinas ao usar servidores web com workers.
**Execute somente uma cópia do worker.** `FLASK_DEBUG=0` é padrão. O servidor
embutido do Flask serve para demonstração acadêmica; não use como servidor de
produção sem configuração adicional. A central `.20` deve estar acessível pela
rede Host-Only dos três agentes. **Na VM Ubuntu, a porta 80 deve ser atendida
pelo Nginx**, conforme o exemplo de implantação na seção 3.

O SSH foi mantido como recurso adicional: `ssh_diagnostics.py` permite consultar
as 3 VMs via Paramiko **sem gravar métricas ou atualizar o heartbeat**, portanto
pode rodar mesmo com os agentes HTTP. `collector.py` permanece como modo de coleta
**alternativo** para quando os agentes HTTP estiverem parados; **não execute
`collector.py` junto com agentes HTTP dos mesmos servidores** para não duplicar
métricas nem mascarar a regra de OFFLINE. Consulte [SSH_SETUP.md](SSH_SETUP.md).

## 5. Contrato de integração para o Grupo 2

O guia envia via `psutil` + `requests` para:

```text
POST http://192.168.56.20/monitoramento
Content-Type: application/json
```

JSON de exemplo exatamente no formato esperado pelo guia:

```json
{
  "servidor": "srv-monitor-01",
  "ip": "192.168.56.11",
  "cpu": 42,
  "memoria": 58,
  "disco": 65,
  "data_hora": "2026-10-19T19:00:00"
}
```

Obrigatórios: `servidor` (ou `server`), `ip`, `cpu`, `memoria` (ou `memory`),
`disco` (ou `disk`). Os percentuais precisam ser números de 0 a 100.
Opcionalmente, envie `disk_total_gb` e `disk_used_gb` como números em GB; ambos
são armazenados e devolvidos pela consulta de métricas.
Opcionais: `rede`/`network` (se ausente fica **0, valor padrão**, **não uma
medição real**), `data_hora`/`timestamp`, `sistema_operacional` e `status=ONLINE`.
Uma leitura válida implica ONLINE; não envie `status=OFFLINE` na rota de dados:
a detecção OFFLINE é função do worker central.

`last_check` (último POST **aceito**, UTC) é diferente de `timestamp` (horário
informado pelo agente, armazenado no histórico; sem timezone assume UTC).
Isso evita que um agente com relógio errado faça a VM ficar OFFLINE.

Resposta HTTP **201**:

```json
{
  "message": "Data received successfully",
  "status": "ok",
  "server_id": 1,
  "alerts_created": 0,
  "alerts_resolved": 0
}
```

## 6. API — endpoints de consulta para o Grupo 4

Todas as rotas possuem aliases em português e inglês:

| Método | Rotas | O que retornam |
| --- | --- | --- |
| GET | `/` | Status básico da API |
| POST | `/monitoramento`, `/monitoring` | Recebimento de métricas (201 / 400) |
| GET | `/servidores`, `/servers` | Servidores cadastrados com status e último POST |
| GET | `/servidores/<id>`, `/servers/<id>` | Detalhe de um servidor (404 se ausente) |
| GET | `/metricas`, `/metrics` | Histórico de métricas |
| GET | `/alertas`, `/alerts` | Alertas (ativos por padrão) |
| PUT | `/alertas/<id>/resolver`, `/alerts/<id>/resolve` | Resolver alerta manualmente |
| GET | `/eventos`, `/events` | Eventos de queda e recuperação |
| GET | `/resumo`, `/summary` | Totais ONLINE, OFFLINE e alertas ativos |

Filtros e limites:

- `GET /metricas?servidor_id=1&limit=100` (ou `server_id`), limite 1–1000,
  padrão **100** registros recentes.
- `GET /eventos?servidor_id=1&limit=100`, mesma regra de limite.
- `GET /alertas?status=ACTIVE` (padrão), `RESOLVED` ou `ALL`.

Resposta de `/resumo`:

```json
{
  "servers_total": 3,
  "online": 2,
  "offline": 1,
  "active_alerts": 1,
  "critical_alerts": 1
}
```

Valores ilustrativos. Rotas de `services` não estão expostas; a tabela está
preparada para uma etapa futura. Os JSONs são acessíveis pelo dashboard do Grupo
4 conforme a configuração de CORS.

## 7. Alertas, quedas e recuperação

**Consumo:** se CPU, RAM ou disco forem **>= 85%**, cria-se um alerta `ACTIVE`
com nível `ALERT`. Sem duplicar alertas ativos para o mesmo servidor e recurso.
Uma leitura abaixo de 85% muda esse alerta para `RESOLVED`.

**Ausência de agente:** se o servidor estava ONLINE e não houve novo POST
válido em **mais de 120 segundos**, o worker:

1. marca `servers.status = OFFLINE`;
2. adiciona um registro em `events` com `unavailable = true`;
3. abre um alerta `alerts.alert_type = AVAILABILITY`, `level = CRITICAL`.

Uma VM OFFLINE continua sem novas métricas; não se inventa CPU=0 para ela.
Alertas existentes por CPU, RAM e disco **não são resolvidos** por perda de
contato. Ao receber novo POST válido, o backend faz:

1. `servers.status = ONLINE` e atualiza `last_check`;
2. registra a recuperação em `events` (`unavailable = false`);
3. resolve os alertas ativos de `AVAILABILITY`;
4. registra a nova métrica e atualiza os alertas por recurso.

A rotina não duplica alertas de disponibilidade em verificações sucessivas.
Tentar resolver manualmente um alerta de disponibilidade **enquanto OFFLINE**
retorna **409 Conflict**, para não esconder uma indisponibilidade real.

O Guia do professor sugere 2 minutos como critério de OFFLINE. Essa detecção
identifica **ausência de dados**, não comprova por si só que a VM desligou:
também pode indicar queda de rede, interrupção do agente ou falha de acesso.

## 8. Testes e demonstração

### Teste rápido no PowerShell (na máquina central)

Execute a API e o worker antes. O PowerShell usa `Invoke-RestMethod`:

```powershell
$body = @{
    servidor = 'srv-monitor-01'
    ip = '192.168.56.11'
    cpu = 92
    memoria = 58
    disco = 65
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1/monitoramento' `
    -ContentType 'application/json' -Body $body

Invoke-RestMethod 'http://127.0.0.1/servidores'
Invoke-RestMethod 'http://127.0.0.1/metricas'
Invoke-RestMethod 'http://127.0.0.1/alertas'
Invoke-RestMethod 'http://127.0.0.1/resumo'
```

Como `cpu=92`, um alerta de CPU será criado. Para resolver, envie novo POST
com `cpu=40`. Para testar OFFLINE, aguarde o limite configurado **sem novos
POSTs** (ou, em ambiente de teste, configure um limite curto). Depois faça um
novo POST e confira a recuperação.

### Testes automatizados

```bash
python -m unittest discover -s tests -v
```

Os testes usam SQLite em memória e **não dependem das VMs nem do MySQL real**.
Cobrem validação, gravação de métricas, limiar, deduplicação, OFFLINE, alerta
crítico, histórico, recuperação, resumo e endpoints. Os testes de SSH só verificam
os interpretadores de métricas e a seleção dos três IPs, sem conectar a uma VM.

### Validação de integração com os grupos

1. Grupo 1 confirma rede: de cada VM, acessar `192.168.56.20` na porta TCP 80.
2. Grupo 2 envia dados reais a `/monitoramento` automaticamente.
3. Grupo 3 verifica métricas, banco MySQL, alertas e worker.
4. Grupo 4 integra `/servidores`, `/metricas`, `/alertas` e `/resumo`.
5. Grupo 5 simula CPU alta, queda da VM 3, status OFFLINE e recuperação.

## 9. Limites conhecidos e cuidados

- **Não foi testada aqui** a conectividade real às VMs nem a instância MySQL da
  central; o teste de integração depende do laboratório.
- Não há autenticação na API: **use somente na rede de laboratório controlada**.
  Em uso real, implementar autorização/autenticação e CORS restrito.
- `CORS_ORIGINS=*` simplifica testes. Restrinja às origens do dashboard ao
  publicar o sistema fora do laboratório.
- A checagem OFFLINE depende do worker separado. Se ele não rodar, o status
  OFFLINE não será atualizado automaticamente.
- `db.create_all()` não migra MySQL existente; execute a migração indicada.
- IPs são declarados pelo agente; a API valida formato, mas não autentica que
  são realmente o remetente. Não exponha isso em redes não confiáveis.
- `network_percent=0` quando não enviado é valor padrão, não leitura efetiva.
- A consulta de métricas e eventos é limitada aos registros mais recentes.
- A aplicação registra o histórico; não implementa limpeza/arquivamento de
  séries temporais ou filas de mensagens.
- Para implantação persistente no Ubuntu, configure API e worker como serviços
  `systemd` separados, com logs, reinício e usuário sem privilégios excessivos.

## 10. Principais alterações realizadas

- Adequação para **três servidores monitorados + uma central `.20`**.
- Modo principal **agentes HTTP** como o guia; SSH preservado como opcional.
- Nova rotina independente `availability_worker.py` e serviço de detecção.
- Novos eventos e alertas `AVAILABILITY / CRITICAL` para servidores OFFLINE.
- Recuperação ONLINE automática ao receber novo POST válido.
- Rotas novas `/eventos` e `/resumo` e consultas com `limit`.
- Melhor tratamento de campos, percentuais, erros e configuração do MySQL.
- Schema MySQL atualizado e migração para banco antigo.
- Diagnóstico SSH adicional sem alterar a coleta HTTP.
- Publicação HTTP na porta 80 e configuração Nginx para Ubuntu.
- Mais testes automatizados e documentação de integração.

Veja [ALTERACOES_E_FLUXO.md](ALTERACOES_E_FLUXO.md) para o detalhamento arquivo
a arquivo e todo o fluxo de execução.

## 11. Diagnóstico SSH adicional sem interferir no HTTP

Para executar uma **consulta avulsa** às 3 VMs sem escrever no banco nem alterar
`last_check`, instale `pip install -r requirements-ssh.txt`, configure
`SSH_USER`, `SSH_KEY_PATH` e as chaves de host conhecidas, e rode:

```bash
python ssh_diagnostics.py
```

As leituras são apenas exibidas no terminal. Isso é seguro para usar com os
agentes HTTP simultaneamente. `collector.py` só deve ser iniciado como um
**modo alternativo de coleta** quando os agentes HTTP estiverem desligados.

**Limitação:** as falhas de SSH isoladas não comprovam que a VM está desligada.
A fonte oficial do estado ONLINE/OFFLINE é a chegada de métricas válidas na
API conforme a regra dos 120 segundos. A medição de rede via SSH ainda usa
`network=0` como valor não coletado, sem afirmar que a rede está ociosa.

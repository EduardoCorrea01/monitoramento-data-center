# Coleta SSH opcional — não é o fluxo principal do guia

O guia do professor pede **três agentes HTTP (Grupo 2)**, instalados em
`192.168.56.11`, `.12`, `.13`, enviando dados para `192.168.56.20`.
A máquina `.20` é a central, não a quarta VM monitorada.

Há **duas formas distintas de usar SSH**:

- `python ssh_diagnostics.py`: mostra CPU/RAM/disco via SSH; **não altera
  o banco nem os heartbeats**, portanto pode ser usado com agentes HTTP.
- `python collector.py`: grava métricas por SSH no banco. É um **modo
  alternativo**, apenas quando os agentes HTTP daquelas mesmas VMs estiverem
  parados. Nunca execute `collector.py` junto com os agentes HTTP monitorando
as mesmas VMs: isso duplica métricas e mascara a detecção de indisponibilidade.

Requisitos: Linux nas 3 VMs, SSH (porta 22), usuário não-root, chave SSH válida,
chaves de host já verificadas. Instale com `pip install -r requirements-ssh.txt`.
Configure `.env` usando as variáveis comentadas em `.env.example`, em particular
`VM1_IP`, `VM2_IP`, `VM3_IP`, `SSH_USER` e `SSH_KEY_PATH`.

Após verificar manualmente o acesso SSH e as impressões digitais das chaves do
servidor, execute `python ssh_diagnostics.py` para um diagnóstico paralelo
seguro. Se for usar SSH em vez dos agentes, execute `python collector.py` apenas se os agentes HTTP estiverem parados.
A API e o worker de disponibilidade rodam em terminais separados.

Uma falha SSH no modo coletor pode ser registrada como **evento de diagnóstico**;
no modo `ssh_diagnostics.py`, ela apenas aparece no terminal. Nenhuma das duas
situações comprova que a VM foi desligada. A rotina de disponibilidade marca um servidor OFFLINE quando ele
passa do limite de tempo configurado sem leituras válidas. A coleta opcional
atualmente envia `network=0` por não calcular uso percentual da interface.

O procedimento oficial e a configuração do MySQL estão no [README](README.md).

SSH utiliza TCP **22**; a API HTTP utiliza TCP **80** na central `.20`.
No Linux, publique a API com Nginx na 80, conforme o README.

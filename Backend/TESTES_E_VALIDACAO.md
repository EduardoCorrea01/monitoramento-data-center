# Testes e validação — Grupo 3

## Verificado na preparação desta versão

- Compilação e análise de sintaxe: **26 arquivos Python**, sem erro.
- Testes locais executáveis sem Flask: **5/5 passaram**
  (`test_ssh_parsers.py` e `test_ssh_diagnostics.py`).
- Verificado estaticamente: `API_PORT=80`, Nginx TCP/80, três VMs monitoradas
  (`.11`, `.12`, `.13`), central `.20`, alerta MySQL `AVAILABILITY`.
- `collector.py` (SSH alternativo) e `ssh_diagnostics.py` (SSH adicional)
  não foram testados em VMs reais.

## Não verificado neste ambiente

- Testes de integração da API Flask (`tests/test_api.py`): as dependências
  `Flask` e `Flask-SQLAlchemy` não estão instaladas e a instalação online
  não foi possível no ambiente de construção.
- MySQL real, agentes do Grupo 2, rede entre VMs e dashboard do Grupo 4.

## Como testar depois de instalar as dependências

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python app.py
```

Em outro terminal execute `python availability_worker.py`.
Teste o POST em `http://localhost/monitoramento` (Windows) ou
`http://192.168.56.20/monitoramento` (central Ubuntu publicada via Nginx).
Veja instruções completas no `README.md`.

**Observação:** executar testes com SQLite em memória não comprova
compatibilidade com o MySQL configurado no laboratório. Valide separadamente.

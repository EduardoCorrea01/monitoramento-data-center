
# -=-=-=- IMPORTAÇÕES -=-=-=-
import time
import json
import platform
import socket
import psutil
import requests

# -=-=-=- CONFIGURAÇÕES BÁSICAS -=-=-=-
AGENTE_ID = platform.node()
INTERVALO_COLETA = 30

# Endereço da API central
BACKEND_URL = "http://192.168.56.20:5000/monitoramento"


# -=-=-=- FUNÇÃO DE COLETA PRINCIPAL -=-=-=-
def coletar_dados_sistema():
    """
    Função central de coleta.
    A estrutura do JSON segue o contrato de comunicação definido para o projeto.
    """
    dados = {
        "agente_id": AGENTE_ID,
        "ip_agente": None,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sistema_operacional": platform.system(),
        "metricas": {
            "cpu": {},
            "memoria_ram": {},
            "disco": {}
        }
    }

    # -=-=-=- IDENTIFICAÇÃO DO AGENTE -=-=-=-
    try:
        conexao = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conexao.connect(("192.168.56.20", 5000))
        dados["ip_agente"] = conexao.getsockname()[0]
        conexao.close()
    except OSError:
        dados["ip_agente"] = socket.gethostbyname(
            socket.gethostname()
        )

    # -=-=-=- PARTE DO FABRÍCIO (CPU) -=-=-=-
    dados["metricas"]["cpu"] = {
        "uso_porcentagem": psutil.cpu_percent(interval=1),
        "nucleos": psutil.cpu_count(logical=True)
    }

    # -=-=-=- PARTE DO WESLEY (RAM) -=-=-=-
    memoria = psutil.virtual_memory()
    percentual_ram = memoria.percent

    # Lógica de alertas de RAM
    status_alerta_ram = "Normal"
    if percentual_ram >= 90:
        status_alerta_ram = "Crítico: Memória RAM muito alta"
    elif percentual_ram >= 85:
        status_alerta_ram = "Atenção: Uso elevado de memória"

    dados["metricas"]["memoria_ram"] = {
        "total_gb": round(memoria.total / (1024**3), 2),
        "em_uso_gb": round(memoria.used / (1024**3), 2),
        "disponivel_gb": round(memoria.available / (1024**3), 2),
        "uso_porcentagem": percentual_ram,
        "status": status_alerta_ram
    }

    # -=-=-=- PARTE DO RAFAEL (DISCO) -=-=-=-
    caminho_disco = (
        "C:\\" if platform.system() == "Windows" else "/"
    )
    disco = psutil.disk_usage(caminho_disco)

    dados["metricas"]["disco"] = {
        "total_gb": round(disco.total / (1024**3), 2),
        "em_uso_gb": round(disco.used / (1024**3), 2),
        "uso_porcentagem": disco.percent
    }

    return dados


# -=-=-=- FORMATAÇÃO DO PAYLOAD PARA O BACKEND -=-=-=-
def montar_payload(d):
    m = d["metricas"]
    return {
        "servidor": AGENTE_ID,
        "ip": d["ip_agente"],
        "cpu": m["cpu"]["uso_porcentagem"],
        "memoria": m["memoria_ram"]["uso_porcentagem"],
        "disco": m["disco"]["uso_porcentagem"],
        "disk_total_gb": m["disco"]["total_gb"],
        "disk_used_gb": m["disco"]["em_uso_gb"],
        "sistema_operacional": d["sistema_operacional"],
        "timestamp": d["timestamp"],
        "status": "ONLINE"
    }


# -=-=-=- EXECUÇÃO PRINCIPAL -=-=-=-
def main():
    print(f"Iniciando Agente de Monitoramento: {AGENTE_ID}")
    print(f"API: {BACKEND_URL}")
    print("Pressione Ctrl+C para interromper.\n")

    try:
        while True:
            payload = coletar_dados_sistema()

            print(f"[{payload['timestamp']}] Dados coletados:")
            print(f"IP do agente: {payload['ip_agente']}")
            print(json.dumps(payload, indent=2, ensure_ascii=False))

            # Envio dos dados para o Backend
            try:
                r = requests.post(
                    BACKEND_URL,
                    json=montar_payload(payload),
                    timeout=5
                )

                print("Resposta do backend:", r.status_code, r.text)
                r.raise_for_status()

            except requests.RequestException as e:
                print("Falha ao enviar:", e)

            print("-" * 50)
            time.sleep(INTERVALO_COLETA)

    except KeyboardInterrupt:
        print("\nAgente de monitoramento finalizado com sucesso.")

    except Exception as e:
        print(f"\nErro inesperado durante a execução do agente: {e}")


if __name__ == "__main__":
    main()

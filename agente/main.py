# -=-=-=- IMPORTAÇÕES -=-=-=-
import time
import json
import platform
import psutil
import requests

# -=-=-=- CONFIGURAÇÕES BÁSICAS -=-=-=-
AGENTE_ID = "servidor-prod-01" 
INTERVALO_COLETA = 5 

# -=-=-=- FUNÇÃO DE COLETA PRINCIPAL -=-=-=-
def coletar_dados_sistema():
    """
    Função central de coleta.
    A estrutura do JSON segue o contrato de comunicação definido para o projeto.
    """
    dados = {
        "agente_id": AGENTE_ID,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sistema_operacional": platform.system(),
        "metricas": {
            "cpu": {},
            "memoria_ram": {},
            "disco": {}
        }
    }
    
    # -=-=-=- PARTE DO FABRÍCIO (CPU) -=-=-=-
    dados["metricas"]["cpu"] = {
        "uso_porcentagem": psutil.cpu_percent(interval=1),
        "nucleos": psutil.cpu_count(logical=True)
    }
    
    # -=-=-=- PARTE DO WESLEY (RAM) -=-=-=-
    # Integração baseada no monitor_ram.py do repositório
    memoria = psutil.virtual_memory()
    percentual_ram = memoria.percent
    
    # Lógica de alertas de RAM
    status_alerta_ram = "Normal"
    if percentual_ram >= 90:
        status_alerta_ram = "Crítico: Memória RAM muito alta"
    elif percentual_ram >= 80:
        status_alerta_ram = "Atenção: Uso elevado de memória"
        
    dados["metricas"]["memoria_ram"] = {
        "total_gb": round(memoria.total / (1024**3), 2),
        "em_uso_gb": round(memoria.used / (1024**3), 2),
        "disponivel_gb": round(memoria.available / (1024**3), 2),
        "uso_porcentagem": percentual_ram,
        "status": status_alerta_ram
    }
    
    # -=-=-=- PARTE DO RAFAEL (DISCO) -=-=-=-
    disco = psutil.disk_usage('/')
    dados["metricas"]["disco"] = {
        "total_gb": round(disco.total / (1024**3), 2),
        "em_uso_gb": round(disco.used / (1024**3), 2),
        "uso_porcentagem": disco.percent
    }
    
    return dados

# -=-=-=- EXECUÇÃO PRINCIPAL -=-=-=-
def main():
    print(f"Iniciando Agente de Monitoramento: {AGENTE_ID}")
    print("Pressione Ctrl+C para interromper.\n")
    
    try:
        while True:
            payload = coletar_dados_sistema()
            
            print(f"[{payload['timestamp']}] Dados coletados prontos para envio:")
            print(json.dumps(payload, indent=2))
            print("-" * 50)
            
            time.sleep(INTERVALO_COLETA)
            
    except KeyboardInterrupt:
        print("\nAgente de monitoramento finalizado com sucesso.")
    except Exception as e:
        print(f"\nErro inesperado durante a execução do agente: {e}")

if __name__ == "__main__":
    main()

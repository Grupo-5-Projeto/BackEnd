from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import asyncio
from dht22 import DHT22
from visao_computacional import VisaoComputacional
from paciente import PacienteSensores
import schedule

# carregando vairaveis de ambiente
load_dotenv()

def envio_dado(instance):
    asyncio.create_task(instance.handler())

async def main():
    connect_azure_ambiente = os.getenv("CONNECT_AZURE_AMBIENTE")
    connect_azure_visao = os.getenv("CONNECT_AZURE_VISAO_COMPUTACIONAL")
    connect_azure_paciente = os.getenv("CONNECT_AZURE_PACIENTE")

    # Inicializa a variável de ambiente para a correlação com o DHT22
    os.environ['QTD_PESSOAS'] = "0"

    print("Configurando sensores...")
    dht22 = DHT22()
    await dht22.config(connect_azure_ambiente)

    camera = VisaoComputacional()
    await camera.config(connect_azure_visao)

    pacientes = PacienteSensores()
    await pacientes.config(connect_azure_paciente)
    print("Configuração completa.")

    # --- Lógica de simulação histórica ---
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    interval = timedelta(minutes=5)

    print(f"\nIniciando simulação histórica dos últimos 7 dias:")
    print(f"De: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Até: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Intervalo: 5 minutos\n")

    current_time = start_time
    # Loop while para iterar sobre o tempo
    while current_time <= end_time:
        # Imprime o timestamp atual que está sendo simulado
        print(f"--- Simulando dados para: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ---")

        # Simula o sensor de visão computacional para este timestamp
        # O handler da visão atualiza a variável de ambiente QTD_PESSOAS
        await camera.handler(current_time)

        # Simula o sensor de ambiente (temperatura e umidade) para este timestamp
        # O handler do DHT22 lê a variável de ambiente QTD_PESSOAS atualizada pela visão
        await dht22.handler(current_time)

        # Simula o sensor de paciente (oximetria e temperatura corporal) para este timestamp
        # O handler do paciente escolhe um ID de paciente aleatório a cada rodada
        await pacientes.handler(current_time)

        # Avança o tempo em 5 minutos
        current_time += interval

        # Pequeno sleep para não sobrecarregar, mesmo com mock
        # await asyncio.sleep(0.01) # Opcional, dependendo da velocidade desejada da simulação

    print("\nSimulação histórica concluída.")

    # O mock device não precisa ser explicitamente desligado na maioria dos casos,
    # mas se houvesse um shutdown, seria chamado aqui.
    # await dht22.client.shutdown()
    # await camera.client.shutdown()
    # await pacientes.client.shutdown()

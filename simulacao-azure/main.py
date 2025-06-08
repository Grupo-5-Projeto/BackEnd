from dotenv import load_dotenv
import os
import asyncio
from device_mock import DeviceLocal 
from dht22 import DHT22
from visao_computacional import VisaoComputacional
from paciente import PacienteSensores
import schedule
from dados_mockados import MockDados
from  azure.identity import DefaultAzureCredential
from datetime import datetime
from azure.storage.blob import BlobClient
import threading
import time

# carregando vairaveis de ambiente
load_dotenv()

def envio_dado(instance):
    asyncio.create_task(instance.handler())

def envio_dado_pacientes(instance):
    asyncio.create_task(instance.handler_azure())

def thread_func(loop, task, parameter):
    loop.call_soon_threadsafe(asyncio.create_task, task(parameter))

async def main():
    DefaultAzureCredential()
    os.environ["QTD_PESSOAS"] = "0"

    dht22 = None
    camera = None
    pacientes = None

    if os.getenv("ENVIROMENT") == "mock":
        print("Gerando massa de dados mockados")
        print(f"Gerando para {os.getenv("SAVE")}")
        mock_dados = MockDados()

        camera = VisaoComputacional()
        await camera.config("")
        # await mock_dados.gerar_massa(camera)

        dht22 = DHT22()
        await dht22.config("")
        # await mock_dados.gerar_massa(dht22)

        pacientes = PacienteSensores()
        await pacientes.config("")
        # await mock_dados.gerar_massa(pacientes)
    
        loop = asyncio.get_running_loop()

        t1 = threading.Thread(target=thread_func, args=(loop, mock_dados.gerar_massa,camera,))
        t2 = threading.Thread(target=thread_func, args=(loop, mock_dados.gerar_massa, dht22,))
        t3 = threading.Thread(target=thread_func, args=(loop, mock_dados.gerar_massa, pacientes,))

        t1.start()
        t2.start()
        t3.start()

        await asyncio.sleep(3)

        if os.getenv("SAVE") == "archive":
            print("Enviando arquivos para o Blob")
            pasta = "./arquivos"
            for nome_arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, nome_arquivo)
                with open(caminho_arquivo, "rb") as data:
                    blob_client = BlobClient.from_connection_string(
                        conn_str=os.getenv("CONNECT_BLOB"),
                        blob_name=nome_arquivo,
                        container_name="blob-raw-sensores"
                    )
                    blob_client.upload_blob(data, overwrite=True)
                    time.sleep(5)
            print("Arquivos enviados para o Blob")
            
    else:
        print("Iniciando simulação enviando dados para o IotHub")
        dht22 = DHT22()
        await dht22.config(os.getenv("CONNECT_AZURE_AMBIENTE"))

        camera = VisaoComputacional()
        await camera.config(os.getenv("CONNECT_AZURE_VISAO_COMPUTACIONAL"))

        pacientes = PacienteSensores()
        await pacientes.config(os.getenv("CONNECT_AZURE_PACIENTE"))

        schedule.every(5).seconds.do(lambda: envio_dado(camera))
        schedule.every(5).seconds.do(lambda: envio_dado(dht22))
        schedule.every(15).seconds.do(lambda: envio_dado_pacientes(pacientes))

        while True:
            schedule.run_pending()
            await asyncio.sleep(1)

asyncio.run(main())
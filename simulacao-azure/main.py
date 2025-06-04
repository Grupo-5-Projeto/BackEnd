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

# carregando vairaveis de ambiente
load_dotenv()

def envio_dado(instance):
    asyncio.create_task(instance.handler())

def envio_dado_pacientes(instance):
    asyncio.create_task(instance.handler_azure())

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

        dht22 = DHT22()
        await dht22.config("")
        await mock_dados.gerar_massa(dht22)


        camera = VisaoComputacional()
        await camera.config("")
        await mock_dados.gerar_massa(camera)

        pacientes = PacienteSensores()
        await pacientes.config("")
        await mock_dados.gerar_massa(pacientes)

        # data_geracao_str = os.getenv("DATA_GERACAO")
        # data_geracao_dt = datetime.strptime(data_geracao_str + " 22:00:00", "%Y-%m-%d %H:%M:%S")
        # await pacientes.handler_mockado(data_geracao_dt)

        await dht22.disconnect()
        await camera.disconnect()
        await pacientes.disconnect()

        
        if os.getenv("SAVE") == "archive":
            print("Gerando arquivos e enviado para o Blob")
            pasta = "./arquivos"
            for nome_arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, nome_arquivo)

                caractere_inicio = '['
                caractere_fim = ']'

                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                novo_conteudo = caractere_inicio + conteudo + caractere_fim

                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    f.write(novo_conteudo)


                with open(caminho_arquivo, "rb") as data:
                    blob_client = BlobClient.from_connection_string(
                        conn_str=os.getenv("CONNECT_BLOB"),
                        blob_name=nome_arquivo,
                        container_name="blob-raw-sensores"
                    )
                    blob_client.upload_blob(data, overwrite=True)
            print("Arquivos enviados para o Blob")
            
    else:
        print("Iniciando simulação enviando dados para o IotHub")
        dht22 = DHT22()
        await dht22.config(os.getenv("CONNECT_AZURE_AMBIENTE"))

        camera = VisaoComputacional()
        await camera.config(os.getenv("CONNECT_AZURE_VISAO_COMPUTACIONAL"))

        pacientes = PacienteSensores()
        await pacientes.config(os.getenv("CONNECT_AZURE_PACIENTE"))

        schedule.every(2).seconds.do(lambda: envio_dado(dht22))
        schedule.every(5).seconds.do(lambda: envio_dado(camera))
        schedule.every(5).seconds.do(lambda: envio_dado_pacientes(pacientes))

        while True:
            schedule.run_pending()
            await asyncio.sleep(1)

asyncio.run(main())
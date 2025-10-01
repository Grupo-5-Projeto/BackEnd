from dotenv import load_dotenv
import os
import asyncio
from dht22 import DHT22
from visao_computacional import VisaoComputacional
from paciente import PacienteSensores
import schedule
from dados_mockados import MockDados
import threading
import boto3

# carregando vairaveis de ambiente
load_dotenv()

def envio_dado(instance):
    asyncio.create_task(instance.handler())

def envio_dado_pacientes(instance):
    asyncio.create_task(instance.handler_azure())

def thread_func(loop, task, parameter):
    loop.call_soon_threadsafe(asyncio.create_task, task(parameter))

async def main():
    os.environ["QTD_PESSOAS"] = "0"

    camera = VisaoComputacional()
    dht22 = DHT22()
    pacientes = PacienteSensores()

    if os.getenv("ENVIROMENT") == "mock":
        print("Gerando massa de dados mockados")
        print(f"Gerando para {os.getenv("SAVE")}")
        mock_dados = MockDados()

        loop = asyncio.get_running_loop()

        t1 = threading.Thread(target=thread_func, args=(loop, mock_dados.gerar_massa, camera,))
        t2 = threading.Thread(target=thread_func, args=(loop, mock_dados.gerar_massa, dht22,))
        t3 = threading.Thread(target=thread_func, args=(loop, mock_dados.gerar_massa, pacientes,))

        t1.start()
        t2.start()
        t3.start()

        await asyncio.sleep(3)

        if os.getenv("SAVE") == "archive":
            pasta = "./arquivos"
            bucket_name = os.environ["BUCKET"]
            s3_client = boto3.client('s3')
            for nome_arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, nome_arquivo)
                with open(caminho_arquivo, "rb") as data:
                    s3_client.upload_fileobj(data, bucket_name, nome_arquivo)
            print("Arquivos enviados para o S3")
            
    else:
        print("Iniciando simulação enviando dados para a AWS")
        schedule.every(5).seconds.do(lambda: envio_dado(camera))
        schedule.every(5).seconds.do(lambda: envio_dado(dht22))
        schedule.every(5).seconds.do(lambda: envio_dado_pacientes(pacientes))

        while True:
            schedule.run_pending()
            await asyncio.sleep(1)

asyncio.run(main())
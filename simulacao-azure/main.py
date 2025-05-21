from dotenv import load_dotenv
import os
import asyncio
from device_mock import DeviceLocal 
from dht22 import DHT22
from visao_computacional import VisaoComputacional
from paciente import PacienteSensores
import schedule
from dados_mockados import MockDados

# carregando vairaveis de ambiente
load_dotenv()

def envio_dado(instance):
    asyncio.create_task(instance.handler())


async def main():
    os.environ["QTD_PESSOAS"] = "0"

    dht22 = None
    camera = None
    pacientes = None

    if os.getenv("ENVIROMENT") == "db":
        mock_dados = MockDados()

        dht22 = DHT22()
        await dht22.config("")
        await mock_dados.gerar_massa(dht22)


        camera = VisaoComputacional()
        await camera.config("")
        await mock_dados.gerar_massa(camera)

        pacientes = PacienteSensores()
        await pacientes.config("")
        # CHAMA O HANDLER DIRETAMENTE PARA GERAR OS DADOS PARA OS 109 PACIENTES
        print("Gerando dados de oximetria e temperatura para 109 pacientes...")
        await pacientes.handler()
        # await mock_dados.gerar_massa(pacientes)
        print("Geração de dados de pacientes concluída para 109 pacientes.")

        # await dht22.disconnect()
        # await camera.disconnect()
        await pacientes.disconnect()

    else:
        dht22 = DHT22()
        await dht22.config(os.getenv("CONNECT_AZURE_AMBIENTE"))

        camera = VisaoComputacional()
        await camera.config(os.getenv("CONNECT_AZURE_VISAO_COMPUTACIONAL"))

        pacientes = PacienteSensores()
        await pacientes.config(os.getenv("CONNECT_AZURE_PACIENTE"))

        schedule.every(2).seconds.do(lambda: envio_dado(dht22))
        schedule.every(5).seconds.do(lambda: envio_dado(camera))
        schedule.every(5).seconds.do(lambda: envio_dado(pacientes))

        while True:
            schedule.run_pending()
            await asyncio.sleep(1)

asyncio.run(main())
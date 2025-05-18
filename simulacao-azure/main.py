from dotenv import load_dotenv
import os
import asyncio
from device_mock import DeviceLocal 
from dht22 import DHT22
from visao_computacional import VisaoComputacional
from paciente import PacienteSensores
import schedule

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
        print("ENTROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOU")
        dht22 = DHT22()
        await dht22.config("")

        # camera = VisaoComputacional()
        # await camera.config(client_database)

        # pacientes = PacienteSensores()
        # await pacientes.config(client_database)
    else:
        print("ENTROu")
        dht22 = DHT22()
        await dht22.config(os.getenv("CONNECT_AZURE_AMBIENTE"))

        camera = VisaoComputacional()
        await camera.config(os.getenv("CONNECT_AZURE_VISAO_COMPUTACIONAL"))

        pacientes = PacienteSensores()
        await pacientes.config(os.getenv("CONNECT_AZURE_PACIENTE"))

    print(type(dht22))

    schedule.every(2).seconds.do(lambda: envio_dado(dht22))
    # schedule.every(20).seconds.do(lambda: envio_dado(camera))
    # schedule.every(60).seconds.do(lambda: envio_dado(pacientes))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

asyncio.run(main())
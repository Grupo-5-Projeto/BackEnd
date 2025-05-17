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
    dht22 = DHT22()
    await dht22.config(os.getenv("CONNECT_AZURE_AMBIENTE"))

    camera = VisaoComputacional()
    await camera.config(os.getenv("CONNECT_AZURE_VISAO_COMPUTACIONAL"))

    pacientes = PacienteSensores()
    await pacientes.config(os.getenv("CONNECT_AZURE_PACIENTE"))

    schedule.every(15).seconds.do(lambda: envio_dado(dht22))
    schedule.every(20).seconds.do(lambda: envio_dado(camera))
    schedule.every(60).seconds.do(lambda: envio_dado(pacientes))

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

asyncio.run(main())

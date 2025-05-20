from datetime import datetime
from device_connect import Device
from device_mock import DeviceLocal
import random
import math
import os


class VisaoComputacional:
    def __init__(self):
        self.client = None
        self.quantidade_pessoas = None
        self.data = None

    async def config(self, connect_string):
        if os.getenv("ENVIROMENT") == "db":
            self.client = DeviceLocal()
            await self.client.connect()
        else:
            self.client = Device()
            await self.client.connect(connect_string)   


    async def handler(self, data_mockada=None):
        tipo_dado = random.choice(["limpo", "limpo", "sujo", "inesperado"])
        id_upa = random.randrange(1, 35)

        if data_mockada != None:
            self.data = data_mockada
        else:
            self.data = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        if tipo_dado == "limpo":
            self.dados_limpos()
        elif tipo_dado == "sujo":
            self.dados_sujos()
        else:
            self.dados_inesperados()
        await self.send(id_upa)


    async def send(self, id):       
        await self.client.send_message({
            "data_hora": self.data,
            "valor": self.quantidade_pessoas,
            "fk_upa": id,
            "fk_paciente": None,
            "fk_sensor": 1,
            "fk_unid_medida": None,
        })


    def visao_computacional(self):
        valor = int(random.gauss(50, 30))
        return max(0, valor)


    def dados_limpos(self):
        self.quantidade_pessoas = self.visao_computacional()
        os.environ['QTD_PESSOAS'] = str(self.quantidade_pessoas)
        

    def dados_sujos(self):
        numero = random.randrange(1, 50)
        if numero < 10:
            self.quantidade_pessoas = None
        elif numero > 10 and numero < 30:
            self.quantidade_pessoas = random.uniform(111, 555)
        else:
            self.quantidade_pessoas = random.uniform(-10, 1)
    

    def dados_inesperados(self):
        spike = random.choice([100, -10, 200, -15])
        self.quantidade_pessoas = round(self.visao_computacional() + spike, 2)

    async def disconnect(self):
        await self.client.shutdown()

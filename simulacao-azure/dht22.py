from datetime import datetime
from device_mock import Device
# from device_connect import Device
import random
import math

class DHT22:
    def __init__(self):
        self.client = None
        self.temperatura = None
        self.umidade = None

    async def config(self, connect_string):
        self.client = Device()
        await self.client.connect(connect_string)    

    async def handler(self):
        tipo_dado = random.choice(["limpo", "limpo", "limpo", "limpo", "sujo", "inesperado"])
        id_upa = random.randrange(1, 35)

        if tipo_dado == "limpo":
            self.dados_limpos()
        elif tipo_dado == "sujo":
            self.dados_sujos()
        else:
            self.dados_inesperados()
        await self.send(id_upa)

    async def send(self, id):
        data_hora = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        valores = [self.temperatura, self.umidade]
        unidades = [1, 2]  # Supondo: 1 = Celsius, 2 = Porcentagem (%)

        for valor, unidade in zip(valores, unidades):
            await self.client.send_message({
                "data_hora": data_hora,
                "valor": valor,
                "fk_sensor": 2,
                "fk_unid_medida": unidade,
                "fk_paciente": None,
                "fk_upa": id
            })


    def temperatura_ambiente(self):
        A = 1.009249522e-03
        B = 2.378405444e-04
        C = 2.019202697e-07

        R = random.uniform(8000, 12000)
        T_kelvin = 1 / (A + B * math.log(R) + C * (math.log(R))**3)
        return T_kelvin - 273.15
    

    def umidade_ambiente(self):
        V_sensor = random.uniform(1, 3)
        V_max = 3.3
        return (V_sensor / V_max) * 100


    def dados_limpos(self):
        self.temperatura = round(self.temperatura_ambiente(), 2)
        self.umidade = round(self.umidade_ambiente(), 2)


    def dados_sujos(self):
        numero = random.randrange(1, 50)
        if numero < 10:
            self.temperatura = None
            self.umidade = None
        elif numero > 10 and numero < 30:
            self.temperatura = round(random.uniform(45, 80), 2)
            self.umidade = round(random.uniform(60, 90), 2)
        else:
            self.temperatura = round(random.uniform(-10, 15), 2)
            self.umidade = round(random.uniform(-10, 20), 2)
    

    def dados_inesperados(self):
        spike = random.choice([10, -10, 15, -15])
        self.temperatura = round(self.temperatura_ambiente() + spike, 2)
        self.umidade = round(self.umidade_ambiente() + spike, 2)

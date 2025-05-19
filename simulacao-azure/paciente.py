from datetime import datetime, timedelta
from device_connect import Device
import random
import math
import os

from device_mock import DeviceLocal

class PacienteSensores:
    def __init__(self):
        self.client = None
        self.oxigenacao = None
        self.temperatura = None
        self.data = None

    async def config(self, connect_string):
        if os.getenv("ENVIROMENT") == "db":
            self.client = DeviceLocal()
            await self.client.connect()
        else:
            self.client = Device()
            await self.client.connect(connect_string) 


    async def handler(self, data_mockada=None):
        tipo_dado = random.choice(["limpo", "limpo", "limpo", "sujo", "sujo", "inesperado"])

        id_paciente = random.randrange(1, 3)
        id_upa = random.randrange(1, 3)

        if data_mockada != None:
            self.data = data_mockada
        else:
            self.data = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        if tipo_dado == "limpo":
            for _ in range(6):
                self.dados_limpos()
                await self.send(id_paciente, id_upa)
        elif tipo_dado == "sujo":
            for _ in range(6):
                self.dados_sujos()
                await self.send(id_paciente, id_upa)
        else:
            for _ in range(6):
                self.dados_inesperados()
                await self.send(id_paciente, id_upa)


    async def send(self, id_paciente, id_upa):
        # Envia 3 valores de oxigenação (unidade 2)
        self.data -= timedelta(seconds=5)
        await self.client.send_message({
            "data_hora": self.data,
            "valor": self.oxigenacao,
            "fk_upa": id_upa,
            "fk_paciente": id_paciente,
            "fk_sensor": 3,
            "fk_unid_medida": 2,  # %
        })

        # Envia 3 valores de temperatura (unidade 1)
        await self.client.send_message({
            "data_hora": self.data,
            "valor": self.temperatura,
            "fk_upa": id_upa,
            "fk_paciente": id_paciente,
            "fk_sensor": 4,
            "fk_unid_medida": 1,  # Celsius
        })


    def oximetro(self):
        V_sensor = random.uniform(1.6, 2.4)  
        SpO2 = 95 + (V_sensor - 2.0) * (5 / 0.4)
        return round(SpO2, 1)


    def temperatura_corporal(self):     
        A = 1.009249522e-03
        B = 2.378405444e-04
        C = 2.019202697e-07
        R_REF = 10000
        VCC = 3.3
        ADC_MAX = 1023 

        adc_value = random.randint(630, 650)  
        V_sensor = (adc_value / ADC_MAX) * VCC
        R_ntc = R_REF * ((VCC / V_sensor) - 1)

        T_kelvin = 1 / (A + B * math.log(R_ntc) + C * (math.log(R_ntc))**3)  # Equação de Steinhart-Hart
        T_celsius = T_kelvin - 273.15 # Convertendo para Celsius
        return round(T_celsius, 2)
    

    def dados_limpos(self):
        self.temperatura = self.temperatura_corporal()
        self.oxigenacao = self.oximetro()


    def dados_sujos(self):
        numero = random.randrange(1, 50)
        if numero < 10:
            self.oxigenacao = None
            self.temperatura = None
        elif numero > 10 and numero < 30:
            self.oxigenacao = round(random.uniform(50.0, 85.0), 2)
            self.temperatura = round(random.uniform(36.0, 37.5), 2)
        else:
            self.oxigenacao = round(random.uniform(95.0, 99.0), 2)
            self.temperatura = round(random.uniform(-0.1, 0.1), 2)
    

    def dados_inesperados(self):
        spike = random.choice([-10, -20, -15, 15, 20])
        self.oxigenacao = round(self.oximetro() + spike, 2)
        self.temperatura = round(self.temperatura_corporal() + spike, 2)

    async def disconnect(self):
        await self.client.shutdown()
from datetime import datetime
from device_connect import Device
from device_mock import DeviceLocal
import random
import math
import os

class DHT22:
    def __init__(self):
        self.client = None
        self.temperatura = None
        self.umidade = None
        self.data = None

    async def config(self, connect_string):
        if os.getenv("ENVIROMENT") == "db":
            self.client = DeviceLocal()
            await self.client.connect()
        else:
            self.client = Device()
            await self.client.connect(connect_string)    

    async def handler(self, data_mockada=None):
        tipo_dado = random.choice(["limpo", "limpo", "limpo", "limpo", "sujo", "inesperado"])
        id_upa = random.randrange(1, 3)

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
        valores = [self.temperatura, self.umidade]
        unidades = [1, 2]  # Supondo: 1 = Celsius, 2 = Porcentagem (%)

        for valor, unidade in zip(valores, unidades):
            await self.client.send_message({
                "data_hora": self.data,
                "valor": valor,
                "fk_upa": id,
                "fk_paciente": None,
                "fk_sensor": 2,
                "fk_unid_medida": unidade
            })


    def temperatura_ambiente(self):
        A = 1.009249522e-03
        B = 2.378405444e-04
        C = 2.019202697e-07

        R = random.uniform(8000, 12000)
        T_kelvin_base = 1 / (A + B * math.log(R) + C * (math.log(R))**3)
        temperatura_base_celsius = T_kelvin_base - 273.15
        temperatura_final_celsius = temperatura_base_celsius
        
        num_pessoas_no_ambiente = int(os.environ.get('QTD_PESSOAS'))
        if num_pessoas_no_ambiente >= 0:
            incremento_por_pessoa = 0.075 
            max_pessoas_para_efeito = 200 
            pessoas_efetivas = min(num_pessoas_no_ambiente, max_pessoas_para_efeito)
            aumento_temperatura = pessoas_efetivas * incremento_por_pessoa
            temperatura_final_celsius += aumento_temperatura
        return temperatura_final_celsius
    

    def umidade_ambiente(self):
        V_sensor_base = random.uniform(1.0, 2.8) 
        V_max = 3.3
        umidade_base = (V_sensor_base / V_max) * 100
        umidade_final = umidade_base

        num_pessoas_no_ambiente = int(os.environ.get('QTD_PESSOAS'))
        if num_pessoas_no_ambiente >= 0:
            incremento_por_pessoa_umidade = 0.18  
            max_pessoas_para_efeito_umidade = 200
            pessoas_efetivas = min(num_pessoas_no_ambiente, max_pessoas_para_efeito_umidade)
            aumento_umidade = pessoas_efetivas * incremento_por_pessoa_umidade
            umidade_final += aumento_umidade
        umidade_final = max(0.0, min(umidade_final, 99.0)) 
        return umidade_final


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
    
    async def disconnect(self):
        await self.client.shutdown()

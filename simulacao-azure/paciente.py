from datetime import datetime, timedelta
import json
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
        self.total_pacientes = 700
        self.historico_pacientes = [0]

        if os.getenv("ENVIROMENT") == "mock":
            self.client = DeviceLocal()
        else:
            self.client = Device()


    async def handler(self, data_mockada, id_upa, intervalo_pacientes):
        self.data = data_mockada

        id_paciente = random.randrange(intervalo_pacientes[0], intervalo_pacientes[1])
        while id_paciente == self.historico_pacientes[len(self.historico_pacientes)-1]:
            id_paciente = random.randrange(intervalo_pacientes[0], intervalo_pacientes[1])
        self.historico_pacientes.append(id_paciente)

        patient_reading_time = self.data

        with open("./biometrias_unicas.json", mode="r") as json_file:
            data = json_file.read()
            data = json.loads(data)
            biometria = data["biometrias"][id_paciente-1]
            await self.send_biometria(biometria, id_paciente, id_upa, patient_reading_time)

        # oximetro
        qtde_dados_limpos = random.randrange(3, 5) 
        for _ in range(qtde_dados_limpos):
            self.dados_limpos() 
            await self.send_oxigenacao(id_paciente, id_upa, patient_reading_time)
            patient_reading_time += timedelta(seconds=5) 
        
        for _ in range(6-qtde_dados_limpos):
            tipo_dado = random.choice(["sujo", "sujo", "sujo", "inesperado", "inesperado"])
            if tipo_dado == "sujo":
                self.dados_sujos()
            else:
                self.dados_inesperados()
            await self.send_oxigenacao(id_paciente, id_upa, patient_reading_time)
            patient_reading_time += timedelta(seconds=5) 

        # temperatura
        for _ in range(qtde_dados_limpos):
            self.dados_limpos()
            await self.send_temperatura(id_paciente, id_upa, patient_reading_time)
            patient_reading_time += timedelta(seconds=5) # Avança 5 segundos para a próxima leitura de temp
        
        for _ in range(6-qtde_dados_limpos):
            tipo_dado = random.choice(["sujo", "sujo", "sujo", "inesperado", "inesperado"])
            if tipo_dado == "sujo":
                self.dados_sujos()
            else:
                self.dados_inesperados()
            await self.send_temperatura(id_paciente, id_upa, patient_reading_time)
            patient_reading_time += timedelta(seconds=5) # Avança 5 segundos para a próxima leitura de temp


    async def send_oxigenacao(self, id_paciente, id_upa, current_timestamp):
        await self.client.send_message({
            "data_hora": current_timestamp,
            "valor": self.oxigenacao,
            "fk_upa": id_upa,
            "fk_paciente": id_paciente,
            "fk_sensor": 3,  # ID do sensor de Oximetria
            "fk_unid_medida": 2, # %
        })

    async def send_temperatura(self, id_paciente, id_upa, current_timestamp):
        await self.client.send_message({
            "data_hora": current_timestamp,
            "valor": self.temperatura,
            "fk_upa": id_upa,
            "fk_paciente": id_paciente,
            "fk_sensor": 4,  # ID do sensor de Temperatura
            "fk_unid_medida": 1, # Celsius
        })

    async def send_biometria(self, biometria, id_paciente, id_upa, current_timestamp):
        await self.client.send_message({
            "data_hora": current_timestamp,
            "valor": 0,
            "biometria": biometria,
            "fk_upa": id_upa,
            "fk_paciente": id_paciente,
            "fk_sensor": 5,  # ID do sensor de Temperatura
            "fk_unid_medida": None, 
        })


    async def handler_azure(self):
        tipo_dado = random.choice(["limpo", "limpo", "limpo", "sujo", "sujo", "inesperado"])

        last_paciente = 0
        id_paciente = random.randrange(1, self.total_pacientes)
        id_upa = random.randrange(1, 35)
        self.data = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        while id_paciente == last_paciente:
            id_paciente = random.randrange(1, self.total_pacientes)
        
        patient_reading_time = datetime.strptime(self.data, "%Y-%m-%dT%H:%M:%S")
        qtde_dados_limpos = random.randrange(3, 5) 

        with open("./biometrias_unicas.json", mode="r") as json_file:
            data = json_file.read()
            data = json.loads(data)
            biometria = data["biometrias"][id_paciente-1]
            await self.send_biometria(biometria, id_paciente, id_upa, patient_reading_time.strftime("%Y-%m-%dT%H:%M:%S"))

        for _ in range(qtde_dados_limpos):
            self.dados_limpos() 
            await self.send_oxigenacao(id_paciente, id_upa, patient_reading_time.strftime("%Y-%m-%dT%H:%M:%S"))
            patient_reading_time += timedelta(seconds=5) 
        
        for _ in range(6-qtde_dados_limpos):
            patient_reading_time
            tipo_dado = random.choice(["sujo", "sujo", "sujo", "inesperado", "inesperado"])
            if tipo_dado == "sujo":
                self.dados_sujos()
            else:
                self.dados_inesperados()
            await self.send_oxigenacao(id_paciente, id_upa, patient_reading_time.strftime("%Y-%m-%dT%H:%M:%S"))
            patient_reading_time += timedelta(seconds=5) 

        # temperatura
        for _ in range(qtde_dados_limpos):
            self.dados_limpos()
            await self.send_temperatura(id_paciente, id_upa, patient_reading_time.strftime("%Y-%m-%dT%H:%M:%S"))
            patient_reading_time += timedelta(seconds=5) # Avança 5 segundos para a próxima leitura de temp
        
        for _ in range(6-qtde_dados_limpos):
            tipo_dado = random.choice(["sujo", "sujo", "sujo", "inesperado", "inesperado"])
            if tipo_dado == "sujo":
                self.dados_sujos()
            else:
                self.dados_inesperados()
            await self.send_temperatura(id_paciente, id_upa, patient_reading_time.strftime("%Y-%m-%dT%H:%M:%S"))
            patient_reading_time += timedelta(seconds=5) # Avança 5 segundos para a próxima leitura de temp


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

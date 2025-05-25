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
        self.total_pacientes = 159

    async def config(self, connect_string):
        if os.getenv("ENVIROMENT") == "db":
            self.client = DeviceLocal()
            await self.client.connect()
        else:
            self.client = Device()
            await self.client.connect(connect_string) 


    async def handler(self, data_mockada=None):
        if data_mockada is not None:
            self.data = data_mockada
        else:
            # self.data = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            self.data = datetime.now()

        current_base_time = self.data

        total_intervalo_minutos_simulacao = (self.total_pacientes - 1) * 5
        # O paciente 1 terá seu tempo base recuado em total_intervalo_minutos_simulacao
        current_base_time_for_oldest_patient = self.data - timedelta(minutes=total_intervalo_minutos_simulacao)

        for id_paciente in range(1, self.total_pacientes + 1):
            id_upa = random.randrange(1, 35) 
 
            patient_reading_time = current_base_time_for_oldest_patient

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
            patient_reading_time_temp = current_base_time_for_oldest_patient
            for _ in range(qtde_dados_limpos):
                self.dados_limpos()
                await self.send_temperatura(id_paciente, id_upa, patient_reading_time_temp)
                patient_reading_time_temp += timedelta(seconds=5) # Avança 5 segundos para a próxima leitura de temp
            
            for _ in range(6-qtde_dados_limpos):
                tipo_dado = random.choice(["sujo", "sujo", "sujo", "inesperado", "inesperado"])
                if tipo_dado == "sujo":
                    self.dados_sujos()
                else:
                    self.dados_inesperados()
                await self.send_temperatura(id_paciente, id_upa, patient_reading_time_temp)
                patient_reading_time_temp += timedelta(seconds=5) # Avança 5 segundos para a próxima leitura de temp


            # Após processar as 6 leituras de um paciente,
            # avança o tempo base em 5 minutos para o próximo paciente (mais recente)
            current_base_time_for_oldest_patient += timedelta(minutes=5)


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
from datetime import datetime
from device_connect import Device
from device_mock import DeviceLocal
import random
import os


class VisaoComputacional:
    def __init__(self):
        self.client = None
        self.quantidade_pessoas = 0
        self.data = None
        self.historico_quantidade_pessoas = [0] * 5 # Média das últimas 5 leituras

        if os.getenv("ENVIROMENT") == "mock":
            self.client = DeviceLocal()
        else:
            self.client = Device()

    async def handler(self, data_mockada=None, id_upa=None, intervalo_pacientes=None):
        tipo_dado = random.choice(["limpo", "limpo", "limpo", "limpo", "sujo", "inesperado"])

        if id_upa is None:
            id_upa = random.randrange(1, 35)

        if data_mockada != None:
            self.data = data_mockada
        else:
            self.data = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        self.quantidade_pessoas = self._gerar_quantidade_pessoas_suave()

        if tipo_dado == "limpo":
            self.dados_limpos()
        elif tipo_dado == "sujo":
            self.dados_sujos()
        else:
            self.dados_inesperados()
        await self.send(id_upa)


    def _gerar_quantidade_pessoas_suave(self):
        if isinstance(self.data, datetime):
            data_obj = self.data
        else:
            data_obj = datetime.strptime(self.data, "%Y-%m-%dT%H:%M:%S")
            
        hora_atual = data_obj.hour

        if 0 <= hora_atual < 6: # Madrugada
            valor_alvo = random.randint(5, 15)
        elif 6 <= hora_atual < 9: # Manhã cedo
            valor_alvo = random.randint(15, 30)
        elif 9 <= hora_atual < 12: # Meio da manhã
            valor_alvo = random.randint(25, 45)
        elif 12 <= hora_atual < 15: # Almoço/Início da tarde (pico)
            valor_alvo = random.randint(40, 70)
        elif 15 <= hora_atual < 18: # Meio da tarde
            valor_alvo = random.randint(30, 55)
        elif 18 <= hora_atual < 21: # Noite (segundo pico)
            valor_alvo = random.randint(35, 60)
        else: # Fim da noite
            valor_alvo = random.randint(15, 35)

        # Pega a última quantidade de pessoas do histórico para suavizar a transição
        ultima_quantidade = self.historico_quantidade_pessoas[-1]

        # Calcula a diferença entre o alvo e o valor atual
        diferenca = valor_alvo - ultima_quantidade

        fator_suavizacao = 0.2 # Quanto mais alto, mais rápido a mudança

        nova_quantidade = ultima_quantidade + (diferenca * fator_suavizacao) + random.uniform(-2, 2)

        nova_quantidade = max(0, int(round(nova_quantidade))) # int e não negativo

        # Atualiza o histórico
        self.historico_quantidade_pessoas.append(nova_quantidade)
        if len(self.historico_quantidade_pessoas) > 5: # Mantém o histórico pequeno
            self.historico_quantidade_pessoas.pop(0)

        return nova_quantidade

    async def send(self, id):       
        await self.client.send_message({
            "data_hora": self.data,
            "valor": self.quantidade_pessoas,
            "fk_upa": id,
            "fk_paciente": None,
            "fk_sensor": 1,
            "fk_unid_medida": None,
        })


    def gerar_quantidade_pessoas(self):
        valor = int(random.gauss(50, 30))
        return max(0, valor)


    def dados_limpos(self):
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
        self.quantidade_pessoas = round(self.gerar_quantidade_pessoas() + spike, 2)

from datetime import timedelta, datetime
import random
import os

class MockDados:
   async  def gerar_massa(self, dispositivo):
        intervalo_dias = int(os.getenv("INTERVALO_DIAS"))
        data_geracao = os.getenv("DATA_GERACAO").split("-")
        ano, mes, dia = int(data_geracao[0]), int(data_geracao[1]), int(data_geracao[2])

        for i in range(intervalo_dias, 0, -1):
            for j in range(23, 0, -1):
                for k in range(60, 0, -5):
                    numero_aleatorio = random.randint(1, 50)
                    data_alterada = datetime(ano, mes, dia, 22, 00, 00) - timedelta(days=i, hours=j, minutes=k, seconds=numero_aleatorio)
                    await dispositivo.handler(data_alterada)
                    
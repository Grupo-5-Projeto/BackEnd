from datetime import timedelta, datetime
import os
import random

class MockDados:
    async def gerar_massa(self, dispositivo):
        
        print(f"Gerando massa para {type(dispositivo)}")
        intervalo_pacientes = [0, 1]
        for upa_id in range(1, 6):
            intervalo_dias = int(os.getenv("INTERVALO_DIAS"))
            data_inicio_str = os.getenv("DATA_GERACAO")
            data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
            data_fim = data_inicio + timedelta(days=intervalo_dias)
            horario_atual = data_inicio

            intervalo_pacientes[0] = intervalo_pacientes[1]
            intervalo_pacientes[1] += 140

            while horario_atual < data_fim:
                await dispositivo.handler(horario_atual.replace(second=0), id_upa=upa_id, intervalo_pacientes=intervalo_pacientes)
                horario_atual += timedelta(minutes=5)

        # gerando dados para upas aleatorias de 6 a 35
        intervalo_dias = int(os.getenv("INTERVALO_DIAS"))
        data_inicio_str = os.getenv("DATA_GERACAO")
        data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
        data_fim = data_inicio + timedelta(days=intervalo_dias)

        horario_atual = data_inicio

        while horario_atual < data_fim:
            for upa_id in range(6, 35):  # De 1 até 34 inclusive
                await dispositivo.handler(horario_atual.replace(second=0), id_upa=upa_id, intervalo_pacientes=[1, 700])
            horario_atual += timedelta(minutes=5)
        print(f"Geração de massa finalizada para {type(dispositivo)}")
        

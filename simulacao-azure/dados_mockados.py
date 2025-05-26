from datetime import timedelta, datetime
import os

class MockDados:
    async def gerar_massa(self, dispositivo):
        print(f"Gerando massa para {type(dispositivo)}")
        intervalo_dias = int(os.getenv("INTERVALO_DIAS"))
        data_inicio_str = os.getenv("DATA_GERACAO")
        data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
        data_fim = data_inicio + timedelta(days=intervalo_dias)

        horario_atual = data_inicio

        while horario_atual < data_fim:
            for upa_id in range(1, 35):  # De 1 até 34 inclusive
                await dispositivo.handler(horario_atual.replace(second=0), id_upa=upa_id)
            horario_atual += timedelta(minutes=5)
        print(f"Geração de massa finalizada para {type(dispositivo)}")
        

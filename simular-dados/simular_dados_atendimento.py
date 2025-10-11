import random
import statistics
from datetime import datetime, timedelta

class Pessoa:
    def __init__(self, id_atendimento, chegada, fk_upa):
        self.id_atendimento = id_atendimento
        self.FK_UPA = fk_upa
        self.FK_PESSOA = random.randint(1, 700)
        self.tempo_chegada = chegada
        self.sala_espera_1_inicio = chegada
        self.sala_espera_1_fim = None
        self.sala_espera_2_inicio = None
        self.sala_espera_2_fim = None
        self.sala_triagem = None
        self.sala_consultorio = None
        self.tempo_triagem_inicio = None
        self.tempo_triagem_fim = None
        self.tempo_atendimento_inicio = None
        self.tempo_atendimento_fim = None
        self.tempo_saida = None
        self.TEMPERATURA_PACIENTE = None
        self.OXIMETRIA_PACIENTE = None

def gerar_temperatura():
    chance = random.random()
    if chance < 0.05:
        return round(random.uniform(34.0, 35.9), 1)
    elif chance < 0.90:
        return round(random.uniform(36.0, 37.4), 1)
    else:
        return round(random.uniform(37.5, 40.0), 1)

def gerar_oximetria():
    chance = random.random()
    if chance < 0.05:
        return random.randint(85, 93)
    elif chance < 0.95:
        return random.randint(94, 100)
    else:
        return random.randint(101, 103)

def minutos_para_hora(base, minutos):
    return (base + timedelta(minutes=minutos)).strftime("%H:%M")

def simular_fluxo(qtd_pessoas=20, fk_upa=1):
    pessoas = []
    triagem_livre = [0, 0]
    consultorio_livre = [0, 0, 0, 0, 0]
    tempo_atual = 0

    for i in range(qtd_pessoas):
        chegada = tempo_atual + random.randint(1, 3)
        p = Pessoa(i + 1, chegada, fk_upa)

        p.TEMPERATURA_PACIENTE = gerar_temperatura()
        p.OXIMETRIA_PACIENTE = gerar_oximetria()

        p.sala_espera_1_inicio = chegada
        idx_triagem = triagem_livre.index(min(triagem_livre))
        inicio_triagem = max(chegada, triagem_livre[idx_triagem])
        p.sala_espera_1_fim = inicio_triagem
        p.sala_triagem = f"TRIAGEM_{idx_triagem + 1}"

        duracao_triagem = random.randint(3, 6)
        fim_triagem = inicio_triagem + duracao_triagem
        triagem_livre[idx_triagem] = fim_triagem

        p.tempo_triagem_inicio = inicio_triagem
        p.tempo_triagem_fim = fim_triagem

        p.sala_espera_2_inicio = fim_triagem
        idx_consultorio = consultorio_livre.index(min(consultorio_livre))
        inicio_atendimento = max(fim_triagem, consultorio_livre[idx_consultorio])
        p.sala_espera_2_fim = inicio_atendimento
        p.sala_consultorio = f"CONSULTORIO_{idx_consultorio + 1}"

        duracao_atendimento = random.randint(8, 15)
        fim_atendimento = inicio_atendimento + duracao_atendimento
        consultorio_livre[idx_consultorio] = fim_atendimento

        p.tempo_atendimento_inicio = inicio_atendimento
        p.tempo_atendimento_fim = fim_atendimento
        p.tempo_saida = fim_atendimento

        pessoas.append(p)
        tempo_atual = chegada

    return pessoas

def estatisticas(pessoas):
    tempos_espera_triagem = [p.tempo_triagem_inicio - p.tempo_chegada for p in pessoas]
    tempos_triagem = [p.tempo_triagem_fim - p.tempo_triagem_inicio for p in pessoas]
    tempos_espera_atendimento = [p.tempo_atendimento_inicio - p.tempo_triagem_fim for p in pessoas]
    tempos_atendimento = [p.tempo_atendimento_fim - p.tempo_atendimento_inicio for p in pessoas]
    tempos_totais = [p.tempo_saida - p.tempo_chegada for p in pessoas]

    print(f"Média espera triagem: {statistics.mean(tempos_espera_triagem):.2f} min")
    print(f"Média duração triagem: {statistics.mean(tempos_triagem):.2f} min")
    print(f"Média espera atendimento: {statistics.mean(tempos_espera_atendimento):.2f} min")
    print(f"Média duração atendimento: {statistics.mean(tempos_atendimento):.2f} min")
    print(f"Média tempo total no fluxo: {statistics.mean(tempos_totais):.2f} min")

def simular_varias_upas(qtd_upas=3, pessoas_por_upa=10):
    base_horario = datetime.strptime("08:00", "%H:%M")
    for fk_upa in range(1, qtd_upas + 1):
        print(f"\n{'='*20}\nUPA {fk_upa}\n{'='*20}")
        pessoas = simular_fluxo(pessoas_por_upa, fk_upa)
        estatisticas(pessoas)
        for p in pessoas:
            print(f"\nID_ATENDIMENTO: {p.id_atendimento}")
            print(f"FK_PESSOA: {p.FK_PESSOA}")
            print(f"chegou: {minutos_para_hora(base_horario, p.sala_espera_1_inicio)} min")
            print(f"{p.sala_triagem}: {minutos_para_hora(base_horario, p.tempo_triagem_inicio)} min")
            print(f"SALA_DE_ESPERA: {minutos_para_hora(base_horario, p.sala_espera_2_inicio)} min")
            print(f"{p.sala_consultorio}: {minutos_para_hora(base_horario, p.tempo_atendimento_inicio)} min")
            print(f"Saida: {minutos_para_hora(base_horario, p.tempo_saida)} min")
            print(f"TEMPERATURA_PACIENTE: {p.TEMPERATURA_PACIENTE} °C")
            print(f"OXIMETRIA_PACIENTE: {p.OXIMETRIA_PACIENTE}%")
            print(f"FK_UPA = {p.FK_UPA}")

# Exemplo de uso
simular_varias_upas(qtd_upas=2, pessoas_por_upa=5)

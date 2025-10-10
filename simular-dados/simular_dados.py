import random
import statistics
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('pt_BR')

class Pessoa:
    def __init__(self, id_paciente, chegada):
        self.id_paciente = id_paciente
        self.nome = fake.name()
        self.cpf = fake.cpf()
        self.data_nascimento = fake.date_of_birth(minimum_age=18, maximum_age=90)
        self.biometria = fake.uuid4()
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

def minutos_para_hora(base, minutos):
    return (base + timedelta(minutes=minutos)).strftime("%H:%M")

def simular_fluxo(qtd_pessoas=20):
    pessoas = []
    triagem_livre = [0, 0]  # TRIAGEM-1, TRIAGEM-2
    consultorio_livre = [0, 0, 0, 0, 0]  # CONSULTORIO-1 a CONSULTORIO-5
    tempo_atual = 0

    for i in range(qtd_pessoas):
        chegada = tempo_atual + random.randint(1, 3)
        p = Pessoa(i + 1, chegada)

        # --- SALA-DE-ESPERA-1 ---
        p.sala_espera_1_inicio = chegada
        idx_triagem = triagem_livre.index(min(triagem_livre))
        inicio_triagem = max(chegada, triagem_livre[idx_triagem])
        p.sala_espera_1_fim = inicio_triagem
        p.sala_triagem = f"TRIAGEM-{idx_triagem + 1}"

        # --- TRIAGEM ---
        duracao_triagem = random.randint(3, 6)
        fim_triagem = inicio_triagem + duracao_triagem
        triagem_livre[idx_triagem] = fim_triagem

        p.tempo_triagem_inicio = inicio_triagem
        p.tempo_triagem_fim = fim_triagem

        # --- SALA-DE-ESPERA-2 ---
        p.sala_espera_2_inicio = fim_triagem
        idx_consultorio = consultorio_livre.index(min(consultorio_livre))
        inicio_atendimento = max(fim_triagem, consultorio_livre[idx_consultorio])
        p.sala_espera_2_fim = inicio_atendimento
        p.sala_consultorio = f"CONSULTORIO-{idx_consultorio + 1}"

        # --- CONSULTORIO ---
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

# --- Execução da simulação ---
base_horario = datetime.strptime("08:00", "%H:%M")
pessoas = simular_fluxo(10)
estatisticas(pessoas)

# --- Exemplo de saída detalhada ---
for p in pessoas:
    print(f"\nID: {p.id_paciente}")
    print(f"Nome: {p.nome}")
    print(f"CPF: {p.cpf}")
    print(f"Data Nascimento: {p.data_nascimento}")
    print(f"Biometria: {p.biometria}")
    print(f"SALA-DE-ESPERA-1: {minutos_para_hora(base_horario, p.sala_espera_1_inicio)} -> {minutos_para_hora(base_horario, p.sala_espera_1_fim)}")
    print(f"{p.sala_triagem}: {minutos_para_hora(base_horario, p.tempo_triagem_inicio)} -> {minutos_para_hora(base_horario, p.tempo_triagem_fim)}")
    print(f"SALA-DE-ESPERA-2: {minutos_para_hora(base_horario, p.sala_espera_2_inicio)} -> {minutos_para_hora(base_horario, p.sala_espera_2_fim)}")
    print(f"{p.sala_consultorio}: {minutos_para_hora(base_horario, p.tempo_atendimento_inicio)} -> {minutos_para_hora(base_horario, p.tempo_atendimento_fim)}")
    print(f"Saída: {minutos_para_hora(base_horario, p.tempo_saida)}")

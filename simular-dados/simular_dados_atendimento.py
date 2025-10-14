import random
import statistics
import csv
from datetime import datetime, timedelta
import copy

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
        self.DATA = datetime.today().strftime("%Y-%m-%d")

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

def minutos_para_hora_completa(base, minutos):
    return (base + timedelta(minutes=minutos)).strftime("%H:%M:%S")

def simular_fluxo(qtd_pessoas=20, fk_upa=1, id_inicial=1):
    pessoas = []
    triagem_livre = [0, 0]
    consultorio_livre = [0, 0, 0, 0, 0]
    tempo_atual = 0

    for i in range(qtd_pessoas):
        chegada = tempo_atual + random.randint(1, 5)
        p = Pessoa(id_inicial + i, chegada, fk_upa)

        p.TEMPERATURA_PACIENTE = gerar_temperatura()
        p.OXIMETRIA_PACIENTE = gerar_oximetria()

        p.sala_espera_1_inicio = chegada
        idx_triagem = triagem_livre.index(min(triagem_livre))
        inicio_triagem = max(chegada, triagem_livre[idx_triagem])
        p.sala_espera_1_fim = inicio_triagem
        p.sala_triagem = f"TRIAGEM_{idx_triagem + 1}"

        duracao_triagem = random.randint(5, 15)
        fim_triagem = inicio_triagem + duracao_triagem
        triagem_livre[idx_triagem] = fim_triagem

        p.tempo_triagem_inicio = inicio_triagem
        p.tempo_triagem_fim = fim_triagem

        p.sala_espera_2_inicio = fim_triagem
        idx_consultorio = consultorio_livre.index(min(consultorio_livre))
        inicio_atendimento = max(fim_triagem, consultorio_livre[idx_consultorio])
        p.sala_espera_2_fim = inicio_atendimento
        p.sala_consultorio = f"CONSULTORIO_{idx_consultorio + 1}"

        duracao_atendimento = random.randint(15, 30)
        fim_atendimento = inicio_atendimento + duracao_atendimento
        consultorio_livre[idx_consultorio] = fim_atendimento

        p.tempo_atendimento_inicio = inicio_atendimento
        p.tempo_atendimento_fim = fim_atendimento
        p.tempo_saida = fim_atendimento

        pessoas.append(p)
        tempo_atual = chegada

    return pessoas, id_inicial + qtd_pessoas

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

def sujar_dados(linhas, percentual=0.1):
    total = len(linhas)
    qtd_sujos = int(total * percentual)
    linhas_sujas = copy.deepcopy(linhas)
    campos = list(linhas[0].keys())

    for i in random.sample(range(total), qtd_sujos):
        campo = random.choice(campos)
        valor = linhas_sujas[i][campo]

        if campo in ["TEMPERATURA_PACIENTE", "OXIMETRIA_PACIENTE", "FK_PESSOA", "FK_UPA"]:
            if random.random() < 0.5:
                linhas_sujas[i][campo] = None
            else:
                linhas_sujas[i][campo] = 999999
        elif campo in ["TRIAGEM_SALA", "CONSULTORIO_SALA"]:
            if random.random() < 0.5:
                linhas_sujas[i][campo] = None
            else:
                linhas_sujas[i][campo] = valor.lower() if random.random() < 0.5 else valor.upper()
        elif campo in ["chegou", "TRIAGEM_HORARIO", "SALA_DE_ESPERA", "CONSULTORIO_HORARIO", "Saida"]:
            linhas_sujas[i][campo] = None
        elif campo == "DATA":
            if random.random() < 0.5:
                linhas_sujas[i][campo] = None
            else:
                linhas_sujas[i][campo] = linhas_sujas[i][campo].lower()

    return linhas_sujas

def simular_varias_upas(qtd_upas=3):
    base_horario = datetime.strptime("08:00:00", "%H:%M:%S")
    data_hoje = datetime.today().strftime("%Y-%m-%d")
    nome_limpo = f"ATENDIMENTOS_LIMPOS_{data_hoje}.csv"
    nome_sujo = f"ATENDIMENTOS_SUJOS_{data_hoje}.csv"

    campos_csv = [
        "ID_ATENDIMENTO",
        "FK_PESSOA",
        "DATA",
        "chegou",
        "TRIAGEM_HORARIO",
        "TRIAGEM_SALA",
        "SALA_DE_ESPERA",
        "CONSULTORIO_HORARIO",
        "CONSULTORIO_SALA",
        "Saida",
        "TEMPERATURA_PACIENTE",
        "OXIMETRIA_PACIENTE",
        "FK_UPA"
    ]

    id_atendimento_global = 1
    todas_linhas = []

    for fk_upa in range(1, qtd_upas + 1):
        pessoas_por_upa = random.randint(25, 70)
        print(f"\n{'='*20}\nUPA {fk_upa} - {pessoas_por_upa} atendimentos\n{'='*20}")
        pessoas, id_atendimento_global = simular_fluxo(pessoas_por_upa, fk_upa, id_atendimento_global)
        estatisticas(pessoas)

        for p in pessoas:
            dados_linha = {
                "ID_ATENDIMENTO": p.id_atendimento,
                "FK_PESSOA": p.FK_PESSOA,
                "DATA": p.DATA,
                "chegou": minutos_para_hora_completa(base_horario, p.sala_espera_1_inicio),
                "TRIAGEM_HORARIO": minutos_para_hora_completa(base_horario, p.tempo_triagem_inicio),
                "TRIAGEM_SALA": p.sala_triagem,
                "SALA_DE_ESPERA": minutos_para_hora_completa(base_horario, p.sala_espera_2_inicio),
                "CONSULTORIO_HORARIO": minutos_para_hora_completa(base_horario, p.tempo_atendimento_inicio),
                "CONSULTORIO_SALA": p.sala_consultorio,
                "Saida": minutos_para_hora_completa(base_horario, p.tempo_saida),
                "TEMPERATURA_PACIENTE": p.TEMPERATURA_PACIENTE,
                "OXIMETRIA_PACIENTE": p.OXIMETRIA_PACIENTE,
                "FK_UPA": p.FK_UPA
            }
            todas_linhas.append(dados_linha)

    sujas = sujar_dados(todas_linhas)

    with open(nome_limpo, 'w', newline='', encoding='utf-8') as arq:
        escritor = csv.DictWriter(arq, fieldnames=campos_csv)
        escritor.writeheader()
        escritor.writerows(todas_linhas)

    with open(nome_sujo, 'w', newline='', encoding='utf-8') as arq:
        escritor = csv.DictWriter(arq, fieldnames=campos_csv)
        escritor.writeheader()
        escritor.writerows(sujas)

    print(f"\nArquivos gerados:\n- {nome_limpo}\n- {nome_sujo}")

# Executa a simulação
simular_varias_upas(qtd_upas=34)

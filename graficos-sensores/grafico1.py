import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pymysql
from datetime import datetime, timedelta
import matplotlib.dates as mdates

DB_CONFIG = {
    'host': 'localhost', 
    'user': 'root',  
    'password': 'Urubu100', 
    'database': 'upa_connect'
}

horarios = pd.date_range("2025-04-14 20:00", periods=12, freq="H").strftime("%H:%M")
def buscar_temperaturas_banco(fk_upa=1, data='2025-04-14'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        query = f"""
            SELECT DATE_FORMAT(data_hora, '%H:%i') AS hora, valor
            FROM temperatura_ambiente
            WHERE DATE(data_hora) = '{data}' AND fk_upa = {fk_upa}
            ORDER BY data_hora;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        horarios = [linha[0] for linha in resultados]
        temperaturas = [float(linha[1]) for linha in resultados]
        return horarios, temperaturas
    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
        return [], []
    finally:
        if 'conexao' in locals():
            conexao.close()

def buscar_umidades_banco(fk_upa=1, data='2025-04-14'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        query = f"""
            SELECT DATE_FORMAT(data_hora, '%H:%i') AS hora, valor
            FROM umidade
            WHERE DATE(data_hora) = '{data}' AND fk_upa = {fk_upa}
            ORDER BY data_hora;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        horarios = [linha[0] for linha in resultados]
        umidades = [float(linha[1]) for linha in resultados]
        return horarios, umidades
    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
        return [], []
    finally:
        if 'conexao' in locals():
            conexao.close()

np.random.seed(0)

def grafico_1():
    data_escolhida = input("Digite a data que deseja visualizar (formato YYYY-MM-DD): ")

    horarios_db_temp, temperaturas_db = buscar_temperaturas_banco(data=data_escolhida)
    horarios_db_umi, umidades_db = buscar_umidades_banco(data=data_escolhida)

    if not horarios_db_temp and not horarios_db_umi:
        print(f"Nenhum dado encontrado para o dia {data_escolhida}.")
        return

    horarios_temp_dt = [datetime.strptime(f"{data_escolhida} {h}", "%Y-%m-%d %H:%M") for h in horarios_db_temp]
    horarios_umi_dt = [datetime.strptime(f"{data_escolhida} {h}", "%Y-%m-%d %H:%M") for h in horarios_db_umi]

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    if horarios_temp_dt:
        ax1.plot(horarios_temp_dt, temperaturas_db, 'r-', label='Temperatura (°C)')
    if horarios_umi_dt:
        ax2.plot(horarios_umi_dt, umidades_db, 'b--', label='Umidade (%)')  

    ax1.set_xlabel('Horário do Dia')
    ax1.set_ylabel('Temperatura (°C)', color='r')
    ax2.set_ylabel('Umidade (%)', color='b')
    plt.title(f"Variação de Temperatura e Umidade em {data_escolhida}")

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    fig.autofmt_xdate(rotation=45)
    plt.tight_layout()
    plt.show()

menu = {
    "1": grafico_1
}

if __name__ == "__main__":
    while True:
        print("\nMenu de Gráficos - Sistema de Monitoramento Inteligente das Filas nas UPAs")
        print("1. Ver gráfico de Temperatura e Umidade por dia escolhido")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "0":
            print("Saindo...")
            break
        elif opcao in menu:
            menu[opcao]()
        else:
            print("Opção inválida. Tente novamente.")

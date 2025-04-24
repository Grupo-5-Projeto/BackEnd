import matplotlib.pyplot as plt
import pandas as pd
import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost', 
    'user': 'root',  
    'password': 'Urubu100', 
    'database': 'upa_connect'
}

def buscar_temperaturas_banco(fk_upa=1, data='2025-04-14'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        query = f"""
            SELECT HOUR(data_hora) AS hora, AVG(valor) AS media_temp
            FROM temperatura_ambiente
            WHERE DATE(data_hora) = '{data}' AND fk_upa = {fk_upa}
            GROUP BY HOUR(data_hora)
            ORDER BY hora;
        """
        df = pd.read_sql(query, conexao)
        return df
    except Exception as e:
        print("Erro ao buscar temperaturas:", e)
        return pd.DataFrame()
    finally:
        if 'conexao' in locals():
            conexao.close()

def buscar_ocupacao(fk_upa=1, data='2025-04-14'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        query = f"""
            SELECT HOUR(data_hora) AS hora, AVG(qtd_pessoas) AS media_ocup
            FROM camera_computacional
            WHERE DATE(data_hora) = '{data}' AND fk_upa = {fk_upa}
            GROUP BY HOUR(data_hora)
            ORDER BY hora;
        """
        df = pd.read_sql(query, conexao)
        return df
    except Exception as e:
        print("Erro ao buscar ocupação:", e)
        return pd.DataFrame()
    finally:
        if 'conexao' in locals():
            conexao.close()

def grafico_2():
    data_escolhida = input("Digite a data que deseja visualizar (formato YYYY-MM-DD): ")

    df_temp = buscar_temperaturas_banco(data=data_escolhida)
    df_ocup = buscar_ocupacao(data=data_escolhida)

    if df_temp.empty and df_ocup.empty:
        print(f"Nenhum dado encontrado para o dia {data_escolhida}.")
        return

    df_merged = pd.merge(df_ocup, df_temp, on='hora', how='outer').sort_values('hora')
    df_merged = df_merged.fillna(0) 

    horas = df_merged['hora']
    ocupacoes = df_merged['media_ocup']
    temperaturas = df_merged['media_temp']

    fig, ax1 = plt.subplots(figsize=(10, 6))

    ax1.bar(horas, ocupacoes, color='skyblue', alpha=0.7)
    ax1.set_ylabel('Ocupação', color='blue')
    ax1.set_xlabel('Hora do Dia')
    ax1.set_xticks(range(0, 24))
    ax1.set_xticklabels([str(h) for h in range(0, 24)])

    ax2 = ax1.twinx()
    ax2.plot(horas, temperaturas, color='red')
    ax2.set_ylabel('Temperatura (°C)', color='red')

    plt.title('Ocupação da Sala vs Temperatura')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

menu = {
    "1": grafico_2,
}

if __name__ == "__main__":
    while True:
        print("\nMenu de Gráficos - Sistema de Monitoramento Inteligente das Filas nas UPAs")
        print("1. Ocupação vs Temperatura Ambiente")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "0":
            print("Saindo...")
            break
        elif opcao in menu:
            menu[opcao]()
        else:
            print("Opção inválida. Tente novamente.")

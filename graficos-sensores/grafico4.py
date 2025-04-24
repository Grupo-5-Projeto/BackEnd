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

def grafico_4():
    conn = pymysql.connect(**DB_CONFIG)
    
    try:
        query = """
        SELECT 
            DAYOFWEEK(data_hora) AS dia_numero,
            DAYNAME(data_hora) AS dia_semana,
            SUM(qtd_pessoas) AS total_atendimentos
        FROM camera_computacional
        GROUP BY dia_numero, dia_semana
        ORDER BY dia_numero;
        """
        
        df = pd.read_sql(query, conn)
        
        traducao_dias = {
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        df['dia_semana'] = df['dia_semana'].map(traducao_dias)

        dias_semana = df['dia_semana']
        atendimentos = df['total_atendimentos']
        
        plt.figure(figsize=(10, 6))
        plt.bar(dias_semana, atendimentos, color='skyblue')
        plt.xlabel("Dias da Semana")
        plt.ylabel("Número de Atendimentos")
        plt.title("Tendência Diária de Atendimentos ao Longo da Semana")
        plt.tight_layout()
        plt.show()
    
    except Exception as e:
        print(f"Erro ao gerar gráfico: {e}")
    finally:
        conn.close()

menu = {
    "1": grafico_4
}

if __name__ == "__main__":
    while True:
        print("\nMenu de Gráficos - Sistema de Monitoramento Inteligente das Filas nas UPAs")
        print("1. Tendência Diária de Atendimentos ao Longo da Semana")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")
        if opcao == "0":
            break
        elif opcao in menu:
            menu[opcao]()
        else:
            print("Opção inválida. Tente novamente.")

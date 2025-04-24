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

def buscar_temperaturas_corpo(fk_paciente=1, data='2025-04-17'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        query = f"""
            SELECT DATE_FORMAT(data_hora, '%H:%i') AS hora, valor
            FROM temperatura_paciente
            WHERE DATE(data_hora) = '{data}' AND fk_paciente = {fk_paciente}
            ORDER BY data_hora;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        horarios = [linha[0] for linha in resultados]
        temperaturas_corpo = [float(linha[1]) for linha in resultados]
        return horarios, temperaturas_corpo
    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
        return [], []
    finally:
        if 'conexao' in locals():
            conexao.close()

def buscar_oximetrias_corpo(fk_paciente=1, data='2025-04-17'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        query = f"""
            SELECT DATE_FORMAT(data_hora, '%H:%i') AS hora, valor
            FROM oximetro
            WHERE DATE(data_hora) = '{data}' AND fk_paciente = {fk_paciente}
            ORDER BY data_hora;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        horarios = [linha[0] for linha in resultados]
        oximetrias_corpo = [float(linha[1]) for linha in resultados]
        return horarios, oximetrias_corpo
    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
        return [], []
    finally:
        if 'conexao' in locals():
            conexao.close()

def verificar_pacientes_com_febre_ou_oximetria_grave(data='2025-04-17'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        
        query_pacientes = "SELECT id_paciente, nome FROM paciente"
        cursor.execute(query_pacientes)
        pacientes = cursor.fetchall()

        for paciente in pacientes:
            id_paciente = paciente[0]
            nome_paciente = paciente[1]
            
            horarios_temp, temperaturas_corpo_db = buscar_temperaturas_corpo(fk_paciente=id_paciente, data=data)
            horarios_oxi, oximetrias_corpo_db = buscar_oximetrias_corpo(fk_paciente=id_paciente, data=data)
            
            for t, o in zip(temperaturas_corpo_db, oximetrias_corpo_db):
                if t > 37.8 or o < 92:
                    print(f"Paciente com febre ou oximetria grave: {nome_paciente}")
                    break

    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
    finally:
        if 'conexao' in locals():
            conexao.close()

def grafico_3():
    horarios_temp, temperaturas_corpo_db = buscar_temperaturas_corpo()
    horarios_oxi, oximetrias_corpo_db = buscar_oximetrias_corpo()

    temp_dict = dict(zip(horarios_temp, temperaturas_corpo_db))
    oxi_dict = dict(zip(horarios_oxi, oximetrias_corpo_db))

    horarios_comuns = set(temp_dict.keys()) & set(oxi_dict.keys())

    fig, ax = plt.subplots()
    for hora in sorted(horarios_comuns):
        t = temp_dict[hora]
        o = oxi_dict[hora]
        color = 'red' if t > 37.8 and o < 92 else 'blue'
        ax.scatter(t, o, color=color, label=hora)

    ax.set_xlabel('Temperatura Corporal (°C)')
    ax.set_ylabel('Oximetria (%)')
    plt.title("Análise do Perfil dos Pacientes com Febre e Baixa Oximetria")
    plt.tight_layout()
    plt.show()

menu = {
    "1": grafico_3,
    "2": verificar_pacientes_com_febre_ou_oximetria_grave,  
}

if __name__ == "__main__":
    while True:
        print("\nMenu de Gráficos - Sistema de Monitoramento Inteligente das Filas nas UPAs")
        print("1. Perfil com Febre e Baixa Oximetria")
        print("2. Verificar Pacientes com Febre ou Oximetria Grave")  
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "0":
            print("Saindo...")
            break
        elif opcao in menu:
            menu[opcao]()
        else:
            print("Opção inválida. Tente novamente.")

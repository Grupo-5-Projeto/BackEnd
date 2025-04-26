import matplotlib.pyplot as plt
import pymysql
import pandas as pd

DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin_upa_connect',
    'password': 'urubu100',
    'database': 'upa_connect'
}

def buscar_temperaturas_por_mes():
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        query = """
            SELECT 
                MONTH(tp.data_hora) AS mes,
                AVG(tp.valor) AS media_temperatura
            FROM temperatura_paciente tp
            JOIN paciente p ON tp.fk_paciente = p.id_paciente
            GROUP BY mes
            ORDER BY mes;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        meses = [linha[0] for linha in resultados]
        temperaturas = [float(linha[1]) for linha in resultados]
        return meses, temperaturas
    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
        return [], []
    finally:
        if 'conexao' in locals():
            conexao.close()

def grafico_temperatura_meses():
    meses, temperaturas = buscar_temperaturas_por_mes()

    nomes_meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                   'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    meses_nomeados = [nomes_meses[m - 1] for m in meses]

    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    ax.plot(meses_nomeados, temperaturas, marker='o', linestyle='-', color='blue')

    ax.set_xlabel('Mês', fontsize=12)
    ax.set_ylabel('Temperatura Média (°C)', fontsize=12)
    ax.set_title(f"Temperatura Média Mensal dos Pacientes - Todas as UPAs", fontsize=14)
    ax.grid(True)
    plt.tight_layout()
    plt.show()

menu = {
    "1": lambda: grafico_temperatura_meses(),
}

if __name__ == "__main__":
    while True:
        print("\nMenu de Gráficos - Sistema de Monitoramento Inteligente das Filas nas UPAs")
        print("1. Temperatura Média por Mês (Todas as UPAs)")
        print("0. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "0":
            print("Saindo...")
            break
        elif opcao in menu:
            menu[opcao]()
        else:
            print("Opção inválida. Tente novamente.")

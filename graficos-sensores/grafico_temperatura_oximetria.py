import matplotlib.pyplot as plt
import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin_upa_connect',
    'password': 'urubu100',
    'database': 'upa_connect'
}

def buscar_nome_upa(fk_upa):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        query = f"SELECT nome FROM upa WHERE id_upa = {fk_upa}"
        cursor.execute(query)
        resultado = cursor.fetchone()
        return resultado[0] if resultado else f"UPA {fk_upa}"
    except Exception as e:
        print("Erro ao buscar nome da UPA:", e)
        return f"UPA {fk_upa}"
    finally:
        if 'conexao' in locals():
            conexao.close()

def buscar_temperaturas_corpo(fk_upa=1, data='2025-04-25'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        query = f"""
            SELECT p.id_paciente, AVG(tp.valor) AS media_temperatura
            FROM temperatura_paciente tp
            JOIN paciente p ON tp.fk_paciente = p.id_paciente
            WHERE DATE(tp.data_hora) = '{data}' AND p.fk_upa = {fk_upa}
            GROUP BY p.id_paciente;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        pacientes = [linha[0] for linha in resultados]
        temperaturas_medias = [float(linha[1]) for linha in resultados]
        return pacientes, temperaturas_medias
    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
        return [], []
    finally:
        if 'conexao' in locals():
            conexao.close()

def buscar_oximetrias_corpo(fk_upa=1, data='2025-04-25'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        query = f"""
            SELECT p.id_paciente, AVG(o.valor) AS media_oximetria
            FROM oximetro o
            JOIN paciente p ON o.fk_paciente = p.id_paciente
            WHERE DATE(o.data_hora) = '{data}' AND p.fk_upa = {fk_upa}
            GROUP BY p.id_paciente;
        """
        cursor.execute(query)
        resultados = cursor.fetchall()
        pacientes = [linha[0] for linha in resultados]
        oximetrias_medias = [float(linha[1]) for linha in resultados]
        return pacientes, oximetrias_medias
    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
        return [], []
    finally:
        if 'conexao' in locals():
            conexao.close()

def grafico_3(fk_upa=1):
    pacientes_temp, temperaturas_medias = buscar_temperaturas_corpo(fk_upa=fk_upa)
    pacientes_oxi, oximetrias_medias = buscar_oximetrias_corpo(fk_upa=fk_upa)
    nome_upa = buscar_nome_upa(fk_upa)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor='white')
    legenda_usada = {}

    for paciente, t, o in zip(pacientes_temp, temperaturas_medias, oximetrias_medias):
        if t > 39:
            cor = 'red'
            legenda = 'Febre muito alta'
        elif t < 35.3 and o < 94.5:
            cor = 'purple'
            legenda = 'Temp. baixa + Oxigenação baixa'
        elif t > 37.8 and o < 94.5:
            cor = 'red'
            legenda = 'Temperatura alta + Oxigenação baixa'
        elif t > 37.8:
            cor = 'orange'
            legenda = 'Temperatura alta'
        elif o < 94.5:
            cor = 'brown'
            legenda = 'Oxigenação baixa'
        else:
            cor = 'blue'
            legenda = 'Normal'

        if legenda not in legenda_usada:
            ax.scatter(t, o, color=cor, edgecolors='black', s=120, alpha=0.8, label=legenda)
            legenda_usada[legenda] = True
        else:
            ax.scatter(t, o, color=cor, edgecolors='black', s=120, alpha=0.8)

    ax.set_xlabel('Temperatura Corporal Média (°C)', fontsize=12)
    ax.set_ylabel('Oximetria Média (%)', fontsize=12)
    ax.set_title(f"Análise do Perfil dos Pacientes - {nome_upa}", fontsize=14)
    ax.grid(True)

    ax.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), fontsize=10, title="Condição")
    plt.tight_layout()
    plt.show()

def verificar_pacientes_com_febre_ou_oximetria_grave(fk_upa=1, data='2025-04-25'):
    try:
        conexao = pymysql.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        
        query_pacientes = f"SELECT id_paciente, nome FROM paciente WHERE fk_upa = {fk_upa}"
        cursor.execute(query_pacientes)
        pacientes = cursor.fetchall()

        _, temperaturas_medias = buscar_temperaturas_corpo(fk_upa=fk_upa, data=data)
        _, oximetrias_medias = buscar_oximetrias_corpo(fk_upa=fk_upa, data=data)

        for (id_paciente, nome_paciente), t, o in zip(pacientes, temperaturas_medias, oximetrias_medias):
            if t > 37.8 or o < 92:
                print(f"Paciente com febre ou oximetria grave: {nome_paciente}")

    except Exception as e:
        print("Erro ao buscar dados do banco:", e)
    finally:
        if 'conexao' in locals():
            conexao.close()

menu = {
    "1": lambda: grafico_3(fk_upa=int(input("Digite o ID da UPA: "))),
    "2": lambda: verificar_pacientes_com_febre_ou_oximetria_grave(fk_upa=int(input("Digite o ID da UPA: "))),  
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

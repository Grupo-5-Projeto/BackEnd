import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector

# Configurações do banco
DB_CONFIG = {
    'host': 'localhost',
    'user': 'admin_upa_connect',
    'password': 'urubu100',
    'database': 'upa_connect'
}

# Conectando ao banco
conn = mysql.connector.connect(**DB_CONFIG)

# Query para pegar data de nascimento e data/hora da biometria
query = """
SELECT 
    p.data_nascimento AS DataNascimento,
    b.data_hora AS DataHora
FROM 
    biometria b
JOIN 
    paciente p ON b.fk_paciente = p.id_paciente
WHERE 
    p.fk_upa = 1
"""

# Carregar dados em um DataFrame
df = pd.read_sql(query, conn)

# Fechar a conexão
conn.close()

# Converter para datetime
df['DataNascimento'] = pd.to_datetime(df['DataNascimento'])
df['DataHora'] = pd.to_datetime(df['DataHora'])

# Calcular a idade
df['Idade'] = df['DataHora'].dt.year - df['DataNascimento'].dt.year

# Corrigir idade se o paciente ainda não fez aniversário no ano
aniversario_passou = (df['DataHora'].dt.month > df['DataNascimento'].dt.month) | (
    (df['DataHora'].dt.month == df['DataNascimento'].dt.month) & (df['DataHora'].dt.day >= df['DataNascimento'].dt.day)
)
df['Idade'] -= (~aniversario_passou).astype(int)

# Ajustar faixas etárias
df['Faixa_Etaria'] = pd.cut(df['Idade'], bins=[0, 12, 17, 39, 59, 120], 
                            labels=['0–12', '13–17', '18–39', '40–59', '60+'])

# Ajustar faixas de horários
df['Hora'] = df['DataHora'].dt.hour
df['Faixa_Hora'] = pd.cut(df['Hora'], bins=[0, 6, 9, 12, 15, 18, 21, 24],
                          labels=['0–6h', '6–9h', '9–12h', '12–15h', '15–18h', '18–21h', '21–24h'],
                          right=False)

# Agrupar os dados
tabela = df.groupby(['Faixa_Hora', 'Faixa_Etaria']).size().unstack(fill_value=0)

# Plotar o gráfico
tabela.plot(kind='bar', figsize=(12, 6))
plt.title("Distribuição de Atendimentos por Faixa Etária e Horário (UPA)")
plt.xlabel("Horário do Dia")
plt.ylabel("Número de Atendimentos")
plt.legend(title="Faixa Etária")
plt.xticks(rotation=45)

# Adicionar linhas auxiliares no gráfico
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

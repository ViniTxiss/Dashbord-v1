import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def gerar_dados_exemplo():
    n_registros = 100
    areas = ['Trabalhista', 'Cível', 'Tributário', 'Empresarial', 'Penal']
    status = ['Execução', 'Conhecimento', 'Recursal', 'Suspenso', 'Encerrado']
    advogados = ['Carlos Silva', 'Ana Oliveira', 'Roberto Santos', 'Mariana Costa', 'Juliana Lima']
    ufs = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'PE', 'DF', 'CE']
    
    data_inicio = datetime(2025, 1, 1)
    
    dados = {
        'ID': range(1001, 1001 + n_registros),
        'Cliente': [f'Cliente {i}' for i in range(1, n_registros + 1)],
        'Area': [np.random.choice(areas) for _ in range(n_registros)],
        'Advogado': [np.random.choice(advogados) for _ in range(n_registros)],
        'Status': [np.random.choice(status) for _ in range(n_registros)],
        'Valor_Causa': np.random.uniform(5000, 500000, n_registros).round(2),
        'Honorarios': np.random.uniform(1000, 100000, n_registros).round(2),
        'UF': [np.random.choice(ufs) for _ in range(n_registros)],
        'Cidade': ['Cidade Exemplo' for _ in range(n_registros)],
        'Data_Abertura': [data_inicio + timedelta(days=np.random.randint(0, 365)) for _ in range(n_registros)],
        'Probabilidade_Exito': np.random.uniform(0.1, 1.0, n_registros).round(2)
    }
    
    df = pd.DataFrame(dados)
    df.to_excel('dados_juridicos.xlsx', index=False)
    print("Arquivo 'dados_juridicos.xlsx' gerado com sucesso!")

if __name__ == "__main__":
    gerar_dados_exemplo()

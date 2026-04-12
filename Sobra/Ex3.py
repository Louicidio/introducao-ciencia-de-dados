import pandas as pd

# df = pd.read_csv('vendas.csv')
# print(df.head())
# print(df.dtypes)

def exercicio1():
    df = pd.read_csv('vendas.csv')
    vendas_por_produto = df.groupby('Produto')['Quantidade'].sum()
    print(vendas_por_produto)

def exercicio2():
    df = pd.read_csv('metereologia.csv', sep=',', encoding='utf-8', parse_dates=["data"], index_col="data")
    print(df.head())
    print(df.dtypes)

    


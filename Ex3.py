import pandas as pd

# df = pd.read_csv('vendas.csv')
# print(df.head())
# print(df.dtypes)

def exercicio1():
    df = pd.read_csv('arquivos_csv/vendas.csv')
    vendas_por_produto = df.groupby('Produto')['Quantidade'].sum()
    print(vendas_por_produto)

def exercicio2():
    df = pd.read_csv('arquivos_csv/metereologia.csv', sep=',', encoding='utf-8', parse_dates=["data"], index_col="data")
    print(df.head())
    print(df.dtypes)

def exercicio3():
    df = pd.read_csv('arquivos_csv/log_sistema.csv', comment='#', nrows=2, engine='python')
    print(df)

def exercicio4():
    df = pd.read_csv('arquivos_csv/estoque.csv', sep=';', decimal=',') 
    df['valor_unitario'] = df['valor_unitario'].astype(float)
    df['peso_kg'] = df['peso_kg'].astype(float)
    print(df)
    print(df.dtypes)

def exercicio5():
    df = pd.read_csv('arquivos_csv/transacoes.csv', sep=',', decimal='.', thousands='.')
    df['valor'] = df['valor'].astype(float)
    print(df)
    print(df.dtypes)

def exercicio6():
    df = pd.read_csv('arquivos_csv/sensores.csv', sep=',', decimal='.', na_values=['NA', '-'])
    df['temperatura'] = df['temperatura'].astype(float)
    print(df.info())
    print(df)
    
def exercicio7():
    df = pd.read_csv('arquivos_csv/experimento.csv')
    print(df.head())
    print(df.tail())
    print(df.describe()) 
    
def exercicio8():
    df = pd.read_csv('arquivos_csv/big_data_simulado.csv', sep=',',decimal='.', na_values='False')
    print(df.info())
    print(df.head())
    
def exercicio9():
    df = pd.read_csv('arquivos_csv/notas.csv', sep=',', decimal='.')
    df = (df[['matematica', 'portugues', 'historia']].median())
    print(df)
    # print(df.describe())
    
def exercicio10():
    for chunk in pd.read_csv('arquivos_csv/transacoes_grandes.csv', sep=',', decimal='.', chunksize=20):
        print(chunk.head(3)) #le em blocos de 20 e imprime as 3 primeiras

def exercicio11():
    for chunk in pd.read_csv('arquivos_csv/dados_sensor_gigante.csv', sep=',', decimal='.', na_values=['NA', '-'], chunksize=10):
        media_temp = chunk['temperatura'].astype(float).mean()
        ausentes = chunk['temperatura'].isna().sum()
        print(int(media_temp)) # a tabela gerada pelo gepeto ficou com mts decimais, por isso converti pra integer
        print(ausentes)
exercicio11()
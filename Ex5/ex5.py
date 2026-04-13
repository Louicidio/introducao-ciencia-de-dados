import pandas as pd
import requests
from sqlalchemy import create_engine
import os

def exercicio_csv():
    print("CSV")
    #gerado pelo gepete
    csv_data = """1,ProdutoA,100,5 
2,ProdutoB,ND,3
3,ProdutoC,250,ND
4,ProdutoD,180,2
5,ProdutoE,ND,ND
6,ProdutoF,300,6
7,ProdutoG,120,4
8,ProdutoH,90,ND
9,ProdutoI,ND,1
10,ProdutoJ,450,8
11,ProdutoK,500,10
12,ProdutoL,ND,7
13,ProdutoM,220,ND
14,ProdutoN,310,5
15,ProdutoO,ND,2
16,ProdutoP,275,3
17,ProdutoQ,330,ND
18,ProdutoR,410,9
19,ProdutoS,ND,4
20,ProdutoT,150,6
"""
    with open("vendas.csv", "w") as f:
        f.write(csv_data)

    # carrega colunas validas
    df_vendas = pd.read_csv(
        "vendas.csv",
        header=None,          
        index_col=0,          
        na_values="ND"       
    )
    
    print("DataFrame carregado de 'vendas.csv':")
    print(df_vendas)
    print("\n")

def exercicio_excel():
    print("Excel")
    relatorio_anual = pd.DataFrame({
        'Ano': [2023, 2023, 2024],
        'Produto': ['A', 'B', 'A'],
        'Vendas': [1000, 1500, 1200]
    })
    dados_brutos_df = pd.DataFrame({
    'ID': list(range(1, 31)),
    'Valor': [
        99, 101, 105, 98, 102, 110, 95, 97, 103, 108,
        112, 115, 90, 92, 94, 100, 104, 106, 109, 111,
        113, 116, 118, 120, 85, 87, 89, 91, 93, 96
    ]
})

    with pd.ExcelWriter('relatorio.xlsx') as writer: #salva em relatorio.xlsx
        relatorio_anual.to_excel(writer, sheet_name='Resultados', index=False)
        dados_brutos_df.to_excel(writer, sheet_name='Dados Brutos', index=False)
    print("DataFrame 'relatorio_anual' salvo em 'relatorio.xlsx' na aba 'Resultados'.")

    df_dados_brutos = pd.read_excel('relatorio.xlsx', sheet_name='Dados Brutos')
    print("\nDataFrame lido da aba 'Dados Brutos':")
    print(df_dados_brutos)
    print("\n")

def exercicio_api():
    print("API")
    url = "https://jsonplaceholder.typicode.com/users"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        
        dados_json = response.json()
        
        df_usuarios = pd.DataFrame(dados_json)
        
        print("DataFrame criado a partir da API (primeiras 5 linhas):")
        print(df_usuarios.head())
        print("\n")
        
    except requests.exceptions.RequestException as e:
        print(f"Nao conectado com a API: {e}")

def exercicio_banco_de_dados():
    print("Banco de Dados")
    # Criando um banco de dados SQLite 
    engine = create_engine('sqlite:///meu_banco.db')
    produtos_df_exemplo = pd.DataFrame({
        'id': [1, 2, 3],
        'nome': ['Notebook', 'Mouse', 'Teclado'],
        'preco': [4500.00, 150.50, 200.00]
    })
    produtos_df_exemplo.to_sql('produtos', engine, if_exists='replace', index=False)
    
    query = "SELECT * FROM produtos"
    df_produtos = pd.read_sql(query, engine)
    
    print(df_produtos)
    print("\n")
    engine.dispose() # Fecha a conexão

if __name__ == "__main__":
    exercicio_csv()
    # exercicio_excel()
    # exercicio_api()
    # exercicio_banco_de_dados()
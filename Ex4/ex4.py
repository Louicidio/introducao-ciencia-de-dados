import string
import csv
import requests
from collections import Counter
from bs4 import BeautifulSoup

def exercicio_1():
    print("\n--- Desafio 1: Contagem de Palavras ---")
    texto_exemplo = "Dados são o novo petróleo. Dados precisam ser processados. Ciência de dados é fundamental."
    texto = texto_exemplo.lower().translate(str.maketrans('', '', string.punctuation))
    contagem = Counter(texto.split()).most_common(10)
    for pal, freq in contagem:
        print(f"{pal}: {freq}")

def exercicio_2():
    print("\n--- Desafio 2: Análise de CSV ---")
    dados_ficticios = [
        {'produto': 'Fone', 'preco': '200', 'categoria': 'Eletrônicos'},
        {'produto': 'Cadeira', 'preco': '500', 'categoria': 'Móveis'},
        {'produto': 'Mouse', 'preco': '100', 'categoria': 'Eletrônicos'}
    ]
    precos = [float(d['preco']) for d in dados_ficticios if d['categoria'] == 'Eletrônicos']
    if precos:
        print(f"Preço médio Eletrônicos: {sum(precos)/len(precos)}")

def exercicio_3():
    print("\n--- Desafio 3: Web Scraping ---")
    url = "https://www.scrapethissite.com/pages/" 
    res = requests.get(url, timeout=5)
    soup = BeautifulSoup(res.text, 'html.parser')
    for h3 in soup.find_all('h3')[:5]: 
        print(f"Título: {h3.get_text(strip=True)}")

def exercicio_4():
    print("\n--- Desafio 4: API GitHub ---")
    url = "https://api.github.com/search/repositories?q=data+science"
    res = requests.get(url).json()
    for repo in res['items'][:5]:
        print(f"Repo: {repo['name']} - {repo['html_url']}")

exercicio_4()

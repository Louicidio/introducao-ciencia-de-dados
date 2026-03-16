import math
from collections import Counter

def exerc1():
    name = "biava"
    idade = "suficiente"
    altura = 1.90
    cidade = "Jardim Alegre"

    print(name, idade, altura , cidade)

def listaCompras():
    lista = ["prateleira","vendedora", "little shirts", "🍆", "repositor de atacado"]
    lista.append("carrinho")
    print(lista)
    lista.append("caixa")
    print(lista)
    lista.remove("🍆")
    print(lista)

def media():
    notas = [7.5, 8.0, 6.0, 9.0]
    media = sum(notas) / len(notas)
    print("Média:", media)

def listComprehension():
    quadrados = [x**2 for x in range(1, 6)]
    print(quadrados)

def agenda():
    contatos = {
        "Alice": "123-456-7890",
        "Bob": "987-654-3210",
        "Charlie": "555-555-5555"
    }
    print(contatos["Alice"])

def tupla(p1, p2):
    x1 , y1 = p1
    x2, y2 = p2

    distancia = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    return distancia

def contadorPalavras():
    texto = "biava biava biava teste 2"
    palavras = texto.split()
    cont = Counter(palavras)
    print(cont.most_common(2))

def estatistica(*args):
    media = sum(args) / len(args)
    minimo = min(args)
    maximo = max(args)

    return {
        "media": media,
        "minimo": minimo,
        "maximo": maximo
    }

args = (1, 2, 3, 4, 5)
numeros = estatistica(*args)

class Produto:
    def __init__(self, nome, preco, quantidade):
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade
    
    def vender(self, quantidade_vendida):
        if quantidade_vendida <= self.quantidade:
            self.quantidade -= quantidade_vendida
            receita = quantidade_vendida * self.preco
            print(f"Venda realizada: {quantidade_vendida} unidades de {self.nome} por R${receita:.2f}")
        else:
            return "Quantidade insuficiente em estoque"
    def repor_estoque(self, quantidade_reposta):
        self.quantidade += quantidade_reposta
        return self.quantidade
    
    def exibir(self):
        return f"Produto: {self.nome}, Preço: R${self.preco:.2f}, Quantidade em estoque: {self.quantidade}"

# produto = Produto("Camiseta", 29.99, 100)
# produto.exibir()
# produto.vender(10)
# produto.repor_estoque(10)
# produto.exibir()

class Veiculos:
    def __init__ (self, marca, modelo, ano) :
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
    
    def tipo_habilitacao(self):
        return "Categoria Vasco Da Gama"
class Carro(Veiculos):
    def tipo_habilitacao(self):
        return "Categoria B"

class Moto(Veiculos):
    def tipo_habilitacao(self):
        return "Categoria A"
    
carro = Carro("Toyota", "Corolla", 2020)
moto = Moto("Honda", "CB500", 2020) 
print(carro.tipo_habilitacao())
print(moto.tipo_habilitacao())

import numpy as np

# Desafios 
def create_array():
# 1 exercicio
    arr = np.random.randint(100, 500, size=(12))
    print(arr)

# 2 exercicio
    arrr = arr.reshape((3, 4))
    print("Matriz 3x4:", arrr)

    print(arrr[:,0:1])

# 3 exercicio
    soma = arrr.sum(axis=1)
    print("Soma das semanas", soma)

# 4 exercicio

    media = arrr.mean(axis=1)
    print("Media por semana", media)

# 5 exercicio
    acima = arrr > 400
    print("Valores acima de 300", acima)


# Desafios part2
def dedsafiospart2():
    #Des 1
    vascodagama = np.arange(10)
    print(vascodagama)

    #Des 2
    boliano = np.ones((3,3), dtype=bool)
    print(boliano)

    #Des 3
    arr = vascodagama
    impares = arr[arr % 2 == 1] #numeros impares 
    print("Impares: ", impares)

    #Des 4
    substituir = np.arange(10)
    substituir[substituir % 2 == 0] = -1 #substituir numeros pares por -1
    print("substituidos: ", substituir)

    #Des5
    matrizAleatoria = np.random.randint(1, 101, size=(5, 5))
    print(matrizAleatoria)

    #Des6
    soma = matrizAleatoria.sum(axis=0)
    print("Soma da coluna", soma)

    #Des7
    maximo = matrizAleatoria.max(axis=1)
    print("Maior em cada coluna", maximo)

    #Des8
    a = np.array([1,2,3,4,5])
    broadcast = a + 2
    print ("Numeros array + 2 =", broadcast)

    #Des9
    a = np.array([1,2,3])
    b = np.array([4,5,6])
    concatenada = np.concatenate((a, b))
    print("A e B, concatenados: ", concatenada)

    #Des10
    invertido = np.array([10,20,30,40,50])
    invertido = invertido[::-1]
    print("Array invertido: ", invertido)

def desafiospart3():
    #1
    temps = np.array([20, 22, 25, 18, 30, 28, 15])
    media = temps.mean()
    print("Temperatura média: ", media)
    mais_quente = temps.argmax()
    match mais_quente:
        case 0: #Em um mundo cheio de purpurinas vc não retorna indice
            print("O dia mais quente foi Domingo")
        case 1:
            print("O dia mais quente foi Segunda")    
        case 2:
            print("O dia mais quente foi Terça")
        case 3:
            print("O dia mais quente foi Quarta")
        case 4:
            print("O dia mais quente foi Quinta")
        case 5:
            print("O dia mais quente foi Sexta")
        case 6:
            print("O dia mais quente foi Sábado") 

    # 2
    vendas = np.random.randint(50 , 201, size=(2,2))
    total_vendas = vendas.sum(axis=1)
    print("total de vendas", total_vendas)

    # 3
    a = np.random.randint(1, 40, size=(10))
    print(a)
    print(a.max())
    print(a.min())

    # 4
    leitura = np.random.rand(20)
    acima = leitura[leitura > 0.7]
    print(acima)

    #5 
    precos = np.random.uniform(10.0, 100.0, size=(5))
    variacao = np.diff(precos) / precos[:-1] * 100
    print("receba", variacao)

    #6 
    identidade = np.eye(4)
    print("identidade\n", identidade)

    #7
    zeros = np.zeros((3, 3))
    uns = np.ones((2, 5))
    print("Matriz de zeros\n", zeros)
    print("Matriz de uns\n", uns)

    #8
    imagem = np.random.randint(0, 256, size=25)
    imagem_5x5 = imagem.reshape((5, 5))
    print("Imagem 5x5\n", imagem_5x5)

    #9
    aurei = np.arange(10)
    pares = aurei[aurei % 2 == 0]
    print("Pares: ", pares)

    #10
    acumulada = np.array([1, 2, 3, 4, 5]).cumsum()
    print("Soma acumulada: ", acumulada)

    #11 
    unicos = np.array([1, 2, 2, 3, 4, 4, 5])
    unicos = np.unique(unicos)

    #12
    linspace = np.linspace(0, 10, 5)
    print("Linspace: ", linspace)

    #13
    notas = np.array([80,90,70])
    pesos = np.array([0.3, 0.5, 0.2])
    media_ponderada = np.dot(notas, pesos)
    print("Média ponderada: ", media_ponderada)

    #14
    dados = np.array([[2,4,6], [80,90,70]])
    transposta = dados.T
    print("Transposta: ", transposta)

    #15
    matriz = np.random.randint(0, 10, size=(3, 4))
    print("Matriz original: ", matriz)
    invertida = matriz[:, ::-1]
    print("Matriz invertida: ", invertida)

    #16
    a = np.array([1, 2, 3])
    b = np.array([4, 2, 6])
    iguais = a == b # meu Deus
    print("Elementos iguais: ", iguais)

    #17
    vascodagama = np.random.randint(0, 101, size=(10))
    print("Vasco da Gama: ", vascodagama)
    mascara = vascodagama > 50
    print("Valores maiores que 50: ", vascodagama[mascara])

    #18
    variavel = np.array([1, 7, 3, 7, 5, 7])
    contagem = np.count_nonzero(variavel == 7)
    print("Contagem do numero sete: ", contagem)

    #19
    arredonda = np.array([1.23, 2.78, 3.5, 4.11])
    print("Array original: ", arredonda)
    arredondado = np.round(arredonda)
    print("Array arredondado: ", arredondado)

    #20
    aurei1 = np.array([1, 2, 3])
    aurei2 = np.array([4, 5, 6])
    empilhado = np.vstack((aurei1, aurei2))
desafiospart3()

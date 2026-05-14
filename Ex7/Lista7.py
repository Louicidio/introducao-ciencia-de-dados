from time import sleep

import pandas as pd  # type: ignore[import-not-found]
from sklearn.preprocessing import StandardScaler  # type: ignore[import-not-found]
from tqdm import tqdm  # type: ignore[import-not-found]

#exercicio 4
def try_or_none(func, value):
    try:
        return func(value)
    except Exception:
        return None

def converter_para_inteiros(valores):
    return [try_or_none(int, valor) for valor in valores]

#exercicio 6 
def standardize_features(data):
    scaler = StandardScaler()
    return scaler.fit_transform(data)

#exercicio 7
def simular_tarefa_demorada(iterations=100, delay_seconds=0.01):
    for _ in tqdm(range(iterations), desc="Processando"):
        sleep(delay_seconds)

#exercicio 8
def iterar_com_indice(items):
    for index, item in tqdm(enumerate(items), total=len(items), desc="Iterando"):
        print(index, item)

#exercicio 10
def aplicar_com_tqdm(df, func, result_column):
    tqdm.pandas()
    df[result_column] = df.progress_apply(func, axis=1)
    return df
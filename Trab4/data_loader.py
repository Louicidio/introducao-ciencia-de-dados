import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def carregar_e_preparar_dados(arquivo='ano_completo_unificado.xlsx'):

    df = pd.read_excel(arquivo)

    df = df.dropna()

    df['TAXA_OCUPACAO'] = df['OCUPADA'] / df['DISTRIBUIDA'].replace(0, np.nan)
    df['TAXA_VAGAS'] = df['VAGAS'] / df['APROVADA'].replace(0, np.nan)
    df['SALDO'] = df['APROVADA'] - df['OCUPADA']

    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    df['OCUPACAO_ALTA'] = (df['TAXA_OCUPACAO'] > 0.7).astype(int)

    return df


def preparar_modelos(df, test_size=0.3, random_state=42):

    features = ['APROVADA', 'DISTRIBUIDA', 'OCUPADA', 'VAGAS', 'SALDO']
    X = df[features].values
    y_class = df['OCUPACAO_ALTA'].values
    y_reg = df['TAXA_OCUPACAO'].values

    X_train, X_test, y_train_class, y_test_class = train_test_split(
        X, y_class, test_size=test_size, random_state=random_state, stratify=y_class
    )
    _, _, y_train_reg, y_test_reg = train_test_split(
        X, y_reg, test_size=test_size, random_state=random_state
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print(f"    Treino: {X_train.shape[0]} amostras")
    print(f"    Teste: {X_test.shape[0]} amostras")

    return {
        'features': features,
        'X_train': X_train, 'X_test': X_test,
        'X_train_scaled': X_train_scaled, 'X_test_scaled': X_test_scaled,
        'y_train_class': y_train_class, 'y_test_class': y_test_class,
        'y_train_reg': y_train_reg, 'y_test_reg': y_test_reg,
        'df': df
    }

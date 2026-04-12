import os
import pandas as pd

# Caminho da pasta com os arquivos ODS
pasta_entrada = r"C:\Users\Luis Eduardo\Desktop\2026\Introdu-o-Ci-ncia-de-dados\UnificarBanco2"

banco = []

for arquivo in os.listdir(pasta_entrada):
    if arquivo.endswith(".ods"):
        caminho_ods = os.path.join(pasta_entrada, arquivo)
        # Lê todas as abas do ODS
        abas = pd.read_excel(caminho_ods, engine="odf", sheet_name=None)
        for nome_aba, df in abas.items():
            df['arquivo_origem'] = arquivo
            df['aba_origem'] = nome_aba
            banco.append(df)

if banco:
    # Unifica tudo em um DataFrame só
    df_banco = pd.concat(banco, ignore_index=True)
    df_banco.to_excel(os.path.join(pasta_entrada, "banco_unificado.xlsx"), index=False)
    print("Banco unificado salvo como banco_unificado.xlsx na mesma pasta dos ODS.")
else:
    print("Nenhum arquivo ODS encontrado ou nenhum dado lido.")
import pandas as pd
import glob
arquivos = glob.glob(r"C:\Users\Luis Eduardo\Desktop\2026\Introdu-o-Ci-ncia-de-dados\UnificarBanco2\*.ods")
df_final = pd.concat([pd.read_excel(f, engine='odf') for f in arquivos])
df_final.to_excel("unificado.xlsx", index=False)

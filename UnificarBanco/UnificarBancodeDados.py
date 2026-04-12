import pandas as pd
import glob

arquivos = glob.glob("*.xlsx")

df = pd.concat([pd.read_excel(f) for f in arquivos])

df.to_excel("ano_completo.xlsx", index=False)
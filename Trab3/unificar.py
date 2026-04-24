import re
from pathlib import Path

import pandas as pd

MES_POR_ABREV = {
    "01": "Jan",
    "1": "Jan",
    "02": "Fev",
    "2": "Fev",
    "03": "Mar",
    "3": "Mar",
    "04": "Abr",
    "4": "Abr",
    "05": "Mai",
    "5": "Mai",
    "06": "Jun",
    "6": "Jun",
    "07": "Jul",
    "7": "Jul",
    "08": "Ago",
    "8": "Ago",
    "09": "Set",
    "9": "Set",
    "10": "Out",
    "11": "Nov",
    "12": "Dez",
}

MES_NAME_MAP = {
    "JAN": "Jan",
    "JANEIRO": "Jan",
    "FEV": "Fev",
    "FEVEREIRO": "Fev",
    "MAR": "Mar",
    "MARCO": "Mar",
    "MARÇO": "Mar",
    "ABR": "Abr",
    "ABRIL": "Abr",
    "MAI": "Mai",
    "MAIO": "Mai",
    "JUN": "Jun",
    "JUNHO": "Jun",
    "JUL": "Jul",
    "JULHO": "Jul",
    "AGO": "Ago",
    "AGOSTO": "Ago",
    "SET": "Set",
    "SETEMBRO": "Set",
    "OUT": "Out",
    "OUTUBRO": "Out",
    "NOV": "Nov",
    "NOVEMBRO": "Nov",
    "DEZ": "Dez",
    "DEZEMBRO": "Dez",
}

STANDARD_COLUMNS = [
    "NOME_MES",
    "ORGAO",
    "NOME_ORGAO",
    "SIGLA_ORGAO",
    "APROVADA",
    "DISTRIBUIDA",
    "OCUPADA",
    "VAGAS",
]

NUMERIC_COLUMNS = ["ORGAO", "APROVADA", "DISTRIBUIDA", "OCUPADA", "VAGAS"]


def normalize_mes_ano(value):
    if pd.isna(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("/", " ").replace("-", " ")

    numeric_match = re.fullmatch(r"(\d{4})(\d{2})", text)
    if numeric_match:
        year, month = numeric_match.groups()
        return f"{MES_POR_ABREV.get(month, month)} {year}"

    numeric_match = re.fullmatch(r"(\d{4})\s+(\d{1,2})", text)
    if numeric_match:
        year, month = numeric_match.groups()
        return f"{MES_POR_ABREV.get(str(int(month)), month)} {year}"

    parts = text.upper().split()
    if len(parts) >= 2 and parts[-1].isdigit() and len(parts[-1]) == 4:
        month_token = parts[0]
        month_abrev = MES_NAME_MAP.get(month_token)
        if month_abrev:
            return f"{month_abrev} {parts[-1]}"

    return text.title()


def cast_numeric_columns(df: pd.DataFrame):
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
    return df


def load_ano_completo(path: Path) -> pd.DataFrame:
    print(f"[PASSO 1/4] Lendo {path.name}")
    df = pd.read_excel(path, dtype=str)
    print(f"  - Linhas lidas: {len(df)}")

    df = df.dropna(how="all")
    print(f"  - Linhas após remover vazios: {len(df)}")

    df = df.rename(columns={col: col.strip() for col in df.columns})

    if "NOME_MES" not in df.columns:
        raise ValueError("Arquivo ano_completo.xlsx não contém a coluna NOME_MES")

    df["NOME_MES"] = df["NOME_MES"].map(normalize_mes_ano)
    df = df[[col for col in STANDARD_COLUMNS if col in df.columns]]
    df = cast_numeric_columns(df)
    print(f"  - Colunas finais: {list(df.columns)}")
    return df


def load_unificado(path: Path) -> pd.DataFrame:
    print(f"[PASSO 2/4] Lendo {path.name}")
    df = pd.read_excel(path, header=None, dtype=str)
    print(f"  - Linhas lidas: {len(df)}")

    df = df.dropna(how="all")
    print(f"  - Linhas após remover vazios: {len(df)}")

    expected_header = [
        "ANO_MES",
        "ORGAO",
        "NOME_ORGAO",
        "SIGLA_ORGAO",
        "APROVADA",
        "DISTRIBUIDA",
        "OCUPADA",
        "VAGA",
    ]

    header_row = None
    for idx in range(min(10, len(df))):
        row = df.iloc[idx].astype(str).str.strip().tolist()
        if row[: len(expected_header)] == expected_header:
            header_row = idx
            break

    if header_row is None:
        raise ValueError("Não foi possível encontrar o cabeçalho esperado em unificado.xlsx")

    df = df.iloc[header_row + 1 :].copy()
    df.columns = expected_header

    df = df.dropna(how="all")
    print(f"  - Linhas após remover vazios da tabela: {len(df)}")

    df = df.rename(columns={"ANO_MES": "NOME_MES", "VAGA": "VAGAS"})
    df["NOME_MES"] = df["NOME_MES"].map(normalize_mes_ano)
    df = df[[col for col in STANDARD_COLUMNS if col in df.columns]]
    df = cast_numeric_columns(df)
    print(f"  - Colunas finais: {list(df.columns)}")
    return df


def main() -> None:
    base_path = Path(__file__).resolve().parent
    ano_path = base_path / "ano_completo.xlsx"
    uni_path = base_path / "unificado.xlsx"
    output_path = base_path / "ano_completo_unificado.xlsx"

    print(f"[ETAPA 1/4] Preparando caminhos de arquivo")
    print(f"  - ano_completo: {ano_path}")
    print(f"  - unificado: {uni_path}")

    df_ano = load_ano_completo(ano_path)
    df_uni = load_unificado(uni_path)

    print(f"[ETAPA 3/4] Concatenando datasets")
    df_combined = pd.concat([df_ano, df_uni], ignore_index=True)
    print(f"  - Total após concatenação: {len(df_combined)} linhas")

    print(f"[ETAPA 4/4] Ordenando e salvando")
    df_combined["CHAVE_MES"] = df_combined["NOME_MES"].astype(str)
    df_combined = df_combined.sort_values(["CHAVE_MES", "ORGAO"], ignore_index=True)
    df_combined = df_combined.drop(columns=["CHAVE_MES"])

    print(f"  - Salvando arquivo em: {output_path.name}")
    df_combined.to_excel(output_path, index=False, engine="openpyxl")

    print("Resumo final:")
    print(f"  - Registros ano_completo: {len(df_ano)}")
    print(f"  - Registros unificado: {len(df_uni)}")
    print(f"  - Registros totais unificados: {len(df_combined)}")


if __name__ == "__main__":
    main()

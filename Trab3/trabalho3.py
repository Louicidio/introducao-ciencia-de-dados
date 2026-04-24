from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
ARQUIVO_BASE = BASE_DIR / "ano_completo_unificado.xlsx"
PASTA_SAIDA = BASE_DIR

#Para usar carregue as informacoes de um arquivo .env 
def _carregar_env_local() -> None:
    for nome_arquivo in (".env"):
        caminho_env = ROOT_DIR / nome_arquivo
        if not caminho_env.exists():
            continue
        for linha in caminho_env.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip())

_carregar_env_local()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

logging.basicConfig(
    filename=str(PASTA_SAIDA / "pipeline.log"),
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

MESES = {
    "jan": 1,
    "fev": 2,
    "mar": 3,
    "abr": 4,
    "mai": 5,
    "jun": 6,
    "jul": 7,
    "ago": 8,
    "set": 9,
    "out": 10,
    "nov": 11,
    "dez": 12,
}

def carregar_dados(caminho_arquivo: Path = ARQUIVO_BASE) -> pd.DataFrame | None:
    try:
        df = pd.read_excel(caminho_arquivo)
        df.columns = [
            "competencia",
            "orgao_id",
            "nome_orgao",
            "sigla_orgao",
            "aprovada",
            "distribuida",
            "ocupada",
            "vagas",
        ]

        for coluna in ["competencia", "nome_orgao", "sigla_orgao"]:
            df[coluna] = df[coluna].astype(str).str.strip()

        df["orgao_id"] = pd.to_numeric(df["orgao_id"], errors="coerce")
        for coluna in ["aprovada", "distribuida", "ocupada", "vagas"]:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

        df = df.dropna(subset=["competencia", "orgao_id", "nome_orgao", "sigla_orgao", "aprovada", "distribuida", "ocupada", "vagas"])

        partes = df["competencia"].str.extract(r"^(?P<mes>[A-Za-zÇç]{3})\s+(?P<ano>\d{4})$")
        partes["mes_num"] = partes["mes"].str.lower().map(MESES)
        partes["ano"] = pd.to_numeric(partes["ano"], errors="coerce")
        df = pd.concat([df, partes], axis=1)
        df = df.dropna(subset=["mes_num", "ano"])

        df["ano"] = df["ano"].astype(int)
        df["mes_num"] = df["mes_num"].astype(int)
        df["competencia_dt"] = pd.to_datetime(
            dict(year=df["ano"], month=df["mes_num"], day=1),
            errors="coerce",
        )
        df = df.dropna(subset=["competencia_dt"])

        df["orgao_id"] = df["orgao_id"].astype(int)
        for coluna in ["aprovada", "distribuida", "ocupada", "vagas"]:
            df[coluna] = df[coluna].astype(float)

        df = df.drop_duplicates(subset=["competencia", "orgao_id", "sigla_orgao"], keep="last")
        df = df.sort_values(["competencia_dt", "sigla_orgao"]).reset_index(drop=True)

        return df
    except FileNotFoundError:
        return None
    except Exception as erro:
        return None

def criar_estrutura_mysql() -> None:
    conexao = None
    cursor = None

    try:
        conexao = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        cursor = conexao.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS dados_govbr (
                id INT AUTO_INCREMENT PRIMARY KEY,
                competencia DATE NOT NULL,
                orgao_id INT NOT NULL,
                nome_orgao VARCHAR(255) NOT NULL,
                sigla_orgao VARCHAR(80) NOT NULL,
                aprovada DOUBLE NOT NULL,
                distribuida DOUBLE NOT NULL,
                ocupada DOUBLE NOT NULL,
                vagas DOUBLE NOT NULL,
                UNIQUE KEY uk_dados_govbr (competencia, orgao_id, sigla_orgao)
            )
            """
        )
        conexao.commit()
    except mysql.connector.Error as erro:
        logging.exception("Erro ao criar estrutura MySQL.")
        raise RuntimeError(f"Falha ao criar estrutura MySQL: {erro}") from erro
    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()

def limpar_tabela_mysql() -> None:
    conexao = None
    cursor = None

    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM dados_govbr")
        conexao.commit()
    except mysql.connector.Error as erro:
        if conexao is not None:
            conexao.rollback()
        logging.exception("Erro ao limpar tabela MySQL.")
        raise RuntimeError(f"Falha ao limpar tabela MySQL: {erro}") from erro
    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()


def salvar_no_mysql(df: pd.DataFrame) -> None:
    conexao = None
    cursor = None

    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        cursor = conexao.cursor()

        sql = """
            INSERT INTO dados_govbr (
                competencia, orgao_id, nome_orgao, sigla_orgao,
                aprovada, distribuida, ocupada, vagas
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                nome_orgao = VALUES(nome_orgao),
                aprovada = VALUES(aprovada),
                distribuida = VALUES(distribuida),
                ocupada = VALUES(ocupada),
                vagas = VALUES(vagas)
        """

        registros = [
            (
                linha.competencia_dt.to_pydatetime(),
                int(linha.orgao_id),
                linha.nome_orgao,
                linha.sigla_orgao,
                float(linha.aprovada),
                float(linha.distribuida),
                float(linha.ocupada),
                float(linha.vagas),
            )
            for linha in df.itertuples(index=False)
        ]

        cursor.executemany(sql, registros)
        conexao.commit()
    except mysql.connector.Error as erro:
        if conexao is not None:
            conexao.rollback()
        logging.exception("Erro ao salvar dados no MySQL.")
        raise RuntimeError(f"Falha ao salvar no MySQL: {erro}") from erro
    finally:
        if cursor is not None:
            cursor.close()
        if conexao is not None and conexao.is_connected():
            conexao.close()


def consultar_dados(busca: str | None = None) -> pd.DataFrame:
    engine = create_engine(
        URL.create(
            "mysql+mysqlconnector",
            username=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            database=DB_CONFIG["database"],
        )
    )

    try:
        consulta = """
            SELECT competencia, orgao_id, nome_orgao, sigla_orgao,
                   aprovada, distribuida, ocupada, vagas
            FROM dados_govbr
        """
        parametros: list[str] = []

        if busca:
            consulta += """
                WHERE nome_orgao LIKE %s
                   OR sigla_orgao LIKE %s
                   OR DATE_FORMAT(competencia, '%Y-%m') LIKE %s
            """
            termo = f"%{busca}%"
            parametros = [termo, termo, termo]

        consulta += " ORDER BY competencia, sigla_orgao"
        with engine.connect() as conexao:
            df = pd.read_sql(consulta, conexao, params=parametros)
            if not df.empty:
                df["competencia"] = pd.to_datetime(df["competencia"])
        return df
    except mysql.connector.Error as erro:
        logging.exception("Erro ao consultar dados no MySQL.")
        raise RuntimeError(f"Falha na consulta MySQL: {erro}") from erro


def salvar_estatisticas(df: pd.DataFrame, sufixo: str) -> None:
    estatisticas = df[["aprovada", "distribuida", "ocupada", "vagas"]].describe().round(2)
    caminho = PASTA_SAIDA / f"estatisticas_{sufixo}.txt"

    with caminho.open("w", encoding="utf-8") as arquivo:
        arquivo.write("ESTATÍSTICAS DESCRITIVAS\n\n")
        arquivo.write(estatisticas.to_string())
        arquivo.write("\n\nTOTAL DE REGISTROS: ")
        arquivo.write(str(len(df)))

def gerar_grafico_pizza(df: pd.DataFrame, sufixo: str) -> None:
    resumo = (
        df.groupby("sigla_orgao", as_index=False)["vagas"]
        .sum()
        .sort_values("vagas", ascending=False)
        .head(10)
    )

    plt.figure(figsize=(10, 8))
    plt.pie(
        resumo["vagas"],
        labels=resumo["sigla_orgao"],
        autopct="%1.1f%%",
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
    )
    plt.title("Top 10 Órgãos com mais vagas \n" , fontsize=14)
    plt.axis("equal")
    plt.tight_layout()
    caminho = PASTA_SAIDA / f"grafico_pizza_{sufixo}.png"
    plt.savefig(caminho, dpi=160)
    plt.close()
def gerar_grafico_linha(df: pd.DataFrame, sufixo: str) -> None:
    serie = (
        df.groupby(df["competencia"].dt.to_period("Y"))["ocupada"]
        .sum()
        .sort_index()
    )

    plt.figure(figsize=(13, 6))
    plt.plot(serie.index.astype(str), serie.values, color="#c45c3c", linewidth=2.5)
    plt.title("Evolução anual das ocupadas")
    plt.xlabel("Ano")
    plt.ylabel("Quantidade ocupada")
    plt.xticks(rotation=45)
    plt.grid(alpha=0.25)
    plt.tight_layout()
    caminho = PASTA_SAIDA / f"grafico_linha_{sufixo}.svg"
    plt.savefig(caminho)
    plt.close()

def preparar_dataframe_analise(df: pd.DataFrame) -> pd.DataFrame:
    preparado = df.copy()

    if "competencia_dt" in preparado.columns:
        preparado["competencia"] = pd.to_datetime(preparado["competencia_dt"], errors="coerce")
    else:
        preparado["competencia"] = pd.to_datetime(preparado["competencia"], errors="coerce")

    preparado = preparado.dropna(subset=["competencia"])
    return preparado

def aplicar_busca_local(df: pd.DataFrame, busca: str | None) -> pd.DataFrame:
    if not busca:
        return df.copy()

    termo = busca.strip().lower()
    if not termo:
        return df.copy()

    competencia_texto = df["competencia_dt"].dt.strftime("%Y-%m") if "competencia_dt" in df.columns else pd.Series([None] * len(df), index=df.index)
    mascara = (
        df["nome_orgao"].astype(str).str.lower().str.contains(termo, na=False)
        | df["sigla_orgao"].astype(str).str.lower().str.contains(termo, na=False)
        | df["competencia"].astype(str).str.lower().str.contains(termo, na=False)
        | competencia_texto.astype(str).str.lower().str.contains(termo, na=False)
    )
    return df.loc[mascara].copy()

def executar_pipeline(busca: str | None, limpar: bool, sem_mysql: bool) -> None:
    df_local = carregar_dados()
    if df_local is None or df_local.empty:
        return

    sufixo = (busca or "geral").lower().replace(" ", "_")

    if not sem_mysql:
        try:
            criar_estrutura_mysql()
            if limpar:
                limpar_tabela_mysql()
            salvar_no_mysql(df_local)
            df_consultado = consultar_dados(busca=busca)
        except RuntimeError as erro:
            df_consultado = aplicar_busca_local(df_local, busca)
    else:
        df_consultado = aplicar_busca_local(df_local, busca)

    df_consultado = preparar_dataframe_analise(df_consultado)

    if df_consultado.empty:
        return

    gerar_grafico_pizza(df_consultado, sufixo)
    gerar_grafico_linha(df_consultado, sufixo)
    salvar_estatisticas(df_consultado, sufixo)

def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trabalho 3")
    parser.add_argument("--busca", default=None, help="")
    parser.add_argument("--limpar", action="store_true", help="")
    parser.add_argument("--sem-mysql", action="store_true", help="")
    return parser

def main() -> None:
    args = criar_parser().parse_args()
    executar_pipeline(busca=args.busca, limpar=args.limpar, sem_mysql=args.sem_mysql)

if __name__ == "__main__":
    main()
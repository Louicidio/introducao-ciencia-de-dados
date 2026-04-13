import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

def conectar_banco():
    try:
        return mysql.connector.connect(
            user='root',
            password='Luis74411!',
            host='127.0.0.1',
            database='Jotair'
        )
    except mysql.connector.Error as err:
        print(f"Erro de conexão com o banco: {err}")
        return None

def coletar_dados_cargos(caminho_arquivo="ano_completo.xlsx"):
    try:
        df = pd.read_excel(caminho_arquivo)
        print(f"Dados de cargos vagos coletados: {len(df)} registros.")
        return df
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao ler o arquivo Excel: {e}")
        return None

def processar_dados(df):
    if df is None:
        return None
    try:
        # Garantir que as colunas numericas sao tratadas corretamente
        colunas_numericas = ['total_cargos_vagos', 'total_cargos_ocupados', 'total_cargos']
        for col in colunas_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Criar uma coluna de data para ordenação e filtros
        df['data'] = pd.to_datetime(df['ano'].astype(str) + '-' + df['mes'].astype(str) + '-01')
        df = df.sort_values('data').reset_index(drop=True)
        
        print(f"Dados processados e formatados. Total de {len(df)} registros.")
        return df
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        return None

def calcular_estatisticas(df):
    if df is None or 'total_cargos_vagos' not in df.columns:
        return None
    try:
        stats = {
            'média_mensal_vagos': df['total_cargos_vagos'].mean(),
            'máximo_vagos': df['total_cargos_vagos'].max(),
            'mínimo_vagos': df['total_cargos_vagos'].min(),
            'total_geral_vagos': df['total_cargos_vagos'].sum()
        }
        print("\n📊 ESTATÍSTICAS DE CARGOS VAGOS (ÚLTIMOS 10 ANOS):")
        for chave, valor in stats.items():
            print(f"- {chave.replace('_', ' ').capitalize()}: {valor:,.0f}".replace(',', '.'))
        return stats
    except Exception as e:
        print(f"Erro ao calcular estatísticas: {e}")
        return None

def criar_graficos(df):
    if df is None: return
    try:
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        fig.suptitle('Análise de Cargos Vagos no Executivo Federal (Últimos 10 Anos)', fontsize=20, fontweight='bold')

        # Gráfico 1
        df_agg_data = df.groupby('data')['total_cargos_vagos'].sum()
        axes[0, 0].plot(df_agg_data.index, df_agg_data.values, color='red', marker='o', linestyle='-')
        axes[0, 0].set_title('Evolução Mensal de Cargos Vagos')
        axes[0, 0].set_ylabel('Total de Cargos Vagos')
        axes[0, 0].grid(True, linestyle='--', alpha=0.6)

        # Gráfico 2
        cargos_por_ano = df.groupby('ano')['total_cargos_vagos'].sum()
        cargos_por_ano.plot(kind='bar', ax=axes[0, 1], color='darkorange')
        axes[0, 1].set_title('Total de Cargos Vagos por Ano')
        axes[0, 1].set_ylabel('Total de Cargos')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # Gráfico 3
        df_agg_ano = df.groupby('ano')[['total_cargos_vagos', 'total_cargos_ocupados']].sum()
        df_agg_ano.plot(kind='area', ax=axes[1, 0], stacked=False, alpha=0.7, color=['red', 'green'])
        axes[1, 0].set_title('Cargos Vagos vs. Ocupados por Ano')
        axes[1, 0].set_ylabel('Número de Cargos')

        # Gráfico 
        stats = calcular_estatisticas(df)
        axes[1, 1].axis('off')
        stats_text = f"""
        RESUMO ESTATÍSTICO
        ─────────────────
        Média Mensal: {stats['média_mensal_vagos']:,.0f}
        Pico Máximo: {stats['máximo_vagos']:,.0f}
        Pico Mínimo: {stats['mínimo_vagos']:,.0f}
        Total no Período: {stats['total_geral_vagos']:,.0f}
        """
        axes[1, 1].text(0.1, 0.5, stats_text.replace(',', '.'), fontsize=12, family='monospace', va='center')

        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig('relatorio_cargos_vagos.png', dpi=300)
        print("\nGráficos salvos em 'relatorio_cargos_vagos.png'")
        plt.show()
    except Exception as e:
        print(f"Erro ao criar gráficos: {e}")

def armazenar_banco(df, cnx):
    if df is None or cnx is None: return
    try:
        cursor = cnx.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cargos_vagos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data_registro DATE NOT NULL,
            ano INT,
            mes INT,
            sigla_orgao VARCHAR(50),
            nome_cargo VARCHAR(255),
            total_cargos_vagos INT,
            total_cargos_ocupados INT,
            total_cargos INT,
            UNIQUE KEY (data_registro, sigla_orgao, nome_cargo)
        )
        """)
        
        inserir_sql = """
        INSERT IGNORE INTO cargos_vagos 
        (data_registro, ano, mes, sigla_orgao, nome_cargo, total_cargos_vagos, total_cargos_ocupados, total_cargos) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        registros = [tuple(row) for row in df[['data', 'ano', 'mes', 'sigla_orgao', 'nome_cargo', 'total_cargos_vagos', 'total_cargos_ocupados', 'total_cargos']].to_numpy()]
        cursor.executemany(inserir_sql, registros)
        
        cnx.commit()
        print(f"{cursor.rowcount} novos registros armazenados no banco de dados.")
        cursor.close()
    except mysql.connector.Error as err:
        print(f"Erro ao armazenar no banco: {err}")

def salvar_excel(df):
    """Salva o DataFrame em um arquivo Excel."""
    if df is None: return
    try:
        df.to_excel("cargos_vagos_analise.xlsx", index=False, engine='openpyxl')
        print("Dados de análise salvos com sucesso em 'cargos_vagos_analise.xlsx'")
    except Exception as e:
        print(f"Erro ao salvar arquivo Excel: {e}")

def executar_pipeline():

    dados_brutos = coletar_dados_cargos()
    df_processado = processar_dados(dados_brutos)
    if df_processado is None or df_processado.empty:
        print("interrompido: não há dados para processar.")
        return

    calcular_estatisticas(df_processado)
    criar_graficos(df_processado)
    
    cnx = conectar_banco()
    if cnx:
        armazenar_banco(df_processado, cnx)
        cnx.close()
        print("Conexão com o banco de dados fechada.")

    salvar_excel(df_processado)
    
if __name__ == "__main__":
    executar_pipeline()
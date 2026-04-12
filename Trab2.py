import mysql.connector
import pandas as pd
import requests
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Configuração do banco de dados
def conectar_banco():
    return mysql.connector.connect(
        user='root',
        password='Luis74411!',
        host='127.0.0.1',
        database='Jotair'
    )

# 1. COLETAR DADOS (exemplo com API do IBGE)
def coletar_dados():
    """Coleta dados de saúde/população do IBGE"""
    try:
        # API exemplo: dados de população por município
        url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
        response = requests.get(url)
        dados = response.json()
        print(f"✓ Dados coletados: {len(dados)} registros")
        return dados
    except Exception as e:
        print(f"✗ Erro ao coletar dados: {e}")
        return None
c
# 2. TRATAR E CONVERTER DADOS
def processar_dados(dados):
    """Converte JSON em DataFrame e filtra últimos 10 anos"""
    try:
        # Exemplo: criar DataFrame com dados
        df = pd.DataFrame(dados)
        
        # Se houver coluna de data, filtrar últimos 10 anos
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'])
            limite = datetime.now() - timedelta(days=365*10)
            df = df[df['data'] >= limite]
        
        print(f"✓ Dados processados: {len(df)} registros válidos")
        return df
    except Exception as e:
        print(f"✗ Erro ao processar dados: {e}")
        return None

# 3. CALCULAR ESTATÍSTICAS
def calcular_estatisticas(df, coluna_numerica):
    """Calcula média, máximo, mínimo"""
    try:
        stats = {
            'média': df[coluna_numerica].mean(),
            'máximo': df[coluna_numerica].max(),
            'mínimo': df[coluna_numerica].min(),
            'desvio_padrão': df[coluna_numerica].std(),
            'mediana': df[coluna_numerica].median()
        }
        
        print("\n📊 ESTATÍSTICAS:")
        for chave, valor in stats.items():
            print(f"{chave}: {valor:.2f}")
        
        return stats
    except Exception as e:
        print(f"✗ Erro ao calcular estatísticas: {e}")
        return None

# 4. CRIAR GRÁFICOS
def criar_graficos(df, coluna_numerica, titulo="Dados"):
    """Cria visualizações dos dados"""
    try:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle(titulo, fontsize=16, fontweight='bold')
        
        # Gráfico 1: Série temporal (se houver data)
        if 'data' in df.columns:
            df.set_index('data')[coluna_numerica].plot(ax=axes[0, 0], title='Série Temporal')
            axes[0, 0].set_ylabel('Valor')
        
        # Gráfico 2: Distribuição (histograma)
        axes[0, 1].hist(df[coluna_numerica], bins=30, edgecolor='black')
        axes[0, 1].set_title('Distribuição dos Valores')
        axes[0, 1].set_xlabel(coluna_numerica)
        
        # Gráfico 3: Box plot
        axes[1, 0].boxplot(df[coluna_numerica])
        axes[1, 0].set_title('Box Plot - Outliers')
        
        # Gráfico 4: Estatísticas resumidas
        axes[1, 1].axis('off')
        stats_text = f"""
        RESUMO ESTATÍSTICO
        ─────────────────
        Média: {df[coluna_numerica].mean():.2f}
        Máximo: {df[coluna_numerica].max():.2f}
        Mínimo: {df[coluna_numerica].min():.2f}
        Mediana: {df[coluna_numerica].median():.2f}
        Total de registros: {len(df)}
        """
        axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, family='monospace')
        
        plt.tight_layout()
        plt.savefig('relatorio_dados.png', dpi=300, bbox_inches='tight')
        print("✓ Gráfico salvo: relatorio_dados.png")
        plt.show()
    except Exception as e:
        print(f"✗ Erro ao criar gráficos: {e}")

# 5. ARMAZENAR EM BANCO DE DADOS
def armazenar_banco(df, cnx):
    """Armazena dados no MySQL"""
    try:
        cursor = cnx.cursor()
        
        # Criar tabela se não existir
        criar_tabela = """
        CREATE TABLE IF NOT EXISTS dados_gov (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255),
            valor FLOAT,
            data_coleta DATETIME,
            INDEX idx_data (data_coleta)
        )
        """
        cursor.execute(criar_tabela)
        
        # Inserir dados
        inserir = "INSERT INTO dados_gov (nome, valor, data_coleta) VALUES (%s, %s, %s)"
        
        for _, row in df.iterrows():
            cursor.execute(inserir, (
                str(row.get('nome', 'N/A')),
                float(row.get('valor', 0)) if pd.notna(row.get('valor')) else 0,
                datetime.now()
            ))
        
        cnx.commit()
        print(f"✓ {cursor.rowcount} registros armazenados no banco")
        cursor.close()
    except Exception as e:
        print(f"✗ Erro ao armazenar no banco: {e}")

# 6. FILTRAR DADOS POR PERÍODO
def filtrar_por_periodo(df, dias=365*10):
    """Filtra dados dos últimos N dias"""
    if 'data' in df.columns:
        limite = datetime.now() - timedelta(days=dias)
        df_filtrado = df[df['data'] >= limite]
        print(f"✓ Filtrado para últimos {dias} dias: {len(df_filtrado)} registros")
        return df_filtrado
    return df

# 7. PIPELINE COMPLETO
def executar_pipeline():
    """Executa todo o pipeline"""
    print("=" * 50)
    print("🚀 INICIANDO PIPELINE DE DADOS GOVERNAMENTAIS")
    print("=" * 50)
    
    # Etapa 1: Coletar
    print("\n[1/6] Coletando dados...")
    dados = coletar_dados()
    if dados is None:
        return
    
    # Etapa 2: Processar
    print("\n[2/6] Processando dados...")
    df = processar_dados(dados)
    if df is None or df.empty:
        return
    
    # Etapa 3: Filtrar por período
    print("\n[3/6] Filtrando por período (últimos 10 anos)...")
    df = filtrar_por_periodo(df, dias=365*10)
    
    # Etapa 4: Calcular estatísticas
    print("\n[4/6] Calculando estatísticas...")
    coluna_numerica = df.select_dtypes(include=['number']).columns[0] if len(df.select_dtypes(include=['number']).columns) > 0 else None
    if coluna_numerica:
        calcular_estatisticas(df, coluna_numerica)
    
    # Etapa 5: Criar gráficos
    print("\n[5/6] Gerando visualizações...")
    if coluna_numerica:
        criar_graficos(df, coluna_numerica, titulo="Análise de Dados Governamentais")
    
    # Etapa 6: Armazenar no banco
    print("\n[6/6] Armazenando no banco de dados...")
    try:
        cnx = conectar_banco()
        armazenar_banco(df, cnx)
        cnx.close()
    except Exception as e:
        print(f"✗ Erro na conexão com banco: {e}")
    
    print("\n" + "=" * 50)
    print("✓ PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 50)

# Executar
if __name__ == "__main__":
    executar_pipeline()
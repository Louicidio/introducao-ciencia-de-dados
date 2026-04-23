import pandas as pd
import glob
import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from io import BytesIO

def extrair_dados_ods(caminho_ods):
    """Extrai dados de um arquivo ODS lendo diretamente o XML"""
    try:
        with zipfile.ZipFile(caminho_ods, 'r') as zip_ref:
            # Ler o arquivo content.xml
            with zip_ref.open('content.xml') as xml_file:
                tree = ET.parse(xml_file)
                root = tree.getroot()
        
        # Namespaces do ODS
        namespaces = {
            'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
            'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
            'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0'
        }
        
        # Encontrar a primeira tabela
        tabelas = root.findall('.//table:table', namespaces)
        if not tabelas:
            return None
        
        tabela = tabelas[0]
        linhas = tabela.findall('table:table-row', namespaces)
        
        dados = []
        for linha in linhas:
            celulas = linha.findall('table:table-cell', namespaces)
            row_data = []
            
            for celula in celulas:
                # Obter o valor de texto
                parafos = celula.findall('.//text:p', namespaces)
                valor = ""
                for parafo in parafos:
                    # Concatenar todo o texto dentro de <text:p>
                    texto_parts = []
                    if parafo.text:
                        texto_parts.append(parafo.text)
                    for elem in parafo:
                        if elem.text:
                            texto_parts.append(elem.text)
                    valor += "".join(texto_parts)
                
                row_data.append(valor)
            
            if any(row_data):  # Só adiciona se não está completamente vazia
                dados.append(row_data)
        
        if dados:
            return pd.DataFrame(dados)
        return None
        
    except Exception as e:
        return None

# Diretório de trabalho
caminho = Path(r"C:\Users\Luis Eduardo\Desktop\2026\Introdu-o-Ci-ncia-de-dados\UnificarBanco2")
arquivos_ods = sorted(glob.glob(str(caminho / "*.ods")))

print(f"[INFO] Encontrados {len(arquivos_ods)} arquivos ODS\n")

dfs = []
erros = []

for i, arquivo_ods in enumerate(arquivos_ods, 1):
    nome = Path(arquivo_ods).name
    try:
        print(f"[{i:2d}/{len(arquivos_ods)}] {nome:<15} ", end="", flush=True)
        
        # Extrair dados diretamente do XML
        df = extrair_dados_ods(arquivo_ods)
        
        if df is not None and len(df) > 0:
            dfs.append(df)
            print(f" ✓ {len(df):5d} linhas")
        else:
            print(f" ✗ vazio")
            erros.append(nome)
            
    except Exception as e:
        print(f" ✗ erro")
        erros.append(f"{nome}: {str(e)[:30]}")

# Resultado
print(f"\n{'='*70}")
print(f"[PROCESSAMENTO] {len(dfs)} arquivos ✓ | {len(erros)} erros ✗")

if dfs:
    # Unificar
    df_final = pd.concat(dfs, ignore_index=True)
    
    output_path = caminho / "unificado.xlsx"
    print(f"\n[RESULTADO]")
    print(f"  ├─ Linhas totais: {len(df_final):,}")
    print(f"  ├─ Colunas: {len(df_final.columns)}")
    print(f"  └─ Salvando {output_path.name}...", end=" ", flush=True)
    
    df_final.to_excel(output_path, index=False, engine='openpyxl')
    print("✓")
    print(f"\n[✓ SUCESSO] Arquivo salvo com sucesso!")
    
    if erros:
        print(f"\n[⚠ AVISO] {len(erros)} arquivo(s) não foram processados:")
        for erro in erros[:5]:
            print(f"  - {erro}")
        if len(erros) > 5:
            print(f"  ... e mais {len(erros)-5}")
else:
    print(f"\n[✗ ERRO] Nenhum arquivo foi processado com sucesso!")

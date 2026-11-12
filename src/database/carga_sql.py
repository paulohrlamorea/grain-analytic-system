import os
import sys
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# --- CONFIGURAÇÕES DE CONEXÃO COM O SQL SERVER ---
# Em produção, prefira carregar estas variáveis de um arquivo .env
DB_SERVER = os.getenv("DB_SERVER", r".\SQLEXPRESS")  # Ex: 'localhost\\SQLEXPRESS' ou IP
DB_DATABASE = os.getenv("DB_DATABASE", "GrainAnalyticDB")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SuaSenhaAqui")
DB_DRIVER = "ODBC Driver 17 for SQL Server"

# Caminho relativo para o arquivo de staging gerado pelo scraper
CAMINHO_EXCEL = os.path.join("data", "staging", "stg_clima_multiequipamento.xlsx")
TABELA_DESTINO = "stg_dados_clima"


def obter_conexao_sqlalchemy():
    """Cria e retorna a engine de conexão com o SQL Server usando Autenticação do Windows."""
    try:
        # Trusted_Connection=yes utiliza a sua conta do Windows logada
        connection_url = (
            f"mssql+pyodbc://@{DB_SERVER}/{DB_DATABASE}"
            f"?driver={DB_DRIVER.replace(' ', '+')}&trusted_connection=yes"
        )
        engine = create_engine(connection_url, fast_executemany=True)
        print(f"[✓] Conexão com o SQL Server ({DB_DATABASE}) estabelecida com sucesso.")
        return engine
    except Exception as e:
        print(f"[!] Erro ao criar a conexão com o banco de dados: {e}")
        sys.exit(1)


def carregar_staging_excel_para_sql(caminho_arquivo: str, tabela_destino: str):
    """Lê o arquivo Excel de staging e faz a carga incremental no SQL Server."""
    if not os.path.exists(caminho_arquivo):
        print(f"[!] Arquivo de staging não encontrado em: {os.path.abspath(caminho_arquivo)}")
        return

    print(f"[*] Lendo o arquivo Excel: {caminho_arquivo}...")
    try:
        df = pd.read_excel(caminho_arquivo, engine="openpyxl")
    except Exception as e:
        print(f"[!] Erro ao ler o arquivo Excel: {e}")
        return

    if df.empty:
        print("[!] O arquivo Excel está vazio. Carga cancelada.")
        return

    # Garante a formatação adequada de tipos antes da ingestão
    df["data_coleta"] = pd.to_datetime(df["data_coleta"]).dt.date
    df["data_processamento_etl"] = pd.to_datetime(df["data_processamento_etl"])

    engine = obter_conexao_sqlalchemy()

    print(f"[*] Iniciando a gravação de {len(df)} registros na tabela '{tabela_destino}'...")

    try:
        with engine.begin() as conexao:
            # Insere os dados no SQL Server. Se a tabela não existir, ela será criada automaticamente.
            # 'append' mantém os dados existentes e adiciona os novos.
            df.to_sql(
                name=tabela_destino,
                con=conexao,
                if_exists="append",
                index=False,
                chunksize=1000
            )
            
        print(f"[✓] Carga concluída com sucesso! {len(df)} linhas inseridas em '{tabela_destino}'.")

    except SQLAlchemyError as e:
        print(f"[!] Erro de SQL durante a ingestão no SQL Server: {e}")
    except Exception as e:
        print(f"[!] Erro inesperado ao gravar no banco de dados: {e}")


# --- EXECUÇÃO DO SCRIPT ---
if __name__ == "__main__":
    # Garante que o script localize a pasta do projeto corretamente
    diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    os.chdir(diretorio_raiz)
    
    carregar_staging_excel_para_sql(CAMINHO_EXCEL, TABELA_DESTINO)
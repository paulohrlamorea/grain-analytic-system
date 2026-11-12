
import os
import sys
from datetime import datetime
from src.scrapers.scraper_clima import extrair_dados_clima_regiao, salvar_em_excel_staging
from src.database.carga_sql import carregar_staging_excel_para_sql

# Aqui funcionará como um ponto de entrada rápida(script legado) para roda exclusivamente a extração de dados climático sem disparar o treinamento de ML

CAMINHO_STAGING_EXCEL = os.path.join("data", "staging", "stg_clima_multiequipamento.xlsx")
TABELA_DESTINO_SQL = "stg_dados_clima"

def executar_etl_clima():
    """Executa isoladamente o scraping de dados climáticos e a carga no SQL Server."""
    print("=" * 60)
    print("  INICIANDO ETL ISOLADO: DADOS CLIMÁTICOS (SCRAPING -> SQL)")
    print("=" * 60)

    estacoes_alvo = ["EST_RS_PASSOFUNDO", "EST_PR_CASCAVEL", "EST_MT_SORRISO"]
    data_consulta = datetime.now().strftime("%Y-%m-%d")

    todos_os_dados = []
    for estacao in estacoes_alvo:
        dados = extrair_dados_clima_regiao(estacao, data_consulta)
        todos_os_dados.extend(dados)

    salvar_em_excel_staging(todos_os_dados, CAMINHO_STAGING_EXCEL)
    carregar_staging_excel_para_sql(CAMINHO_STAGING_EXCEL, TABELA_DESTINO_SQL)

    print("\n[✓] ETL de dados climáticos concluído com sucesso!")

if __name__ == "__main__":
    executar_etl_clima()
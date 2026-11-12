import os
import sys
from datetime import datetime

# Importa as funções dos três módulos da aplicação
from src.scrapers.scraper_clima import extrair_dados_clima_regiao, salvar_em_excel_staging
from src.database.carga_sql import carregar_staging_excel_para_sql
from src.models.train_model import carregar_dados_para_treinamento, treinar_e_avaliar_modelo_multiequipamento

CAMINHO_STAGING_EXCEL = os.path.join("data", "staging", "stg_clima_multiequipamento.xlsx")
TABELA_DESTINO_SQL = "stg_dados_clima"


def executar_pipeline_completa():
    inicio_pipeline = datetime.now()
    print("=" * 70)
    print(f"  INICIANDO PIPELINE COMPLETA - GRAIN ANALYTIC SYSTEM")
    print(f"  Data/Hora: {inicio_pipeline.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ---------------------------------------------------------------------------
    # ETAPA 1: WEB SCRAPING
    # ---------------------------------------------------------------------------
    print("\n[ETAPA 1/3] Executando Web Scraping de dados climáticos...")
    estacoes_alvo = ["EST_RS_PASSOFUNDO", "EST_PR_CASCAVEL", "EST_MT_SORRISO"]
    data_consulta = datetime.now().strftime("%Y-%m-%d")

    todos_os_dados = []
    for estacao in estacoes_alvo:
        dados = extrair_dados_clima_regiao(estacao, data_consulta)
        todos_os_dados.extend(dados)

    arquivo_gerado = salvar_em_excel_staging(todos_os_dados, CAMINHO_STAGING_EXCEL)

    if not os.path.exists(arquivo_gerado):
        print("\n[!] ERRO CRÍTICO: O arquivo de staging não foi gerado. Interrompendo pipeline.")
        sys.exit(1)

    # ---------------------------------------------------------------------------
    # ETAPA 2: INGESTÃO NO SQL SERVER
    # ---------------------------------------------------------------------------
    print("\n[ETAPA 2/3] Executando ingestão de dados no SQL Server...")
    carregar_staging_excel_para_sql(CAMINHO_STAGING_EXCEL, TABELA_DESTINO_SQL)

    # ---------------------------------------------------------------------------
    # ETAPA 3: TREINAMENTO E VALIDAÇÃO DE MACHINE LEARNING
    # ---------------------------------------------------------------------------
    print("\n[ETAPA 3/3] Executando pipeline de Machine Learning (GroupKFold)...")
    df_modelo = carregar_dados_para_treinamento()
    treinar_e_avaliar_modelo_multiequipamento(df_modelo)

    # ---------------------------------------------------------------------------
    # FINALIZAÇÃO
    # ---------------------------------------------------------------------------
    tempo_execucao = datetime.now() - inicio_pipeline
    print("\n" + "=" * 70)
    print(f"  [✓] PIPELINE TOTAL CONCLUÍDA COM SUCESSO EM {tempo_execucao.total_seconds():.2f} SEGUNDOS!")
    print("=" * 70)


if __name__ == "__main__":
    executar_pipeline_completa()
# 🌾 Grain Analytic System

Solução end-to-end de Engenharia de Dados, Machine Learning e Business Intelligence voltada para o monitoramento em tempo real da qualidade e umidade de grãos em unidades de beneficiamento e armazenagem.

## 🎯 Visão Geral do Projeto

O Grain Analytic System integra dados meteorológicos externos (via Web Scraping) e leituras físico-químicas de sensores ópticos/NIR de múltiplos equipamentos (EQ_CASCAVEL_01, EQ_PASSOFUNDO_01, EQ_RIOVERDE_01, EQ_SORRISO_01) para classificar grãos automaticamente e apoiar a tomada de decisão operacional.

Principais Funcionalidades

Pipeline ETL Automatizado: Extração de dados climáticos, higienização em camada staging (Excel/Pandas) e ingestão estruturada no SQL Server.

Modelagem Dimensional (Star Schema): Arquitetura de banco de dados relacional otimizada para consultas analíticas e alimentação de modelos preditivos.

Machine Learning com Validação Cruzada por Grupo (GroupKFold): Classificação preditiva de qualidade dos grãos (INTEIRO, ARDIDO, IMATURO, PICADO) garantindo generalização entre equipamentos distintos sem vazamento de dados, atingindo 99,5% de acurácia média.

Dashboard Executivo & UI/UX: Interface interativa no Power BI Desktop com design personalizado prototipado no Figma.

🏗️ Arquitetura e Fluxo de Dados

[Web Scraping Climático] ──┐
                           ├──► [Camada Staging (.xlsx)] ──► [SQL Server (GrainAnalyticDB)] ──┬──► [Modelo ML (Scikit-Learn)]
[Simulador de Sensores] ───┘                                                                  └──► [Dashboard Power BI + Figma]


🛠️ Tecnologias Utilizadas

Linguagem & ETL: Python 3.x (pandas, numpy, SQLAlchemy, pyodbc, requests, beautifulsoup4)

Machine Learning: scikit-learn (GroupKFold)

Banco de Dados: Microsoft SQL Server (GrainAnalyticDB)

Business Intelligence: Power BI Desktop (DAX, Modelagem Estrela)

UI/UX Design: Figma (Prototipagem de layout e identidade visual)

📂 Estrutura do Repositório

grain-analytic-system/
├── assets/
│   └── dashboard_preview.png          # Captura de tela do painel final
├── data/
│   └── staging/
│       └── stg_clima_multiequipamento.xlsx  # Arquivo intermediário de staging
├── src/
│   ├── database/
│   │   ├── carga_sql.py               # Ingestão de dados de staging para o SQL Server
│   │   ├── gerar_leituras_reais.py    # Simulador de padrões físicos dos sensores
│   │   └── schema_grain_analytic.sql  # Scripts DDL (Staging, Dimensões e Fatos)
│   ├── models/
│   │   └── train_model.py             # Treinamento e validação do modelo de classificação
│   └── scrapers/
│       └── scraper_clima.py           # Coleta e higienização de dados meteorológicos
├── dashboard/
│   └── grain_analytic.pbix            # Arquivo do projeto Power BI
├── etl_clima_scraping.py              # Execução isolada do pipeline climático
├── main.py                            # Orquestrador principal da pipeline
├── requirements.txt                   # Dependências do projeto
└── README.md                          # Documentação do projeto


🗄️ Modelo de Dados (SQL Server)

O banco de dados GrainAnalyticDB foi estruturado seguindo boas práticas de Data Warehouse:

dbo.stg_dados_clima: Recepção bruta e rastreabilidade (data_processamento_etl) das coletas climáticas.

dbo.dim_equipamento: Cadastro das unidades físicas, modelos e versões de firmware.

dbo.dim_localizacao: Dados geográficos e regiões agrícolas das unidades.

dbo.fato_leitura_grao: Registro granular das leituras de umidade (%), densidade (g/L), índice refratativo e classificação predita.

dbo.fato_clima_diario: Consolidação climática diária por localização.

📊 Indicadores e Visualizações (Power BI)

O painel foi estruturado para leitura rápida da operação, com filtros dinâmicos por Equipamento e Data de Leitura:

KPIs Principais:

Total de Amostras: Contagem total de leituras registradas (COUNTROWS).

Umidade Média %: Média percentual de umidade dos lotes analisados (AVERAGE).

% Grãos Inteiros: Proporção de grãos dentro do padrão de qualidade aceitável.

% Grãos Avariados: Proporção consolidada de defeitos (ARDIDO, IMATURO e PICADO).

Análises Visuais:

Distribuição por Classe de Grão: Gráfico de rosca com proporção volumétrica e percentual por classificação.

Média de Umidade ao Longo do Tempo: Gráfico de área monitorando variações temporais e picos de umidade.

Volume de Amostra por Equipamento: Comparativo de processamento entre as unidades monitoradas.

Últimas Leituras de Grãos: Tabela analítica detalhada com umidade, densidade e classe predita por registro.

🚀 Como Executar o Projeto

Clone o repositório:

git clone https://github.com/paulohrlamorea/grain-analytic-system.git
cd grain-analytic-system


Instale as dependências:

pip install -r requirements.txt


Configure o Banco de Dados:

Execute o script src/database/schema_grain_analytic.sql no SQL Server Management Studio (SSMS) para criar o banco GrainAnalyticDB e suas tabelas.

Ajuste a variável DB_SERVER em src/database/carga_sql.py conforme sua instância local (ex: .\SQLEXPRESS).

Popule os dados e execute a pipeline:

python -m src.database.gerar_leituras_reais
python main.py


Visualize o Dashboard:

Abra o arquivo .pbix no Power BI Desktop e atualize a fonte de dados apontando para a sua instância local do SQL Server.


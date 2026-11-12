-- ===============================================================================
-- PROJETO: Grain Analytic System
-- BANCO DE DADOS: SQL Server
-- OBJETIVO: Estrutura de Staging, Dimensões e Fatos para Análise e ML
-- ===============================================================================

-- 1. Criação do Banco de Dados (opcional, execute se ainda não existir)
-- CREATE DATABASE GrainAnalyticDB;
-- GO
-- USE GrainAnalyticDB;
-- GO

-- -------------------------------------------------------------------------------
-- CAMADA DE STAGING (Recebe os dados brutos importados do Excel/Web Scraping)
-- -------------------------------------------------------------------------------
IF OBJECT_ID('dbo.stg_dados_clima', 'U') IS NOT NULL 
    DROP TABLE dbo.stg_dados_clima;
GO

CREATE TABLE dbo.stg_dados_clima (
    id_staging INT IDENTITY(1,1) PRIMARY KEY,
    codigo_estacao VARCHAR(50) NOT NULL,
    data_coleta DATE NOT NULL,
    horario VARCHAR(10) NULL,
    temperatura_media_c DECIMAL(5,2) NULL,
    umidade_relativa_pct DECIMAL(5,2) NULL,
    precipitacao_mm DECIMAL(6,2) NULL,
    pressao_atmosferica_hpa DECIMAL(7,2) NULL,
    data_processamento_etl DATETIME DEFAULT GETDATE()
);
GO

-- -------------------------------------------------------------------------------
-- CAMADA DIMENSIONAL (Modelagem Estrela / Snowflake)
-- -------------------------------------------------------------------------------

-- Dimensão: Localização/Região das Unidades e Estações Meteorológicas
IF OBJECT_ID('dbo.dim_localizacao', 'U') IS NOT NULL 
    DROP TABLE dbo.dim_localizacao;
GO

CREATE TABLE dbo.dim_localizacao (
    sk_localizacao INT IDENTITY(1,1) PRIMARY KEY,
    codigo_ibge VARCHAR(20) NOT NULL UNIQUE,
    municipio VARCHAR(100) NOT NULL,
    uf CHAR(2) NOT NULL,
    regiao_agricola VARCHAR(100) NULL,
    latitude DECIMAL(9,6) NULL,
    longitude DECIMAL(9,6) NULL,
    data_cadastro DATETIME DEFAULT GETDATE()
);
GO

-- Dimensão: Equipamentos (Grain Analytic System)
IF OBJECT_ID('dbo.dim_equipamento', 'U') IS NOT NULL 
    DROP TABLE dbo.dim_equipamento;
GO

CREATE TABLE dbo.dim_equipamento (
    sk_equipamento INT IDENTITY(1,1) PRIMARY KEY,
    codigo_equipamento VARCHAR(50) NOT NULL UNIQUE, -- Identificador único da unidade física
    modelo VARCHAR(50) NOT NULL DEFAULT 'Grain Analytic V1',
    versao_firmware VARCHAR(20) NULL,
    sk_localizacao INT NOT NULL,
    status_operacional VARCHAR(20) DEFAULT 'ATIVO', -- ATIVO, MANUTENCAO, INATIVO
    data_instalacao DATE NULL,
    ultima_calibracao DATE NULL,
    CONSTRAINT FK_equipamento_localizacao FOREIGN KEY (sk_localizacao) 
        REFERENCES dbo.dim_localizacao(sk_localizacao)
);
GO

-- -------------------------------------------------------------------------------
-- CAMADA FATO (Tabelas de Eventos e Medições)
-- -------------------------------------------------------------------------------

-- Fato: Medições Climáticas Consolidadas por Região
IF OBJECT_ID('dbo.fato_clima_diario', 'U') IS NOT NULL 
    DROP TABLE dbo.fato_clima_diario;
GO

CREATE TABLE dbo.fato_clima_diario (
    sk_fato_clima BIGINT IDENTITY(1,1) PRIMARY KEY,
    sk_localizacao INT NOT NULL,
    data_medicao DATE NOT NULL,
    temperatura_media_c DECIMAL(5,2) NULL,
    temperatura_max_c DECIMAL(5,2) NULL,
    temperatura_min_c DECIMAL(5,2) NULL,
    umidade_relativa_pct DECIMAL(5,2) NULL,
    precipitacao_acumulada_mm DECIMAL(6,2) NULL,
    pressao_atmosferica_hpa DECIMAL(7,2) NULL,
    CONSTRAINT FK_fatoclima_localizacao FOREIGN KEY (sk_localizacao) 
        REFERENCES dbo.dim_localizacao(sk_localizacao),
    CONSTRAINT UK_clima_local_data UNIQUE (sk_localizacao, data_medicao)
);
GO

-- Fato: Leituras e Classificação de Grãos de Soja pelo Equipamento
IF OBJECT_ID('dbo.fato_leitura_grao', 'U') IS NOT NULL 
    DROP TABLE dbo.fato_leitura_grao;
GO

CREATE TABLE dbo.fato_leitura_grao (
    sk_fato_leitura BIGINT IDENTITY(1,1) PRIMARY KEY,
    sk_equipamento INT NOT NULL,
    sk_localizacao INT NOT NULL,
    id_lote VARCHAR(50) NOT NULL,
    data_hora_leitura DATETIME NOT NULL,
    
    -- Sensores Físicos / Ópticos do Equipamento
    umidade_grao_pct DECIMAL(5,2) NOT NULL,
    densidade_g_l DECIMAL(6,2) NULL,
    indice_refratativo DECIMAL(8,5) NULL,
    espectro_absorbancia_raw NVARCHAR(MAX) NULL, -- JSON com o vetor de sinais NIR/ópticos
    
    -- Resultados da Classificação
    classe_grao_predita VARCHAR(50) NOT NULL, -- Ex: 'INTEIRO', 'ARDIDO', 'PICADO', 'IMATURO'
    confianca_modelo DECIMAL(5,4) NULL,       -- Probabilidade da classe (ex: 0.9542)
    classe_grao_real VARCHAR(50) NULL,        -- Label humano de validação (se houver auditoria)
    
    CONSTRAINT FK_leituragrao_equipamento FOREIGN KEY (sk_equipamento) 
        REFERENCES dbo.dim_equipamento(sk_equipamento),
    CONSTRAINT FK_leituragrao_localizacao FOREIGN KEY (sk_localizacao) 
        REFERENCES dbo.dim_localizacao(sk_localizacao)
);
GO

-- -------------------------------------------------------------------------------
-- ÍNDICES DE PERFORMANCE (Para consultas analíticas e extrações do Python)
-- -------------------------------------------------------------------------------
CREATE INDEX IX_fato_clima_data ON dbo.fato_clima_diario(data_medicao);
CREATE INDEX IX_fato_leitura_equip_data ON dbo.fato_leitura_grao(sk_equipamento, data_hora_leitura);
CREATE INDEX IX_fato_leitura_lote ON dbo.fato_leitura_grao(id_lote);
GO
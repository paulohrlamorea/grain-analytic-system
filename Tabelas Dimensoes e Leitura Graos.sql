USE GrainAnalyticDB;
GO

-- 1. Tabela Dimensão Equipamento
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'dim_equipamento')
BEGIN
    CREATE TABLE dbo.dim_equipamento (
        sk_equipamento INT PRIMARY KEY,
        codigo_equipamento VARCHAR(50) NOT NULL UNIQUE,
        modelo VARCHAR(50) NOT NULL,
        versao_firmware VARCHAR(20) NOT NULL
    );
END
GO

-- 2. Tabela Fato de Leitura de Grãos
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'fato_leitura_grao')
BEGIN
    CREATE TABLE dbo.fato_leitura_grao (
        sk_fato_leitura INT IDENTITY(1,1) PRIMARY KEY,
        sk_equipamento INT NOT NULL,
        data_hora_leitura DATETIME NOT NULL,
        umidade_grao_pct DECIMAL(5,2) NOT NULL,
        densidade_g_l DECIMAL(6,2) NOT NULL,
        indice_refratativo DECIMAL(7,5) NOT NULL,
        classe_grao_predita VARCHAR(30) NOT NULL,
        score_confianca DECIMAL(5,4) NOT NULL,
        CONSTRAINT FK_fato_leitura_equipamento FOREIGN KEY (sk_equipamento) REFERENCES dbo.dim_equipamento(sk_equipamento)
    );
END
GO
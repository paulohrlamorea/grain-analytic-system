
-- 1. Cria a base de dados do projeto 
CREATE DATABASE GrainAnalyticDB;
GO

USE GrainAnalyticDB;
GO

-- 2. Tabela de Staging
CREATE TABLE dbo.stg_dados_clima (               --Cria a tabela Staging(camada intermediária) casa ela não exista
	id_staging INT IDENTITY(1,1) PRIMARY KEY,    --Chave Primária, ele vai gerar um número único p/ cada registro inserido
	codigo_estacao VARCHAR(50) NOT NULL,         --Armazena texto 50 caracteres, obrigatório ter os 50 caract
    data_coleta DATE NOT NULL,                   --Guarda data formato AAAA-MM-DD Obrigatório sem limites de caract
	horario VARCHAR(10) NULL,                    --Guarda o horário texto simples, de até 10 caracteres
	temperatura_media_c DECIMAL(5,2) NULL,       --N° decimal com 5 digítos no total de 2 casas decimais, NULL-opcional 
	umidade_relativa_pct DECIMAL(5,2) NULL,      --N° decimal com 5 digítos no total de 2 casas decimais, NULL-opcional
	precipitacao_mm DECIMAL(6,2) NULL,           --N° decimal com 6 digítos no total de 2 casas decimais, NULL-opcional
	pressao_atmosferica_hp DECIMAL(7,2) NULL,    --N° decimal com 7 digítos no total de 2 casas decimais, NULL-opcional

	data_processamento_etl DATETIME DEFAULT GETDATE()       --Registra automaticamente data/hora exatas sistema  GETDATE() no momento em que a linha for inserida
)
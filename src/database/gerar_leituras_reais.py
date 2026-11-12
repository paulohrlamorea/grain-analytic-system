import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.database.carga_sql import obter_conexao_sqlalchemy


def gerar_dados_leituras_soja_realistas(n_registros_por_equipamento: int = 500) -> pd.DataFrame:
    """Gera um conjunto de dados altamente realista simulando medições físicas de grãos de soja

    em 4 unidades do Grain Analytic System.
    """
    np.random.seed(42)

    equipamentos = [
        {"sk_equipamento": 1, "codigo": "EQ_PASSOFUNDO_01", "ruido_sensor": 0.02},
        {"sk_equipamento": 2, "codigo": "EQ_CASCAVEL_01", "ruido_sensor": 0.05},
        {"sk_equipamento": 3, "codigo": "EQ_SORRISO_01", "ruido_sensor": 0.03},
        {"sk_equipamento": 4, "codigo": "EQ_RIOVERDE_01", "ruido_sensor": 0.04},
    ]

    classes = ["INTEIRO", "ARDIDO", "IMATURO", "PICADO"]
    probabilidade_classes = [0.70, 0.10, 0.12, 0.08]  # Distribuição típica de safra

    registros = []
    data_base = datetime.now() - timedelta(days=30)

    for equip in equipamentos:
        for i in range(n_registros_por_equipamento):
            classe = np.random.choice(classes, p=probabilidade_classes)
            ruido = equip["ruido_sensor"]

            # Parâmetros Físicos por Classe + Ruído Calibrado do Equipamento
            if classe == "INTEIRO":
                umidade = np.random.normal(12.5, 0.8) + np.random.normal(0, ruido)
                densidade = np.random.normal(760.0, 12.0) + np.random.normal(0, ruido * 10)
                refratativo = np.random.normal(1.3340, 0.001) + np.random.normal(0, ruido * 0.01)

            elif classe == "ARDIDO":
                umidade = np.random.normal(19.2, 1.2) + np.random.normal(0, ruido)
                densidade = np.random.normal(670.0, 18.0) + np.random.normal(0, ruido * 10)
                refratativo = np.random.normal(1.3410, 0.002) + np.random.normal(0, ruido * 0.01)

            elif classe == "IMATURO":
                umidade = np.random.normal(16.5, 1.0) + np.random.normal(0, ruido)
                densidade = np.random.normal(710.0, 15.0) + np.random.normal(0, ruido * 10)
                refratativo = np.random.normal(1.3375, 0.0015) + np.random.normal(0, ruido * 0.01)

            else:  # PICADO
                umidade = np.random.normal(13.8, 1.1) + np.random.normal(0, ruido)
                densidade = np.random.normal(630.0, 22.0) + np.random.normal(0, ruido * 10)
                refratativo = np.random.normal(1.3315, 0.002) + np.random.normal(0, ruido * 0.01)

            data_coleta = data_base + timedelta(minutes=i * 15)

            registros.append({
                "sk_equipamento": equip["sk_equipamento"],
                "data_hora_leitura": data_coleta.strftime("%Y-%m-%d %H:%M:%S"),
                "umidade_grao_pct": round(float(umidade), 2),
                "densidade_g_l": round(float(densidade), 2),
                "indice_refratativo": round(float(refratativo), 5),
                "classe_grao_predita": classe,
                "score_confianca": round(float(np.random.uniform(0.88, 0.99)), 4)
            })

    return pd.DataFrame(registros)


def popular_fato_leitura_sql():
    """Gera e insere os dados realistas na tabela fato_leitura_grao no SQL Server."""
    print("[*] Gerando 2.000 registros de leituras realistas para a tabela fato...")
    df_leituras = gerar_dados_leituras_soja_realistas(n_registros_por_equipamento=500)

    engine = obter_conexao_sqlalchemy()
    print("[*] Conectando ao SQL Server e limpando registros antigos da fato...")

    try:
        with engine.begin() as conexao:
            # Garante a inserção prévia da dimensão de equipamentos
            conexao.exec_driver_sql("""
                IF NOT EXISTS (SELECT 1 FROM dbo.dim_equipamento WHERE sk_equipamento = 1)
                BEGIN
                    INSERT INTO dbo.dim_equipamento (sk_equipamento, codigo_equipamento, modelo, versao_firmware)
                    VALUES 
                        (1, 'EQ_PASSOFUNDO_01', 'GrainAnalytic Pro', 'v2.1'),
                        (2, 'EQ_CASCAVEL_01', 'GrainAnalytic Pro', 'v2.1'),
                        (3, 'EQ_SORRISO_01', 'GrainAnalytic Pro', 'v2.2'),
                        (4, 'EQ_RIOVERDE_01', 'GrainAnalytic Lite', 'v1.9');
                END
            """)

            # Carrega a tabela fato
            df_leituras.to_sql(
                name="fato_leitura_grao",
                con=conexao,
                if_exists="append",
                index=False,
                chunksize=500
            )

        print(f"[✓] Sucesso! {len(df_leituras)} leituras inseridas na tabela 'fato_leitura_grao'.")
    except Exception as e:
        print(f"[!] Erro ao inserir leituras no SQL Server: {e}")


if __name__ == "__main__":
    popular_fato_leitura_sql()
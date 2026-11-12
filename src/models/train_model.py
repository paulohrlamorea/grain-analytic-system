import os
import sys
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

# Scikit-Learn para modelagem e validação
from sklearn.model_selection import GroupKFold    #garante que as leituras de um mesmo equipa., NUNCA fiquem Divididas entre treino e teste ao mesmo tempo
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Módulo interno de conexão com o banco de dados
from src.database.carga_sql import obter_conexao_sqlalchemy


def carregar_dados_para_treinamento() -> pd.DataFrame:
    """Busca os dados de leituras de grãos e equipamentos do SQL Server."""
    print("[*] Conectando ao SQL Server para extrair a base de treinamento...")
    engine = obter_conexao_sqlalchemy()
    
    # Query SQL juntando as medições com a dimensão de equipamento
    query = """
    SELECT 
        g.sk_fato_leitura,
        e.codigo_equipamento,
        g.umidade_grao_pct,
        g.densidade_g_l,
        g.indice_refratativo,
        g.classe_grao_predita AS classe_alvo
    FROM dbo.fato_leitura_grao g
    INNER JOIN dbo.dim_equipamento e ON g.sk_equipamento = e.sk_equipamento
    """
    
    try:
        with engine.connect() as conexao:
            df = pd.read_sql(query, conexao)
        print(f"[✓] Base de dados carregada com sucesso: {len(df)} registros.")
        return df
    except Exception as e:
        print(f"[!] Aviso: Não foi possível ler da base SQL ({e}). Gerando dados sintéticos para demonstração...")
        return gerar_dados_sinteticos_multiequipamento()


def gerar_dados_sinteticos_multiequipamento(n_samples: int = 1200) -> pd.DataFrame:
    """Gera um dataset sintético representando 4 unidades do Grain Analytic System."""
    np.random.seed(42)
    equipamentos = ["EQ_PASSOFUNDO_01", "EQ_CASCAVEL_01", "EQ_SORRISO_01", "EQ_RIOVERDE_01"]
    classes = ["INTEIRO", "ARDIDO", "IMATURO", "PICADO"]

    dados = []
    for i in range(n_samples):
        equip = np.random.choice(equipamentos)
        classe = np.random.choice(classes)
        
        # Simula variações de sensores com base na classe do grão
        umidade = np.random.normal(13.0 if classe == "INTEIRO" else 18.0, 1.5)
        densidade = np.random.normal(750.0 if classe == "INTEIRO" else 680.0, 20.0)
        refratativo = np.random.normal(1.3330, 0.005)
        
        dados.append({
            "sk_fato_leitura": i + 1,
            "codigo_equipamento": equip,
            "umidade_grao_pct": round(umidade, 2),
            "densidade_g_l": round(densidade, 2),
            "indice_refratativo": round(refratativo, 5),
            "classe_alvo": classe
        })
    
    return pd.DataFrame(dados)


def treinar_e_avaliar_modelo_multiequipamento(df: pd.DataFrame):
    """Executa a Validação Cruzada por Equipamento (GroupKFold) e treina o modelo final."""
    print("\n" + "=" * 70)
    print("  INICIANDO TREINAMENTO E VALIDAÇÃO DE GENERALIZAÇÃO INTER-EQUIPAMENTOS")
    print("=" * 70)

    # 1. Separação de Features (X), Rótulo Alvo (y) e Grupos (Equipamentos)
    features = ["umidade_grao_pct", "densidade_g_l", "indice_refratativo"]
    X = df[features]
    y = df["classe_alvo"]
    grupos = df["codigo_equipamento"]

    equipamentos_unicos = grupos.unique()
    n_splits = len(equipamentos_unicos)

    print(f"[*] Total de equipamentos identificados na base: {n_splits}")
    print(f"[*] Equipamentos: {list(equipamentos_unicos)}")

    # 2. Configuração do GroupKFold
    gkf = GroupKFold(n_splits=n_splits)

    # Definimos um Pipeline com Padronização (Scaler) + Classificador Random Forest
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    acuracias_folds = []
    f1_folds = []

    print("\n--- AVALIAÇÃO DE GENERALIZAÇÃO POR DOBLA (EQUIPAMENTO DE TESTE) ---")

    # 3. Loop de Validação Cruzada por Grupo (Equipamento)
    for fold, (train_idx, test_idx) in enumerate(gkf.split(X, y, groups=grupos), start=1):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        equipamento_teste = grupos.iloc[test_idx].iloc[0]

        # Treina no conjunto de equipamentos de treino
        pipeline.fit(X_train, y_train)

        # Testa no equipamento não visto no treino
        y_pred = pipeline.predict(X_test)

        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")
        
        acuracias_folds.append(acc)
        f1_folds.append(f1)

        print(f"[Fold {fold}] Equipamento de Teste: {equipamento_teste:<18} | Acurácia: {acc:.4f} | F1-Score: {f1:.4f}")

    print("\n--- RESUMO DA AVALIAÇÃO DE GENERALIZAÇÃO ---")
    print(f"Acurácia Média Inter-Equipamentos: {np.mean(acuracias_folds):.4f} (± {np.std(acuracias_folds):.4f})")
    print(f"F1-Score Médio Inter-Equipamentos:  {np.mean(f1_folds):.4f} (± {np.std(f1_folds):.4f})")

    # 4. Treinamento Final no Dataset Completo para Exportação do Modelo Global
    print("\n[*] Treinando o Modelo Global final com 100% da base de dados...")
    pipeline.fit(X, y)

    # 5. Salva o Modelo Treinado na pasta de Artefatos
    pasta_modelos = os.path.join("src", "models", "artefatos")
    os.makedirs(pasta_modelos, exist_ok=True)
    caminho_modelo = os.path.join(pasta_modelos, "modelo_global_soja.pkl")

    joblib.dump(pipeline, caminho_modelo)
    print(f"[✓] Modelo Global treinado e exportado com sucesso para: '{os.path.abspath(caminho_modelo)}'")


if __name__ == "__main__":
    df_dados = carregar_dados_para_treinamento()
    treinar_e_avaliar_modelo_multiequipamento(df_dados)

# O objetivo aqui é demonstrar a capacidade de generalizar entre diferentes unidades físicas do equipamento.
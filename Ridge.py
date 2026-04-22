import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV

def treinar_modelo_ridge(portas_treino, portas_teste):
    # ========================================================
    # 1. PREPARAÇÃO DOS DADOS DE TREINO (As 48 portas)
    # ========================================================
    X_train_list, y_train_list = [], []
    
    for porta_id, df_porta in portas_treino:
        df_features = df_porta.copy() 
        
        # Criamos o gabarito (Target) porque sabemos que as portas de treino falharam no final
        ciclo_da_falha = df_features['Ciclo'].max()
        target = ciclo_da_falha - df_features['Ciclo']
        
        features = df_features.drop(columns=['Porta_ID', 'Ciclo', 'Ciclo_Relativo'], errors='ignore')
        X_train_list.append(features)
        y_train_list.append(target)

    X_train_full = pd.concat(X_train_list, ignore_index=True).fillna(0)
    y_train_full = np.concatenate(y_train_list)

    # ========================================================
    # 2. PREPARAÇÃO DOS DADOS DE TESTE (As 19 portas)
    # ========================================================
    X_test_list = []
    ids_test_final, ciclos_test_final = [], []
    
    for porta_id, df_porta in portas_teste:
        df_features = df_porta.copy() 
        
        # ATENÇÃO: Não tem "target" aqui! O objetivo é prevê-lo.
        features = df_features.drop(columns=['Porta_ID', 'Ciclo', 'Ciclo_Relativo'], errors='ignore')
        
        X_test_list.append(features)
        ids_test_final.extend([porta_id] * len(df_features))
        ciclos_test_final.extend(df_features['Ciclo'].tolist())

    X_test_final = pd.concat(X_test_list, ignore_index=True).fillna(0)

    # ========================================================
    # 3. TREINAMENTO E PREVISÃO
    # ========================================================
    print(f"\nTreinando RidgeCV com {len(portas_treino)} portas...")
    modelo = RidgeCV(alphas=np.logspace(-3, 4, 100), cv=5)
    modelo.fit(X_train_full, y_train_full)
    
    print(f"Prevendo RUL para {len(portas_teste)} portas de Teste...")
    previsoes = modelo.predict(X_test_final)
    
    return modelo, previsoes, ids_test_final, ciclos_test_final
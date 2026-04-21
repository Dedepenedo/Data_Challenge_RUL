# Arquivo: treinamento_ridge.py
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, RidgeCV

def treinar_modelo_ridge(todas_as_portas):
    # Divisão exata solicitada
    ids_treino = [2, 4, 5, 6, 8, 10, 11, 14, 15, 16, 18, 19, 22, 23, 24, 26, 29, 30, 31, 32, 33, 34, 35, 36, 39, 41, 42, 43, 44, 45]
    ids_val    = [1, 12, 13, 20, 21, 27, 28, 46, 48]
    ids_teste  = [3, 7, 9, 17, 25, 37, 38, 40, 47]

    # ========================================================
    # 2. SEPARAÇÃO DAS JANELAS (TRAIN, VAL, TEST)
    # ========================================================
    X_train_list, y_train_list = [], []
    X_val_list, y_val_list = [], []
    X_test_list, y_test_list = [], []
    
    ids_test_final = []
    ciclos_test_final = []

    print("Separando os dados nas listas de Treino, Validação e Teste...")

    for porta_id, df_porta in todas_as_portas:
        df_features = df_porta.copy() 
        
        ciclo_da_falha = df_features['Ciclo'].max()
        target = ciclo_da_falha - df_features['Ciclo']
        
        features = df_features.drop(columns=['Porta_ID', 'Ciclo', 'Ciclo_Relativo'], errors='ignore')
        
        if porta_id in ids_treino:
            X_train_list.append(features)
            y_train_list.append(target)
        elif porta_id in ids_val:
            X_val_list.append(features)
            y_val_list.append(target)
        elif porta_id in ids_teste:
            X_test_list.append(features)
            y_test_list.append(target)
            
            ids_test_final.extend([porta_id] * len(df_features))
            ciclos_test_final.extend(df_features['Ciclo'].tolist()) 

    # Concatenando
    X_train = pd.concat(X_train_list, ignore_index=True).fillna(0)
    y_train = pd.concat(y_train_list, ignore_index=True).values

    X_val = pd.concat(X_val_list, ignore_index=True).fillna(0)
    y_val = pd.concat(y_val_list, ignore_index=True).values

    X_test = pd.concat(X_test_list, ignore_index=True).fillna(0)
    y_test = pd.concat(y_test_list, ignore_index=True).values

    # ========================================================
    # 3. TREINAMENTO DO MODELO RIDGE
    # ========================================================
    X_train_full = pd.concat([X_train, X_val], ignore_index=True)
    y_train_full = np.concatenate([y_train, y_val])
    
    print("\nOtimizando hiperparâmetros e treinando o modelo Ridge...")
    
    # O RidgeCV vai testar automaticamente todos estes valores
    # np.logspace(-3, 4, 100) cria 100 valores espaçados entre 0.001 e 10.000
    modelo_ridge_final = RidgeCV(
        alphas=np.logspace(-3, 5, 100), 
        cv=20
    )
    
    # Ele treina, descobre o melhor alpha sozinho e já se ajusta para a versão campeã!
    modelo_ridge_final.fit(X_train_full, y_train_full)
    
    print("✅ Treinamento final concluído!")
    print(f"🏆 Melhor 'alpha' descoberto pelo modelo: {modelo_ridge_final.alpha_:.4f}")
    
    print("✅ Treinamento final concluído!")

    # ========================================================
    # 4. PREVISÕES E RETORNO
    # ========================================================
    previsoes_teste = modelo_ridge_final.predict(X_test)
    
    return modelo_ridge_final, previsoes_teste, y_test, ids_test_final, ciclos_test_final
import os
import pandas as pd
import numpy as np
import pickle


def dataframe_train():
    # Lista mestre para guardar os DataFrames de todas as portas já processadas
    todas_as_portas = [] 

    nomes_colunas = [
        "Duration", "Ref_Pos", "Fbk_Pos", "Ref_Vel", "Fbk_Vel", 
        "Fbk_Hall", "Fbk_Enc", "Vbus", "Temp_Motor", 
        "Corrente_A", "Corrente_B", "Corrente_C", 
        "Temp_Driver", "Volt_A", "Volt_B", "Volt_C"
    ]

    # Loop para N portas
    for i in range(1, 49):  # Range arbitrário, pode ser qualquer quantidade
        print(f"Analisando o Train_{i}...")  
        caminho_pasta = f"Train/Train_{i}/"
        arquivo_rul = f"{caminho_pasta}F_{i}_RUL.csv"
        
        try:
            with open(arquivo_rul, 'r') as f:
                linha = f.readline()
                nCiclos = int(linha.strip())
        except FileNotFoundError:
            print(f"Erro: Arquivo RUL não encontrado na porta {i}")
            continue

        dados_processados = []
        
        # Loop pelos ciclos da porta atual
        for j in range(1, nCiclos + 1):
            
            # ========================================================
            # NOVA LÓGICA DE EXTRAÇÃO DE FEATURES (OPENING E CLOSING)
            # ========================================================
            file_open = f"{caminho_pasta}F_{i}_{j:05d}_Opening.csv"
            file_close = f"{caminho_pasta}F_{i}_{j:05d}_Closing.csv"
            
            # Só prossegue se AMBOS os arquivos existirem
            if not os.path.exists(file_open) or not os.path.exists(file_close):
                continue
                        
            df_open = pd.read_csv(file_open, sep=';', header=None, names=nomes_colunas)
                
            # 1. PREPARAÇÃO E EXTRAÇÃO COM PANDAS
            df_open['Ciclo_ID'] = j
            df_alvo = df_open[['Ciclo_ID', 'Duration', 'Corrente_A', 'Volt_A', 'Fbk_Vel']]
            
            features_estatisticas = df_alvo.groupby('Ciclo_ID').agg({
                'Duration': ['max'], 
                'Corrente_A': ['mean', 'std', 'max', 'min', 'median'], 
                'Volt_A': ['mean', 'std', 'max', 'min'],
                'Fbk_Vel': ['mean', 'std', 'max', 'min']
            }).reset_index()
            
            features_estatisticas.columns = ['_'.join(col).strip('_') for col in features_estatisticas.columns.values]
            
            # 2. MISTURANDO COM SUAS FEATURES MANUAIS
            x_max_atual = df_open['Fbk_Pos'].iloc[0] 
            
            dict_pandas = features_estatisticas.drop(columns=['Ciclo_ID'], errors='ignore').iloc[0].to_dict()
            
            features_manuais = {
                'Ciclo': j,
                'X_max_Atual': x_max_atual,
            }
            
            features_completas = {**features_manuais, **dict_pandas}
            
            dados_processados.append(features_completas)
        
        # Se não processou nenhum dado, pula
        if not dados_processados:
            continue
            
        # Transforma em DataFrame
        df_porta = pd.DataFrame(dados_processados)
        df_porta = df_porta.sort_values(by='Ciclo').reset_index(drop=True)
        
        # ----------------------------------------------
        # LÓGICA DO FDI (MANTIDA INTACTA)
        # ----------------------------------------------
        limite_head = min(15, len(df_porta))
        referencia = df_porta['X_max_Atual'].head(limite_head).median()
        limiar_queda = referencia - 7.1 

        fdi_ciclo = None
        
        for idx, row in df_porta.iterrows():
            if row['X_max_Atual'] < limiar_queda:
                ciclos_futuros = df_porta.loc[idx+1:, 'X_max_Atual']
                recuperacoes = (ciclos_futuros >= referencia)
                teve_recuperacao_sustentada = (recuperacoes.rolling(window=3).sum() == 3).any() 
                
                if teve_recuperacao_sustentada:
                    continue 
                else:
                    fdi_ciclo = row['Ciclo'] - 1
                    break
        
        # Cálculos pós-FDI
        if fdi_ciclo is not None:
            print(f"Train {i} | Último ciclo saudável: {fdi_ciclo}")
            df_porta['Ciclo_Relativo'] = df_porta['Ciclo'] - fdi_ciclo
            df_porta['Distancia_Ref'] = referencia - df_porta['X_max_Atual']
            
            df_porta_filtrada = df_porta[(df_porta['Ciclo_Relativo'] >= -5)]
            todas_as_portas.append((i, df_porta_filtrada))

    return todas_as_portas


import glob
def dafaframe_test():
    print("\nIniciando extração da base de TESTE...")
    todas_as_portas_teste = [] 

    nomes_colunas = [
        "Duration", "Ref_Pos", "Fbk_Pos", "Ref_Vel", "Fbk_Vel", 
        "Fbk_Hall", "Fbk_Enc", "Vbus", "Temp_Motor", 
        "Corrente_A", "Corrente_B", "Corrente_C", 
        "Temp_Driver", "Volt_A", "Volt_B", "Volt_C"
    ]

    for i in range(1, 20):
        print(f"Analisando o Test_{i}...")  
        caminho_pasta = f"Test/Test_{i}/"
        
        # ========================================================
        # DIFERENÇA 1: Contagem cega de ciclos (Sem arquivo RUL)
        # ========================================================
        arquivos_encontrados = glob.glob(f"{caminho_pasta}F_{i}_*_Opening.csv")
        nCiclos = len(arquivos_encontrados)
        
        if nCiclos == 0:
            print(f"Aviso: Nenhum dado encontrado na porta {i}")
            continue

        dados_processados = []
        
        # Limite de busca com uma margem extra caso haja pulo de numeração (buracos)
        for j in range(1, nCiclos + 100):
            file_open = f"{caminho_pasta}F_{i}_{j:05d}_Opening.csv"
            file_close = f"{caminho_pasta}F_{i}_{j:05d}_Closing.csv"
            
            if not os.path.exists(file_open) or not os.path.exists(file_close):
                continue
                        
            df_open = pd.read_csv(file_open, sep=';', header=None, names=nomes_colunas)
                
            df_open['Ciclo_ID'] = j
            df_alvo = df_open[['Ciclo_ID', 'Duration', 'Corrente_A', 'Volt_A', 'Fbk_Vel']]
            
            features_estatisticas = df_alvo.groupby('Ciclo_ID').agg({
                'Duration': ['max'], 
                'Corrente_A': ['mean', 'std', 'max', 'min', 'median'], 
                'Volt_A': ['mean', 'std', 'max', 'min'],
                'Fbk_Vel': ['mean', 'std', 'max', 'min']
            }).reset_index()
            
            features_estatisticas.columns = ['_'.join(col).strip('_') for col in features_estatisticas.columns.values]
            
            x_max_atual = df_open['Fbk_Pos'].iloc[0] 
            dict_pandas = features_estatisticas.drop(columns=['Ciclo_ID'], errors='ignore').iloc[0].to_dict()
            
            features_manuais = {'Ciclo': j, 'X_max_Atual': x_max_atual}
            features_completas = {**features_manuais, **dict_pandas}
            
            dados_processados.append(features_completas)
        
        if not dados_processados:
            continue
            
        df_porta = pd.DataFrame(dados_processados)
        df_porta = df_porta.sort_values(by='Ciclo').reset_index(drop=True)
        
        # LÓGICA DO FDI
        limite_head = min(15, len(df_porta))
        referencia = df_porta['X_max_Atual'].head(limite_head).median()
        limiar_queda = referencia - 7.1 

        fdi_ciclo = None
        for idx, row in df_porta.iterrows():
            if row['X_max_Atual'] < limiar_queda:
                ciclos_futuros = df_porta.loc[idx+1:, 'X_max_Atual']
                recuperacoes = (ciclos_futuros >= referencia)
                teve_recuperacao_sustentada = (recuperacoes.rolling(window=3).sum() == 3).any() 
                
                if not teve_recuperacao_sustentada:
                    fdi_ciclo = row['Ciclo'] - 1
                    break
        
        # ========================================================
        # DIFERENÇA 2: Fallback do FDI e NENHUM CORTE DE DADOS
        # ========================================================
        # Nas portas de teste, o defeito pode ainda não ter começado!
        if fdi_ciclo is None:
            fdi_ciclo = df_porta['Ciclo'].max()
            
        df_porta['Ciclo_Relativo'] = df_porta['Ciclo'] - fdi_ciclo
        df_porta['Distancia_Ref'] = referencia - df_porta['X_max_Atual']
        
        # Salva a porta INTEIRA, sem filtrar >= -5. O modelo precisa ler tudo!
        todas_as_portas_teste.append((i, df_porta.copy()))

    return todas_as_portas_teste
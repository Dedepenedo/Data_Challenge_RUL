import os
import pandas as pd
import numpy as np
import pickle

# Repare que não temos mais nenhum import do tsfresh aqui!
def executar_extracao():
    todas_as_portas = [] # Lista mestre para guardar os DataFrames de todas as portas já processadas

    nomes_colunas = [ # Todas as colunas de acordo com o pdf
        "Duration", "Ref_Pos", "Fbk_Pos", "Ref_Vel", "Fbk_Vel", 
        "Fbk_Hall", "Fbk_Enc", "Vbus", "Temp_Motor", 
        "Corrente_A", "Corrente_B", "Corrente_C", 
        "Temp_Driver", "Volt_A", "Volt_B", "Volt_C"
    ]

    for i in range(1, 49): # Loop para os 48 Train's
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
        
        for j in range(1, nCiclos + 1): 
            file_open = f"{caminho_pasta}F_{i}_{j:05d}_Opening.csv"
            file_close = f"{caminho_pasta}F_{i}_{j:05d}_Closing.csv"
            
            if not os.path.exists(file_open) or not os.path.exists(file_close):
                continue 
                
            df_open = pd.read_csv(file_open, sep=';', header=None, names=nomes_colunas)
            
            # 1. PREPARAÇÃO E EXTRAÇÃO COM PANDAS (Adeus tsfresh!)
            df_open['Ciclo_ID'] = j
            df_alvo = df_open[['Ciclo_ID', 'Duration', 'Corrente_A', 'Volt_A', 'Fbk_Vel']]
            
            # Agrupamos pelo ID do ciclo e calculamos as estatísticas
            features_estatisticas = df_alvo.groupby('Ciclo_ID').agg({
                'Duration': ['max'], # Pega a duração total daquele ciclo
                'Corrente_A': ['mean', 'std', 'max', 'min', 'median'], # Média, desvio padrão, picos...
                'Volt_A': ['mean', 'std', 'max', 'min'],
                'Fbk_Vel': ['mean', 'std', 'max', 'min']
            }).reset_index()
            
            # Arrumamos os nomes das colunas (Ex: 'Corrente_A' e 'mean' vira 'Corrente_A_mean')
            features_estatisticas.columns = ['_'.join(col).strip('_') for col in features_estatisticas.columns.values]
            
            # 2. MISTURANDO COM SUAS FEATURES MANUAIS
            x_max_atual = df_open['Fbk_Pos'].iloc[0] 
            
            # Transforma a linha gerada pelo pandas em um dicionário (ignorando a coluna Ciclo_ID para não duplicar)
            dict_pandas = features_estatisticas.drop(columns=['Ciclo_ID'], errors='ignore').iloc[0].to_dict()
            
            features_manuais = {
                'Ciclo': j,
                'X_max_Atual': x_max_atual,
            }
            
            # Une os dois mundos
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

    # ========================================================
    # EXPORTAÇÃO DOS DADOS TURBINADOS PARA DISCO
    # ========================================================
    pasta_destino = "Dados_Processados"
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    caminho_completo = os.path.join(pasta_destino, "df_features.pkl")

    with open(caminho_completo, 'wb') as arquivo_pkl:
        pickle.dump(todas_as_portas, arquivo_pkl)

    print(f"\n✅ Extração concluída! {len(todas_as_portas)} trens salvos com as novas features elétricas em: {caminho_completo}")
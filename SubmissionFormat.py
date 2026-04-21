def gera_arquivo_datachallenge(df_resultados):
    print("\nReconstruindo os ciclos filtrados e gerando arquivo de submissão...")
    
    import pandas as pd # Garantindo que o pandas está disponível
    df_final_list = []
    
    # Passa por cada porta que foi testada
    for porta in df_resultados['Porta_ID'].unique():
        df_p = df_resultados[df_resultados['Porta_ID'] == porta].copy()
        
        # 1. Descobre qual foi o último ciclo (o tempo de vida total da porta no teste)
        max_ciclo = int(df_p['Ciclo_Atual'].max())
        
        # 2. Cria uma tabela "perfeita" com TODOS os ciclos, do 1 até o último
        df_completo = pd.DataFrame({
            'Porta_ID': porta,
            'Ciclo_Atual': range(1, max_ciclo + 1)
        })
        
        # 3. Junta as previsões do modelo nas linhas onde elas existem
        df_completo = pd.merge(df_completo, df_p[['Ciclo_Atual', 'RUL_Final']], on='Ciclo_Atual', how='left')
        
        # 4. Preenchimento reverso dos ciclos saudáveis que foram filtrados!
        # Pega a primeira previsão real que o modelo fez
        primeiro_ciclo_previsto = df_p['Ciclo_Atual'].min()
        primeira_previsao = df_p[df_p['Ciclo_Atual'] == primeiro_ciclo_previsto]['RUL_Final'].values[0]
        
        def preenche_vazios(row):
            if pd.isna(row['RUL_Final']):
                # Contagem regressiva inversa: 
                # Se no ciclo 80 a RUL predita é 20, no ciclo 79 a RUL tem que ser 21.
                distancia_para_previsao = primeiro_ciclo_previsto - row['Ciclo_Atual']
                return primeira_previsao + distancia_para_previsao
            return row['RUL_Final']
        
        df_completo['RUL_Final'] = df_completo.apply(preenche_vazios, axis=1)
        df_final_list.append(df_completo)
        
    # Junta todas as portas reconstruídas em um DataFrame só
    df_submissao_completo = pd.concat(df_final_list, ignore_index=True)

    # =========================================================
    # FORMATAÇÃO FINAL PARA O DESAFIO
    # =========================================================
    # 5. Arredonda o RUL para inteiro
    df_submissao_completo['RUL_Final'] = df_submissao_completo['RUL_Final'].round(0).astype(int)

    # 6. Seleciona apenas as duas colunas exigidas
    df_out = df_submissao_completo[['Porta_ID', 'RUL_Final']]

    # 7. Salva com as especificações estritas (Universal)
    nome_arquivo = 'submission.csv'
    df_out.to_csv(nome_arquivo, 
                  sep=';', 
                  header=False, 
                  index=False)

    print(f"✅ Arquivo '{nome_arquivo}' gerado com sucesso!")
    print(f"Total de linhas sincronizadas geradas: {len(df_out)}")
    print("\nPrévia das primeiras linhas (ID;RUL) após reconstrução:")
    print(df_out.head(10).to_string(header=False, index=False).replace("  ", ";"))
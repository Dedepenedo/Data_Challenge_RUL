import numpy as np
import pandas as pd

def norm_f(m, a=4443.76, b=1.53, c=4443.76, d=0):
    return (a / ((m**b) + c)) + d

def calcular_score(df_resultados, alpha_peso=2.0):
    
    y_true = df_resultados['RUL_Real'].values
    y_pred = df_resultados['RUL_Final'].values

    resultados_viagem = []

    for porta_id, df_porta in df_resultados.groupby('Porta_ID'):
        
        # T: Número total de pontos preditos nessa viagem
        T = len(df_porta)
        
        # Prevenção contra divisão por zero em viagens vazias
        if T == 0:
            continue
        
        # Ordena o tempo (Fundamental para o PH funcionar)
        df_porta = df_porta.sort_values('Ciclo_Atual')
        
        erro_t = df_porta['RUL_Real'] - df_porta['RUL_Final'] 
        
        # ---------------------------------------
        # SPREAD OF ERROR (SDE)
        # ---------------------------------------
        erro_medio = erro_t.mean() 
        diferencas_quadradas = (erro_t - erro_medio) ** 2 
        somatorio = np.sum(diferencas_quadradas)
        metric_val = np.sqrt(somatorio / T)

        # ---------------------------------------
        # RMSE
        # ---------------------------------------
        erro_quadrado = erro_t ** 2 
        mse = erro_quadrado.mean() 
        rmse_val = np.sqrt(mse)

        # ---------------------------------------
        # NORMALIZAÇÃO IMEDIATA
        # ---------------------------------------
        sde_norm = norm_f(metric_val)
        rmse_norm = norm_f(rmse_val)
        
        # ---------------------------------------
        # ACCURACY METRIC
        # ---------------------------------------
        erro_absoluto = np.abs(df_porta['RUL_Real'] - df_porta['RUL_Final']) 
        rul_real = np.maximum(df_porta['RUL_Real'], 1e-5) 
        expoente = -(erro_absoluto / rul_real) 
        valores_exponenciais = np.exp(expoente) 
        acc_val = valores_exponenciais.mean() 

        # ---------------------------------------
        # PROGNOSTIC HORIZON (PH INDIVIDUAL)
        # ---------------------------------------
        t_eof = df_porta['Ciclo_Atual'].max() 
        
        margem_constante = t_eof * 0.10
        limite_inferior = df_porta['RUL_Real'] - margem_constante
        limite_superior = df_porta['RUL_Real'] + margem_constante
        
        dentro_dos_limites = (df_porta['RUL_Final'] >= limite_inferior) & (df_porta['RUL_Final'] <= limite_superior)
        fora_dos_limites = ~dentro_dos_limites 
        
        if fora_dos_limites.any():
            ultimo_erro = df_porta.loc[fora_dos_limites, 'Ciclo_Atual'].max()
            df_reta_final = df_porta[df_porta['Ciclo_Atual'] > ultimo_erro]
            
            if df_reta_final.empty:
                t_alpha = t_eof 
            else:
                t_alpha = df_reta_final['Ciclo_Atual'].min()
        else:
            t_alpha = df_porta['Ciclo_Atual'].min()
                
        # Calcula o PH só dessa porta
        ph = (t_eof - t_alpha) / t_eof if t_eof > 0 else 0

        # ---------------------------------------
        # SCORE
        # ---------------------------------------
        score = (rmse_norm + sde_norm + (alpha_peso * ph)) / (2 + alpha_peso)


        resultados_viagem.append({
            'Porta_ID': porta_id,
            'T_Pontos': T,
            'Erro_Medio (ε_barra)': round(erro_medio, 2),
            'SDE_Bruto': round(metric_val, 2),
            'SDE_Norm': round(sde_norm, 4),
            'RMSE_Bruto': round(rmse_val, 2),
            'RMSE_Norm': round(rmse_norm, 4),
            'Accuracy_Exp': round(acc_val, 4),
            'PH': round(ph, 4),
            'Score': round(score, 4)
        })

    # Converte a lista de resultados no DataFrame de análise detalhada
    df_metricas = pd.DataFrame(resultados_viagem)

    print("\n--- Métricas Individuais por Porta ---")
    print(df_metricas.to_string(index=False))
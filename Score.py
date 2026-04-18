import pandas as pd
import numpy as np
import plotly.graph_objects as go

def norm_f(m, a=4443.76, b=1.53, c=4443.76, d=0):
    return (a / ((m**b) + c)) + d

def calcular_score(df_resultados, alpha_peso=2.0): # alpha_peso só é usado no final e seu valor foi dado no pdf

    resultados_viagem = []

    for porta_id, df_porta in df_resultados.groupby('Porta_ID'):
        
        T = len(df_porta) # T: Número total de pontos preditos nessa viagem
        
        if T == 0: # Prevenção contra divisão por zero em viagens vazias
            continue
        
        df_porta = df_porta.sort_values('Ciclo_Atual') # Ordena o tempo

        y_true = df_porta['RUL_Real']
        y_pred = df_porta['RUL_Final']
        
        erro = y_true - y_pred
        
        # ---------------------------------------
        # RMSE
        # ---------------------------------------
        erro_quadrado = erro ** 2 
        somatorio = np.sum(erro_quadrado)
        mse = somatorio / T
        rmse = np.sqrt(mse)

        # ---------------------------------------
        # Precision
        # ---------------------------------------
        erro_modulo = abs(erro) 
        fracao = erro_modulo / y_true 
        
        # Filtra os valores e soma
        fracoes_validas = fracao[fracao < 0.1]
        somatorio_prec = np.sum(fracoes_validas) if not fracoes_validas.empty else 0
        precicion = 100*(somatorio_prec / T)

        # ---------------------------------------
        # NORMALIZAÇÃO
        # ---------------------------------------
        precicion_norm = norm_f(precicion)
        rmse_norm = norm_f(rmse)

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
                
        ph = (t_eof - t_alpha) / t_eof if t_eof > 0 else 0

        # ---------------------------------------
        # SCORE 
        # ---------------------------------------
        score = (rmse_norm + precicion_norm + (alpha_peso * ph)) / (2 + alpha_peso)


        resultados_viagem.append({
            'Porta_ID': porta_id,
            'T_Pontos': T,
            'Precision_Bruto': round(precicion, 2),
            'Precision_Norm': round(precicion_norm, 4),
            'RMSE_Bruto': round(rmse, 2),
            'RMSE_Norm': round(rmse_norm, 4),
            'PH': round(ph, 4),
            'Score': round(score, 4)
        })

    df_metricas = pd.DataFrame(resultados_viagem)

    # ========================================================
    # TABELA INTERATIVA COM PLOTLY
    # ========================================================
    fig = go.Figure(data=[go.Table(
        # 1. Configuração do Cabeçalho
        header=dict(
            values=[f"<b>{col}</b>" for col in df_metricas.columns], # Nomes em negrito
            fill_color='#1f77b4', # Azul padrão elegante do Plotly
            font=dict(color='white', size=13),
            align='center',
            height=35
        ),
        # 2. Configuração das Células (Linhas)
        cells=dict(
            # O Plotly exige que os dados entrem como uma lista de colunas
            values=[df_metricas[col] for col in df_metricas.columns],
            fill_color='#f5f6fa', # Fundo cinza bem clarinho
            font=dict(color='black', size=12),
            align='center',
            height=30
        )
    )])

    # 3. Embelezamento e Layout
    fig.update_layout(
        title=dict(text='<b>Métricas Individuais por Porta</b>', x=0.5, font=dict(size=18)),
        margin=dict(l=20, r=20, t=50, b=20), # Corta margens vazias
        height=400 # Altura fixa da tabela (gera scrollbar automático se tiver muitas linhas)
    )

    # 4. Exibe direto no VS Code!
    fig.show()

import numpy as np
<<<<<<< HEAD

def calcular_score_phm(y_true, y_pred, t_atual, t_eol, alpha=0.05, beta=1.0):
    """
    Calcula as métricas avançadas de PHM e o Score Final combinado.
    
    Parâmetros:
    - y_true: Lista ou array com a RUL real (Gabarito).
    - y_pred: Lista ou array com a RUL prevista pelo seu modelo (ex: XGBoost).
    - t_atual: Lista ou array com o instante de tempo (ciclo) em que a previsão foi feita.
    - t_eol: Tempo de fim de vida real da máquina (End of Life).
    - alpha: Porcentagem de tolerância da RUL (Padrão: 0.05 ou 5%).
    - beta: Peso do Prognostic Horizon no Score Final (Padrão: 1.0).
    """
    
    # Converte tudo para array do numpy para facilitar a matemática
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    t_atual = np.array(t_atual)
    T = len(y_true)
    
    # Cálculo do Erro e(t)
    eps = y_true - y_pred
    
    # ----------------------------------------------------
    # 1. Precision Metric (Dispersão do erro em torno da média)
    # ----------------------------------------------------
    mean_eps = np.mean(eps)
    precision = np.sqrt(np.mean((eps - mean_eps)**2))
    
    # ----------------------------------------------------
    # 2. RMSE (Root Mean Square Error)
    # ----------------------------------------------------
    rmse = np.sqrt(np.mean(eps**2))
    
    # ----------------------------------------------------
    # 3. Accuracy Metric (Acc) - Punição exponencial
    # ----------------------------------------------------
    # Adicionamos 1e-10 ao denominador para evitar divisão por zero
    acc = np.mean(np.exp(-np.abs(eps) / (y_true + 1e-10)))
    
    # ----------------------------------------------------
    # 4. Prognostic Horizon (PH)
    # ----------------------------------------------------
    limite_inferior = y_true - (alpha * t_eol)
    limite_superior = y_true + (alpha * t_eol)
    
    # Verifica em quais pontos a previsão bateu dentro do cone de aceitação
    dentro_dos_limites = (y_pred >= limite_inferior) & (y_pred <= limite_superior)
    
    # t_alpha é o PRIMEIRO instante em que a previsão entra nos limites e NÃO sai mais
    t_alpha = t_eol # Valor padrão: se nunca estabilizar, o t_alpha é o próprio fim da vida (PH = 0)
    for i in range(T):
        if np.all(dentro_dos_limites[i:]): # Se deste ponto em diante for tudo True
            t_alpha = t_atual[i]
            break
            
    ph = t_eol - t_alpha
    
    # ----------------------------------------------------
    # 5. Normalizações
    # ----------------------------------------------------
    # Normalização do PH
    ph_norm = (t_eol - t_alpha) / t_eol if t_eol > 0 else 0
    
    # Função normalizadora f(m) sugerida pela imagem
    def normalizar_erro(m, a=1, b=1, c=1, d=0):
        return a / ((m**b) + c) + d
    
    prec_norm = normalizar_erro(precision)
    rmse_norm = normalizar_erro(rmse)
    
    # ----------------------------------------------------
    # 6. Score Final Combinado
    # ----------------------------------------------------
    score = (acc + prec_norm + rmse_norm + (beta * ph_norm)) / (3 + beta)
    
    # ====================================================
    # EXIBIÇÃO FORMATADA
    # ====================================================
    print("=" * 50)
    print("📊 RELATÓRIO DE MÉTRICAS PHM (AVALIAÇÃO DE RUL)")
    print("=" * 50)
    print("1. MÉTRICAS BRUTAS:")
    print(f"   🔹 Precision (Dispersão) : {precision:.4f}")
    print(f"   🔹 RMSE (Erro Padrão)    : {rmse:.4f}")
    print(f"   🔹 Accuracy (Acc)        : {acc:.4f} (0 a 1)")
    print(f"   🔹 Prognostic Horizon    : {ph:.1f} ciclos ganhos")
    print("-" * 50)
    print("2. MÉTRICAS NORMALIZADAS:")
    print(f"   🔸 Norm. Precision       : {prec_norm:.4f}")
    print(f"   🔸 Norm. RMSE            : {rmse_norm:.4f}")
    print(f"   🔸 Norm. Prog. Horizon   : {ph_norm:.4f}")
    print("=" * 50)
    print(f"🏆 SCORE FINAL COMBINADO    : {score:.4f} / 1.0000")
    print("=" * 50)
    
    return score
=======
import pandas as pd
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
>>>>>>> 3711cf4 (arquivos organizados)

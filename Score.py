import numpy as np

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
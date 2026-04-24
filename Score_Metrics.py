import numpy as np

def calcular_score_phme2026(y_true, y_pred, alpha=2.0):
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    n = len(y_true)
    epsilon = 1e-10 
    
    rmse_bruto = np.sqrt(np.mean((y_true - y_pred)**2))
    
    erro_relativo = np.abs(y_true - y_pred) / (y_true + epsilon)
    precision_bruto = 100 * np.mean(erro_relativo <= 0.1)
    
    erros_acima_20 = erro_relativo > 0.2
    if np.any(erros_acima_20):
        t_alpha = np.argmax(erros_acima_20)
    else:
        t_alpha = n 
        
    t_eof = n
    ph_norm = (t_eof - t_alpha) / t_eof
    
    a = 4443.76
    b = 1.53
    c = 4443.76
    d = 0.0
    
    def normalizar(m):
        return (a / (m**b + c)) + d
    
    rmse_norm = normalizar(rmse_bruto)
    precision_norm = normalizar(100.0 - precision_bruto)
    
    score_final = (rmse_norm + precision_norm + (alpha * ph_norm)) / (2 + alpha)
    
    return {
        "Score Final": score_final,
        "RMSE (Bruto)": rmse_bruto,
        "Precision (%)": precision_bruto,
        "PH (Bruto/Norm)": ph_norm,
        "RMSE Normalizado": rmse_norm,
        "Precision Normalizada": precision_norm
    }
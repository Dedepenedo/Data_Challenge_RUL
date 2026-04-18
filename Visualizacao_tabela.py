# Arquivo: tabelas_visuais.py
import plotly.graph_objects as go

def gerar_tabelas_plotly(df_resultados, ids_teste, limite_abas=9):
    """
    Gera tabelas visuais interativas no navegador usando o Plotly.
    """
    print(f"\nGerando tabelas visuais interativas no navegador (Viagem Completa)...\n")

    # Usa o limite_abas para não travar o navegador abrindo dezenas de guias de uma vez
    for porta_escolhida in ids_teste[:limite_abas]: 
        df_porta = df_resultados[df_resultados['Porta_ID'] == porta_escolhida].copy().sort_values('Ciclo_Atual')
        
        if df_porta.empty:
            continue
            
        # 1. TEMPO E RUL
        df_porta['t'] = df_porta['Ciclo_Atual'] - df_porta['Ciclo_Atual'].min()
        df_porta['RUL_Real'] = df_porta['Ciclo'].max() - df_porta['Ciclo']
        df_porta['RUL predito'] = df_porta['RUL_Final'].round(2)
        
        # 2. CÁLCULO DA MARGEM
        t_eol_viagem = df_porta['RUL real'].iloc[0]
        alpha_val = t_eol_viagem * 0.10
        
        df_porta['+alpha'] = (df_porta['RUL real'] + alpha_val).round(1)
        df_porta['-alpha'] = (df_porta['RUL real'] - alpha_val).round(1)
        
        df_porta = df_porta.reset_index(drop=True)
        
        # 3. ENCONTRA O T_ALPHA
        esta_na_banda = (df_porta['RUL predito'] >= df_porta['-alpha']) & (df_porta['RUL predito'] <= df_porta['+alpha'])
        
        if esta_na_banda.any():
            idx_acerto = esta_na_banda.idxmax()
            t_alpha_val = df_porta.loc[idx_acerto, 't']
            status_texto = f"<span style='color: #27ae60;'>Acerto no t={t_alpha_val}</span>"
        else:
            idx_acerto = float('inf') 
            t_alpha_val = "NaN"
            status_texto = "<span style='color: #c0392b;'>Nunca entrou na margem</span>"

        # 4. LÓGICA DAS CORES DAS LINHAS
        cores_linhas = []
        for i in range(len(df_porta)):
            if i >= idx_acerto:
                cores_linhas.append('#e8f5e9' if i % 2 == 0 else '#d4edda') 
            else:
                cores_linhas.append('white' if i % 2 == 0 else '#f2f7f9')

        # 5. REMOVE A COLUNA T_ALPHA DA TABELA FINAL
        tabela_final = df_porta[['t', 'RUL real', 'RUL predito', '+alpha', '-alpha']]
        
        matriz_cores = [cores_linhas] * len(tabela_final.columns)

        # 6. CRIANDO A TABELA COM SCROLL NO PLOTLY
        titulo_tabela = (
            f"<b>DIAGNÓSTICO DA VIAGEM COMPLETA - PORTA {porta_escolhida}</b><br>"
            f"<sup style='font-size: 14px;'>t_EoL: {t_eol_viagem:.0f} ciclos | Margem (&alpha;): &plusmn;{alpha_val:.1f} | t_alpha: {status_texto}</sup>"
        )

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[f"<b>{col}</b>" for col in tabela_final.columns],
                line_color='darkslategray',
                fill_color='#2c3e50', 
                align='center',
                font=dict(color='white', size=14),
                height=40
            ),
            cells=dict(
                values=[tabela_final[col] for col in tabela_final.columns],
                line_color='darkslategray',
                fill_color=matriz_cores, 
                align='center',
                font=dict(color='darkslategray', size=13),
                height=30
            )
        )])

        fig.update_layout(
            title_text=titulo_tabela,
            title_x=0.5, 
            margin=dict(l=20, r=20, t=80, b=20),
            width=900,
            height=600 
        )

        fig.show(renderer='browser')
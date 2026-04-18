# CRIA GRÁFICOS DA DEGRADAÇÃO REAL EM COMPARAÇÃO COM A PREDIÇÃO DO MODELO

import plotly.graph_objects as go

def comparacao_RUL(df_resultados):
    print("\nGerando gráficos de degradação interativos...")

    # Pega a lista de portas únicas que o modelo testou (ex: 3, 7, 9...)
    portas_testadas = df_resultados['Porta_ID'].unique()

    # Cria um gráfico N vezes (um para cada porta)
    for porta in portas_testadas:
        # Filtra os dados apenas da porta da vez e garante que o tempo está na ordem certa
        df_porta = df_resultados[df_resultados['Porta_ID'] == porta].sort_values('Ciclo_Atual')

        fig = go.Figure()

        # 1. Linha do Gabarito (A vida real do componente)
        fig.add_trace(go.Scatter(
            x=df_porta['Ciclo_Atual'],
            y=df_porta['RUL_Real'],
            mode='lines',
            name='RUL Real',
            line=dict(color='#1f77b4', width=3) # Azul clássico e espesso
        ))

        # 2. Linha do Modelo (A nossa previsão)
        fig.add_trace(go.Scatter(
            x=df_porta['Ciclo_Atual'],
            y=df_porta['RUL_Final'],
            mode='lines',
            name='RUL Predita (Modelo)',
            line=dict(color='#ff7f0e', width=2, dash='dash') # Laranja tracejado para destacar a previsão
        ))

        # 3. Embelezamento do Gráfico
        fig.update_layout(
            title=dict(text=f'<b>Acompanhamento de Degradação - Porta {porta}</b>', x=0.5, font=dict(size=16)),
            xaxis_title='<b>Ciclo Atual</b> (Tempo de Uso)',
            yaxis_title='<b>RUL</b> (Ciclos Restantes até Falha)',
            plot_bgcolor='white',          # Fundo branco profissional
            hovermode='x unified',         # Ao passar o mouse, mostra a RUL real e a predita juntas numa caixinha!
            margin=dict(l=40, r=40, t=50, b=40),
            height=350                     # Altura controlada para caberem vários na tela do VS Code
        )

        # 4. Linhas de grade suaves (Grid)
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E5E5')

        # 5. Exibe o gráfico diretamente na célula do VS Code
        fig.show()

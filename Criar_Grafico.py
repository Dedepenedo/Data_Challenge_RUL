import plotly.graph_objects as go
import plotly.colors as pc
import numpy as np
import pickle

def gera_grafico(todas_as_portas):
    # Inicializa a figura em branco
    fig = go.Figure()

    num_linhas = len(todas_as_portas)

    # Cria a paleta de cores 'turbo' fatiada matematicamente para o Plotly
    valores_cor = np.linspace(0, 1, num_linhas)
    paleta_cores = pc.sample_colorscale('turbo', valores_cor)

    # Adiciona cada trem como uma linha (trace) interativa
    for idx, (porta_id, df_plot) in enumerate(todas_as_portas):
        fig.add_trace(go.Scatter(
            x=df_plot['Ciclo_Relativo'],
            y=df_plot['Distancia_Ref'],
            mode='lines',
            line=dict(color=paleta_cores[idx], width=1.5),
            opacity=0.6, # Transparência equivalente ao alpha
            name=f'Train {porta_id}',
            # Configura a caixinha interativa que aparece ao passar o mouse:
            hovertemplate=f'<b>Train {porta_id}</b><br>Ciclo FDI: %{{x}}<br>Perda: %{{y:.2f}}°<extra></extra>'
        ))

    # ---------------------------------------------------------
    # Linhas de Marcação (Limiar e Ciclo Zero)
    # ---------------------------------------------------------
    # O Plotly tem funções específicas para cruzar o gráfico com linhas retas:
    fig.add_hline(y=0, line_dash="dash", line_color="red", line_width=1.5)
    fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=1, opacity=0.7)

    # Para que essas linhas apareçam na legenda (como no Matplotlib), 
    # criamos "linhas invisíveis" apenas com o nome para ancorar na legenda
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', 
                            line=dict(color='red', width=2, dash='dash'), name='Limiar de Falha'))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', 
                            line=dict(color='black', width=1.5), name='Último Ciclo Saudável'))

    # ---------------------------------------------------------
    # Embelezamento e Layout (equivalente ao plt.title, labels e grid)
    # ---------------------------------------------------------
    fig.update_layout(
        title=dict(text='Curvas de Degradação Normalizadas', font=dict(size=20)),
        xaxis_title='Ciclos FDI',
        yaxis_title='Perda de Amplitude da Porta',
        
        # Tamanho da figura (equivalente ao figsize=(16,7))
        width=1200, 
        height=600,
        
        # Fundo branco com grid sutil (igual ao matplotlib com seaborn)
        template="plotly_white",
        hovermode="closest", # O mouse foca no ponto mais próximo
        
        # Configuração da Legenda (coloca do lado de fora, com scrollbar automático se ficar grande)
        legend=dict(
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=10)
        )
    )

    # Reforça as linhas de grade pontilhadas
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray', griddash='dot')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray', griddash='dot')

    # Exibe o gráfico interativo
    fig.show()
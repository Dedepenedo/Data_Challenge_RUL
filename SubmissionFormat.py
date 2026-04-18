
def gera_arquivo_datachallenge(df_resultados):
    print("\nGerando arquivo de submissão (Formato Universal)...")

    # 1. Seleciona as colunas na ordem pedida (ID do teste e Resultado RUL)
    # IMPORTANTE: Não usamos drop_duplicates aqui para garantir a sincronia estrita de linhas
    df_submissao = df_resultados[['Porta_ID', 'RUL_Final']].copy()

    # 2. Arredonda o RUL para inteiro
    df_submissao['RUL_Final'] = df_submissao['RUL_Final'].round(0).astype(int)

    # 3. Nome do arquivo
    nome_arquivo = 'submission.csv'

    # 4. Salva com as especificações estritas:
    # sep=';' -> Separador ponto e vírgula
    # header=False -> Sem linha de cabeçalho
    # index=False -> Sem a coluna de índices do pandas
    df_submissao.to_csv(nome_arquivo, 
                        sep=';', 
                        header=False, 
                        index=False)

    print(f"✅ Arquivo '{nome_arquivo}' gerado com sucesso!")
    print(f"Total de linhas geradas: {len(df_submissao)}")
    print("\nPrévia das primeiras linhas (ID;RUL):")
    # Mostra como o arquivo ficou por dentro
    print(df_submissao.head(10).to_string(header=False, index=False).replace("  ", ";"))
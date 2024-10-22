import os
import pandas as pd
import streamlit as st

# Define o caminho da pasta contendo os arquivos CSV
caminho_pasta = r'C:\Users\Rodrigo Traldi\PROJETO INVESTIMENTO\MELHOR PRAZO'

# Lista para armazenar todos os DataFrames
lista_dataframes = []

# Itera sobre todos os arquivos na pasta
for arquivo in os.listdir(caminho_pasta):
    if arquivo.endswith('.csv'):
        caminho_arquivo = os.path.join(caminho_pasta, arquivo)
        df = pd.read_csv(caminho_arquivo, encoding='latin1', sep=';', index_col=False)
        # Converter colunas numéricas que contêm vírgulas para o formato numérico adequado
        colunas_para_converter = [
            'Peso Inicial Kg', 'Peso Final Kg', 'Valor Inicial R$', 'Valor Final R$', 'Cubagem', 
            'Limite Peso Kg', 'Prazo Entrega', 'Frete Valor R$', 'Excedente R$', 'AdValor %', 
            'Peso Excedente Kg', 'Valor Por Kg R$', 'Despacho R$', 'Total Minimo R$', 'Imposto %',
            'Seguro %', 'Seguro Minimo R$', 'Gris %', 'Gris Minimo R$', 'Pedagio R$', 
            'Pedagio Fração R$', 'Tas %', 'Tas Minimo R$', 'Emex %', 'Emex Minimo R$', 
            'Taxa Minima R$', 'Taxa Maxima R$', 'Taxa %'
        ]
        for coluna in colunas_para_converter:
            if coluna in df.columns and df[coluna].dtype == 'object':
                df[coluna] = pd.to_numeric(df[coluna].str.replace('.', '').str.replace(',', '.'), errors='coerce')
        # Garantir que a coluna Transportadora está sendo lida corretamente
        if 'Transportadora' not in df.columns:
            df.rename(columns={'transportadora': 'Transportadora'}, inplace=True)
        lista_dataframes.append(df)

# Concatena todos os DataFrames em um único DataFrame
# Ignorar índices para evitar conflitos e preservar os valores corretos
df_completo = pd.concat(lista_dataframes, ignore_index=True)

# Corrigir nomes de colunas para evitar erros de chave
df_completo.rename(columns={'Cep final': 'Cep Final', 'transportadora': 'Transportadora'}, inplace=True)

# Função para verificar se um CEP está dentro de um intervalo
def cep_in_range(cep, cep_inicial, cep_final):
    return cep_inicial <= cep <= cep_final

# Cria um DataFrame para armazenar o melhor prazo por CEP e por range de peso
melhores_prazos = []

# Itera sobre cada linha do DataFrame completo
for index, row in df_completo.iterrows():
    cep_inicial = row['Cep Inicial']
    cep_final = row['Cep Final']
    peso_inicial = row['Peso Inicial Kg']
    peso_final = row['Peso Final Kg']
    prazo = row['Prazo Entrega']
    transportadora = row['Transportadora']

    # Verifica se o prazo já foi registrado para o range específico
    encontrado = False
    for melhor_prazo in melhores_prazos:
        if (melhor_prazo['Cep Inicial'] == cep_inicial and
                melhor_prazo['Cep Final'] == cep_final and
                melhor_prazo['Peso Inicial Kg'] == peso_inicial and
                melhor_prazo['Peso Final Kg'] == peso_final):
            # Se o prazo atual for menor que o já registrado, atualiza o melhor prazo
            if pd.notna(prazo) and (pd.isna(melhor_prazo['Prazo Entrega']) or prazo < melhor_prazo['Prazo Entrega']):
                melhor_prazo['Prazo Entrega'] = prazo
                melhor_prazo['Transportadora'] = transportadora
            encontrado = True
            break

    # Se não encontrado, adiciona o novo prazo à lista de melhores prazos
    if not encontrado:
        melhores_prazos.append({
            'Cep Inicial': cep_inicial,
            'Cep Final': cep_final,
            'Peso Inicial Kg': peso_inicial,
            'Peso Final Kg': peso_final,
            'Prazo Entrega': prazo,
            'Transportadora': transportadora
        })

# Converte a lista de melhores prazos para um DataFrame
df_melhores_prazos = pd.DataFrame(melhores_prazos)

# Salva o DataFrame resultante em um arquivo CSV
df_melhores_prazos.to_csv(r'C:\Users\Rodrigo Traldi\PROJETO INVESTIMENTO\melhor_prazo_por_cep_peso.csv', index=False)

print("Análise concluída e arquivo salvo.")

# Streamlit para consulta de melhores prazos
st.title('Consulta de Melhor Prazo de Entrega por CEP e Peso')

# Entrada de CEP
cep_input = st.text_input('Digite o CEP para consultar o melhor prazo de entrega:')

# Entrada de Peso
peso_input = st.number_input('Digite o peso (em Kg):', min_value=0.0, step=0.1)

# Buscar e exibir o melhor prazo para o CEP e peso informados
if cep_input and peso_input > 0:
    resultados = df_melhores_prazos[(df_melhores_prazos['Cep Inicial'] <= cep_input) &
                                     (df_melhores_prazos['Cep Final'] >= cep_input) &
                                     (df_melhores_prazos['Peso Inicial Kg'] <= peso_input) &
                                     (df_melhores_prazos['Peso Final Kg'] >= peso_input)]
    if not resultados.empty:
        melhor_opcao = resultados.loc[resultados['Prazo Entrega'].idxmin()]
        st.write('Melhor opção de transportadora:')
        st.write(f"Transportadora: {melhor_opcao['Transportadora']}")
        st.write(f"Prazo de Entrega: {melhor_opcao['Prazo Entrega']} dias")
    else:
        st.write('Nenhuma opção encontrada para o CEP e peso informados.')

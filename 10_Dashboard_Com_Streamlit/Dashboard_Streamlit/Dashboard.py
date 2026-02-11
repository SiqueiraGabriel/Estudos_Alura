import streamlit as st
import pandas as pd
import requests
import plotly.express as px


def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor /= 1000
    return f'{prefixo} {valor:.2f} milhões'






# Obter os dados da API
url = "https://labdados.com/produtos"
response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format='%d/%m/%Y')



## ---------------------------------------->> TABELAS

# ------------->> TABELAS DE QTD RECEITA

# Obter a receita total por Estado
receitas_estados = dados.groupby('Local da compra')[['Preço']].sum()
receitas_estados = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(receitas_estados, left_on='Local da compra', right_index=True).sort_values(by='Preço', ascending=False)

# Obter a receita por mes
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum() .reset_index() # Setar a data como indice e agroupar os elemnrtos a partir do mes
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

# Obter a receita por categoria
receitas_categoria = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values(by='Preço', ascending=False)

# ------------->> TABELAS DE QTD VENDAS

# Obter a quantidade de vendas por Estado
vendas_estado = dados.groupby('Local da compra').size().reset_index()
vendas_estado.columns = ['Local da compra', 'Qtd']
vendas_estado = dados.drop_duplicates(subset='Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estado, left_on='Local da compra', right_on='Local da compra').sort_values(by='Qtd', ascending=False)

# Obter a qtd vendas por mes
vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M')).size().reset_index() # Setar a data como indice e agroupar os elemnrtos a partir do mes
vendas_mensal.columns = ['Data da Compra', 'Qtd']
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.month_name()

# Vendas por categoria
vendas_categoria = dados.groupby('Categoria do Produto').size().reset_index()
vendas_categoria.columns = ['Categoria do Produto', 'Qtd']

vendas_categoria = vendas_categoria.sort_values(by='Qtd', ascending=False)

# ------------->> TABELAS DE VENDEDORES
vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))


## ---------------------------------------->> GRAFICOS
fig_mapa_receita = px.scatter_geo(
    receitas_estados, 
    lat='lat',
    lon='lon',
    scope='south america',
    size='Preço',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False},
    title='Receita por Estado'
)

fig_receita_mensal = px.line(
    data_frame=receita_mensal,
    x='Mes',
    y='Preço',
    markers= True,
    range_y = (0,receita_mensal.max()),
    color='Ano',
    line_dash='Ano', # Formato da linha
    title='Receita mensal'
)
fig_receita_mensal.update_layout(yaxis_title='Receita')


fig_receita_estados = px.bar(
    data_frame=receitas_estados.head(),
    x = 'Local da compra',
    y='Preço',
    text_auto=True, # No grafico o valor ficara em cima de cada coluna
    title='Top Estados (Receita)'
)
fig_receita_estados.update_layout(yaxis_title='Receita')


fig_receita_categorias = px.bar(
    data_frame=receitas_categoria,
    text_auto=True,
    title='Receita por categoria'
)
fig_receita_categorias.update_layout(yaxis_title='Receita')

# ----------------- Vendas
fig_mapa_vendas = px.scatter_geo(
    vendas_estado, 
    lat='lat',
    lon='lon',
    scope='south america',
    size='Qtd',
    template='seaborn',
    hover_name='Local da compra',
    hover_data={'lat': False, 'lon': False},
    title='Vendas por Estado'
)

fig_vendas_mensal = px.line(
    data_frame=vendas_mensal,
    x='Mes',
    y='Qtd',
    markers= True,
    range_y = (0,receita_mensal.max()),
    color='Ano',
    line_dash='Ano', # Formato da linha
    title='Vendas mensal'
)
fig_vendas_mensal.update_layout(yaxis_title='Qtd. Vendas')

fig_vendas_categorias = px.bar(
    data_frame=vendas_categoria,
    x='Categoria do Produto',
    y='Qtd',
    text_auto=True,
    title='Qtd. Venda por categoria'
)
fig_receita_categorias.update_layout(yaxis_title='Receita')

fig_vendas_estados = px.bar(
    data_frame=vendas_estado.head(),
    x = 'Local da compra',
    y='Qtd',
    text_auto=True, # No grafico o valor ficara em cima de cada coluna
    title='Top Estados (Vendas)'
)
fig_vendas_estados.update_layout(yaxis_title='Vendas')


# ----------------------------------------->> VISUALIZAÇÃO NO STREAMLIT

# 

# Definir por padrão que o dash será sempre tela cheia
st.set_page_config(layout='wide', page_title='Dashboard Vendas - Alura')

#Adicionando um título ao programa (emoji: :shopping_trolley:)
st.title('DASHBOARD DE VENDAS ')

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])

with aba1:

    # Criação de colunas
    coluna1, coluna2 = st.columns(2)

    # O with especifica todos os valores que estão presentes dentro da coluna
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$')) # Adicionar uma métrica no Aplicativo e vincular a coluna
        st.plotly_chart(fig_mapa_receita, use_container_width=True) # Adicionar uma figura do plotly 
        st.plotly_chart(fig_receita_estados, use_container_width=True)

    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0])) # Adicionar uma métrica no Aplicativo e vincular a coluna
        st.plotly_chart(fig_receita_mensal, use_container_width=True) # Adicionar uma figura do plotly
        st.plotly_chart(fig_receita_categorias, use_container_width=True) # Criação do Gráfico de mapa com o plotly


with aba2:
        # Criação de colunas
    coluna1, coluna2 = st.columns(2)

    # O with especifica todos os valores que estão presentes dentro da coluna
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$')) # Adicionar uma métrica no Aplicativo e vincular a coluna
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0])) # Adicionar uma métrica no Aplicativo e vincular a coluna
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:

    qtd_vendedores = st.number_input('Quantidade de Vendedores: ', min_value=2, max_value=10, value=5)

    # Construção do gráfico de forma dinamica


        # Criação de colunas
    coluna1, coluna2 = st.columns(2)

    # O with especifica todos os valores que estão presentes dentro da coluna
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$')) # Adicionar uma métrica no Aplicativo e vincular a coluna
        fig_receita_vendedores = px.bar(
            data_frame=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),
            x='sum',
            y=vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendores (receita)'
        )
        st.plotly_chart(fig_receita_vendedores)
       
    with coluna2:
        st.metric('Quantidade de Vendas', formata_numero(dados.shape[0])) # Adicionar uma métrica no Aplicativo e vincular a coluna
        fig_vendas_vendedores = px.bar(
            data_frame=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores),
            x='count',
            y=vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
            text_auto=True,
            title=f'Top {qtd_vendedores} vendores (quantidade de vendas)'
        )
        st.plotly_chart(fig_vendas_vendedores)
       







# Apresentar os dados na tela em forma de tabela
st.dataframe(dados)



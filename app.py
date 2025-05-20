import dash
from dash import dcc, html, Input, Output, callback, State, ALL
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import json
import os
import numpy as np

# Carregar os grupos de colunas do arquivo JSON
with open('grupos_colunas.json', 'r', encoding='utf-8') as f:
    grupos_colunas = json.load(f)

# Carregar os dados do CSV
try:
    df = pd.read_csv('dados_sergipe.csv', delimiter=';', encoding='utf-8')
except Exception as e:
    print(f"Erro ao carregar o CSV: {e}")
    # Se falhar, tente outra codificação
    df = pd.read_csv('dados_sergipe.csv', delimiter=';', encoding='latin1')

# Inicializar o aplicativo Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Estilo do aplicativo
colors = {
    'background': '#F0F0F0',
    'text': '#111111',
    'accent': '#007BFF',
    'panel': '#FFFFFF',
    'tab_selected': '#FFFFFF',
    'tab_unselected': '#DDDDDD',
    'filter_panel': '#F8F9FA'
}

# Estilo das tabs
tab_style = {
    'backgroundColor': colors['tab_unselected'],
    'padding': '10px',
    'fontWeight': 'bold',
    'borderRadius': '5px',
    'marginRight': '2px'
}

tab_selected_style = {
    'backgroundColor': colors['tab_selected'],
    'padding': '10px',
    'fontWeight': 'bold',
    'color': colors['accent'],
    'borderRadius': '5px',
    'borderTop': f'2px solid {colors["accent"]}',
    'boxShadow': '0px 2px 5px rgba(0, 0, 0, 0.1)'
}

# Preparar os valores para os filtros
filtros_config = {
    'cidade': {
        'label': 'Cidade',
        'options': sorted([{'label': city, 'value': city} for city in df['cidade'].unique()], key=lambda x: x['label']),
        'value': []
    },
    'região': {
        'label': 'Região',
        'options': sorted([{'label': region, 'value': region} for region in df['região'].unique()], key=lambda x: x['label']),
        'value': []
    },
    'faixa de idade': {
        'label': 'Faixa de Idade',
        'options': sorted([{'label': age, 'value': age} for age in df['faixa de idade'].unique()], key=lambda x: x['label']),
        'value': []
    },
    'religião': {
        'label': 'Religião',
        'options': sorted([{'label': religion, 'value': religion} for religion in df['religião'].unique()], key=lambda x: x['label']),
        'value': []
    },
    'grau de Instrução': {
        'label': 'Grau de Instrução',
        'options': sorted([{'label': edu, 'value': edu} for edu in df['grau de Instrução'].unique()], key=lambda x: x['label']),
        'value': []
    },
    'renda familiar': {
        'label': 'Renda Familiar',
        'options': sorted([{'label': income, 'value': income} for income in df['renda familiar'].unique()], key=lambda x: x['label']),
        'value': []
    },
    'sexo': {
        'label': 'Sexo',
        'options': sorted([{'label': gender, 'value': gender} for gender in df['sexo'].unique()], key=lambda x: x['label']),
        'value': []
    }
}

# Layout do aplicativo com filtros
app.layout = html.Div([
    html.H1('Dashboard de Pesquisa de Opinião - Sergipe', 
           style={'textAlign': 'center', 'color': colors['text'], 'padding': '20px'}),
    
    # Painel de filtros
    html.Div([
        html.H3('Filtros', style={'marginBottom': '15px', 'color': colors['text']}),
        
        html.Div([
            # Criando os dropdowns de filtro
            html.Div([
                html.Label(filtros_config[filtro]['label'], style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                dcc.Dropdown(
                    id={'type': 'filtro-dropdown', 'index': filtro},
                    options=filtros_config[filtro]['options'],
                    value=filtros_config[filtro]['value'],
                    multi=True,
                    placeholder=f"Selecione {filtros_config[filtro]['label'].lower()}...",
                    style={'width': '100%', 'marginBottom': '10px'}
                )
            ], style={'width': '13%', 'display': 'inline-block', 'marginRight': '1%'})
            for filtro in filtros_config
        ], style={'display': 'flex', 'justifyContent': 'space-between'}),
        
        # Botões para aplicar ou limpar filtros
        html.Div([
            html.Button('Aplicar Filtros', id='aplicar-filtros', n_clicks=0, 
                       style={'backgroundColor': colors['accent'], 'color': 'white', 'border': 'none', 
                              'borderRadius': '5px', 'padding': '10px 15px', 'marginRight': '10px'}),
            html.Button('Limpar Filtros', id='limpar-filtros', n_clicks=0,
                       style={'backgroundColor': '#6c757d', 'color': 'white', 'border': 'none', 
                              'borderRadius': '5px', 'padding': '10px 15px'})
        ], style={'margin': '15px 0'}),
        
        # Exibir informações sobre os filtros aplicados
        html.Div(id='filtros-aplicados-info', style={'margin': '10px 0', 'fontStyle': 'italic'}),
        
        # Adicionar informação sobre o uso da ponderação
        html.Div([
            html.P('Todos os gráficos consideram a ponderação por peso amostral.', 
                  style={'fontStyle': 'italic', 'color': '#6c757d', 'marginTop': '10px'})
        ])
    ], style={
        'backgroundColor': colors['filter_panel'], 
        'padding': '15px', 
        'borderRadius': '5px',
        'marginBottom': '20px',
        'boxShadow': '0px 2px 5px rgba(0, 0, 0, 0.1)'
    }),
    
    # Store para armazenar o estado dos filtros
    dcc.Store(id='filtros-aplicados', data={filtro: [] for filtro in filtros_config}),
    
    # Tabs do dashboard
    dcc.Tabs(id='tabs', value='tab-demografico', children=[
        dcc.Tab(label='Demográfico', value='tab-demografico',
                style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Mídia e Comunicação', value='tab-midia',
                style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Avaliação de Governo', value='tab-governo',
                style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Programas', value='tab-programas',
                style=tab_style, selected_style=tab_selected_style),
        dcc.Tab(label='Figuras Públicas', value='tab-figuras',
                style=tab_style, selected_style=tab_selected_style),
    ]),
    
    html.Div(id='tab-content', style={'padding': '20px'})
], style={'backgroundColor': colors['background'], 'minHeight': '100vh', 'padding': '20px'})

# Função para filtrar o dataframe com base nos filtros aplicados
def filter_dataframe(df, filtros):
    filtered_df = df.copy()
    
    for filtro, valores in filtros.items():
        if valores and len(valores) > 0:
            filtered_df = filtered_df[filtered_df[filtro].isin(valores)]
    
    return filtered_df

# Função para calcular contagens ponderadas
def weighted_count(df, column, weight_col='peso'):
    # Verificar se a coluna existe no DataFrame
    if column not in df.columns:
        return pd.Series(dtype=float)  # Retornar uma série vazia
    
    # Verificar se a coluna de peso existe
    if weight_col not in df.columns:
        return df[column].value_counts()
    
    # Filtrar valores nulos ou vazios
    valid_df = df[df[column].notna() & (df[column] != '.')]
    if len(valid_df) == 0:
        return pd.Series(dtype=float)
    
    # Calcular proporções
    total_peso = df[weight_col].sum()
    if total_peso == 0:
        return pd.Series(dtype=float)
        
    # Agrupar e somar os pesos
    weighted_counts = valid_df.groupby(column)[weight_col].sum()
    # Calcular percentuais
    weighted_percent = (weighted_counts / total_peso) * 100
    return weighted_percent.round(2).sort_values(ascending=False)

# Função para calcular percentuais ponderados
def weighted_percentage(df, column, weight_col='peso'):
    # Verificar se a coluna existe no DataFrame
    if column not in df.columns:
        return pd.Series(dtype=float)  # Retornar uma série vazia
    
    # Verificar se a coluna de peso existe
    if weight_col not in df.columns:
        counts = df[column].value_counts(normalize=True) * 100
        return counts.round(2)  # Arredondar para 2 casas decimais
    
    # Filtrar valores nulos ou vazios
    valid_df = df[df[column].notna() & (df[column] != '.')]
    if len(valid_df) == 0:
        return pd.Series(dtype=float)  # Retornar uma série vazia se não houver dados válidos
    
    # Calcular proporções
    total_peso = df[weight_col].sum()
    if total_peso == 0:
        return pd.Series(dtype=float)
        
    # Agrupar e somar os pesos
    weighted_counts = valid_df.groupby(column)[weight_col].sum()
    # Calcular percentuais
    weighted_percent = (weighted_counts / total_peso) * 100
    return weighted_percent.round(2).sort_values(ascending=False)  # Arredondar para 2 casas decimais

# Função para criar tabulação cruzada ponderada
def weighted_crosstab(df, index, columns, weight_col='peso'):
    # Verificar se as colunas existem no DataFrame
    if index not in df.columns or columns not in df.columns:
        return pd.DataFrame()  # Retornar um DataFrame vazio
    
    # Filtrar valores nulos ou vazios
    valid_df = df[(df[index].notna() & (df[index] != '.')) & 
                  (df[columns].notna() & (df[columns] != '.'))]
    
    if len(valid_df) == 0:
        return pd.DataFrame()
    
    # Se não houver coluna de peso, use o crosstab padrão
    if weight_col not in df.columns:
        return pd.crosstab(valid_df[index], valid_df[columns], normalize='index') * 100
    
    # Crosstab ponderado
    cross_data = []
    for idx_val in valid_df[index].unique():
        for col_val in valid_df[columns].unique():
            mask = (valid_df[index] == idx_val) & (valid_df[columns] == col_val)
            weight_sum = valid_df.loc[mask, weight_col].sum()
            cross_data.append({
                'index': idx_val,
                'column': col_val,
                'weight': weight_sum
            })
    
    if not cross_data:
        return pd.DataFrame()
    
    cross_df = pd.DataFrame(cross_data)
    pivot_df = cross_df.pivot(index='index', columns='column', values='weight')
    
    # Normalizar por linha (percentual por categoria do índice)
    row_sums = pivot_df.sum(axis=1)
    if (row_sums == 0).any():
        # Evitar divisão por zero
        for idx in pivot_df.index[row_sums == 0]:
            pivot_df.loc[idx, :] = np.nan
        row_sums = row_sums[row_sums > 0]
    
    for col in pivot_df.columns:
        pivot_df[col] = (pivot_df[col] / row_sums) * 100
    
    return pivot_df.round(2)  # Arredondar para 2 casas decimais

# Função para criar um card de gráfico
def create_graph_card(graph, title):
    return html.Div([
        html.H3(title, style={'textAlign': 'center', 'color': colors['text']}),
        dcc.Graph(figure=graph)
    ], style={
        'backgroundColor': colors['panel'],
        'padding': '15px',
        'borderRadius': '5px',
        'boxShadow': '0px 2px 5px rgba(0, 0, 0, 0.1)',
        'margin': '10px'
    })

# Função para criar um dropdown de seleção
def create_dropdown(id, options, value, title):
    return html.Div([
        html.Label(title, style={'fontWeight': 'bold', 'marginBottom': '5px'}),
        dcc.Dropdown(
            id=id,
            options=options,
            value=value,
            style={'width': '100%', 'marginBottom': '15px'}
        )
    ], style={'padding': '10px'})

# Função para formatar o texto de filtros aplicados
def format_filtros_text(filtros):
    filtros_text = []
    for filtro, valores in filtros.items():
        if valores and len(valores) > 0:
            if len(valores) <= 3:
                valores_str = ", ".join(valores)
            else:
                valores_str = f"{len(valores)} selecionados"
            filtros_text.append(f"{filtro.title()}: {valores_str}")
    
    if filtros_text:
        return "Filtros aplicados: " + " | ".join(filtros_text)
    else:
        return "Nenhum filtro aplicado. Mostrando todos os dados."

# Callback para gerenciar os filtros
@callback(
    [Output('filtros-aplicados', 'data'),
     Output('filtros-aplicados-info', 'children')],
    [Input('aplicar-filtros', 'n_clicks'),
     Input('limpar-filtros', 'n_clicks')],
    [State({'type': 'filtro-dropdown', 'index': ALL}, 'value'),
     State({'type': 'filtro-dropdown', 'index': ALL}, 'id'),
     State('filtros-aplicados', 'data')]
)
def gerenciar_filtros(n_aplicar, n_limpar, valores_filtros, ids_filtros, filtros_atuais):
    ctx = dash.callback_context
    
    if not ctx.triggered:
        return filtros_atuais, format_filtros_text(filtros_atuais)
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if button_id == 'limpar-filtros':
        filtros_limpos = {filtro: [] for filtro in filtros_atuais}
        return filtros_limpos, "Nenhum filtro aplicado. Mostrando todos os dados."
    
    elif button_id == 'aplicar-filtros':
        novos_filtros = {}
        for i, id_dict in enumerate(ids_filtros):
            filtro = id_dict['index']
            novos_filtros[filtro] = valores_filtros[i] if valores_filtros[i] else []
        
        return novos_filtros, format_filtros_text(novos_filtros)
    
    return filtros_atuais, format_filtros_text(filtros_atuais)

# Callback para atualizar o conteúdo das abas
@callback(
    Output('tab-content', 'children'),
    [Input('tabs', 'value'),
     Input('filtros-aplicados', 'data')]
)
def render_content(tab, filtros_aplicados):
    # Filtrar o dataframe com base nos filtros aplicados
    filtered_df = filter_dataframe(df, filtros_aplicados)
    
    # Se não houver dados após a filtragem, exiba uma mensagem
    if len(filtered_df) == 0:
        return html.Div([
            html.H3("Nenhum dado encontrado com os filtros aplicados.", 
                   style={'textAlign': 'center', 'color': 'red', 'margin': '50px'})
        ])
    
    if tab == 'tab-demografico':
        # Distribuição por cidade (top 10) - Ponderada
        cidade_count = weighted_percentage(filtered_df, 'cidade').nlargest(10)
        if not cidade_count.empty:
            fig_cidade = px.bar(
                x=cidade_count.index, 
                y=cidade_count.values,
                labels={'x': 'Cidade', 'y': 'Percentual (%)'},
                title='Top 10 Cidades',
                color=cidade_count.values,
                color_continuous_scale='Blues'
            )
            fig_cidade.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        else:
            fig_cidade = go.Figure()
            fig_cidade.update_layout(title='Dados insuficientes para distribuição por cidade')
        
        # Distribuição por sexo - Ponderada
        sexo_count = weighted_percentage(filtered_df, 'sexo')
        if not sexo_count.empty:
            fig_sexo = px.pie(
                values=sexo_count.values, 
                names=sexo_count.index,
                title='Distribuição por Sexo (%)',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig_sexo.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
        else:
            fig_sexo = go.Figure()
            fig_sexo.update_layout(title='Dados insuficientes para distribuição por sexo')
        
        # Distribuição por faixa etária - Ponderada
        idade_count = weighted_percentage(filtered_df, 'faixa de idade')
        if not idade_count.empty:
            fig_idade = px.pie(
                values=idade_count.values, 
                names=idade_count.index,
                title='Distribuição por Faixa Etária (%)',
                color_discrete_sequence=px.colors.sequential.Plasma
            )
            fig_idade.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
        else:
            fig_idade = go.Figure()
            fig_idade.update_layout(title='Dados insuficientes para distribuição por faixa etária')
        
        # Distribuição por grau de instrução - Ponderada
        instrucao_count = weighted_percentage(filtered_df, 'grau de Instrução')
        if not instrucao_count.empty:
            fig_instrucao = px.bar(
                x=instrucao_count.index, 
                y=instrucao_count.values,
                labels={'x': 'Grau de Instrução', 'y': 'Percentual (%)'},
                title='Distribuição por Grau de Instrução',
                color=instrucao_count.values,
                color_continuous_scale='Blues'
            )
            fig_instrucao.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        else:
            fig_instrucao = go.Figure()
            fig_instrucao.update_layout(title='Dados insuficientes para distribuição por grau de instrução')
        
        # Distribuição por renda familiar - Ponderada
        renda_count = weighted_percentage(filtered_df, 'renda familiar')
        if not renda_count.empty:
            fig_renda = px.bar(
                x=renda_count.index, 
                y=renda_count.values,
                labels={'x': 'Renda Familiar', 'y': 'Percentual (%)'},
                title='Distribuição por Renda Familiar',
                color=renda_count.values,
                color_continuous_scale='Greens'
            )
            fig_renda.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        else:
            fig_renda = go.Figure()
            fig_renda.update_layout(title='Dados insuficientes para distribuição por renda familiar')
        
        # Distribuição por religião - Ponderada
        religiao_count = weighted_percentage(filtered_df, 'religião')
        if not religiao_count.empty:
            fig_religiao = px.pie(
                values=religiao_count.values, 
                names=religiao_count.index,
                title='Distribuição por Religião (%)',
                color_discrete_sequence=px.colors.sequential.Viridis
            )
            fig_religiao.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
        else:
            fig_religiao = go.Figure()
            fig_religiao.update_layout(title='Dados insuficientes para distribuição por religião')
        
        return html.Div([
            html.Div([
                html.Div([
                    create_graph_card(fig_cidade, 'Distribuição por Cidade'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_sexo, 'Distribuição por Sexo'),
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.Div([
                    create_graph_card(fig_idade, 'Distribuição por Faixa Etária'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_religiao, 'Distribuição por Religião'),
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.Div([
                    create_graph_card(fig_instrucao, 'Distribuição por Grau de Instrução'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_renda, 'Distribuição por Renda Familiar'),
                ], className='six columns'),
            ], className='row'),
        ])
    
    elif tab == 'tab-midia':
        # Gráficos para a aba de Mídia e Comunicação - Ponderados
        
        # Uso de redes sociais - Ponderado
        redes = ['utiliza redes: whatsapp', 'utiliza redes: instagram', 
                'utiliza redes: facebook', 'utiliza redes: youtube', 
                'utiliza redes: tiktok', 'utiliza redes: x/ antigo twitter']
        
        uso_redes = {}
        for rede in redes:
            if rede in filtered_df.columns:
                rede_nome = rede.replace('utiliza redes: ', '')
                # Calcular como percentual do total
                total_peso = filtered_df['peso'].sum()
                rede_df = filtered_df[filtered_df[rede] == 'Sim']
                if len(rede_df) > 0 and total_peso > 0:
                    uso_redes[rede_nome] = (rede_df['peso'].sum() / total_peso) * 100
                else:
                    uso_redes[rede_nome] = 0
        
        if uso_redes:
            fig_redes = px.bar(
                x=list(uso_redes.keys()), 
                y=list(uso_redes.values()),
                labels={'x': 'Rede Social', 'y': 'Percentual de Uso (%)'},
                title='Uso de Redes Sociais',
                color=list(uso_redes.values()),
                color_continuous_scale='Blues'
            )
            fig_redes.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        else:
            fig_redes = go.Figure()
            fig_redes.update_layout(title='Dados insuficientes para uso de redes sociais')
        
        # Recebimento de notícias por redes sociais - Ponderado
        redes_noticias = ['recebe notícia redes: whatsapp', 'recebe notícia redes: instagram', 
                          'recebe notícia redes: facebook', 'recebe notícia redes: youtube', 
                          'recebe notícia redes: tiktok', 'recebe notícia redes: x/ antigo twitter']
        
        noticias_redes = {}
        for rede in redes_noticias:
            if rede in filtered_df.columns:
                rede_nome = rede.replace('recebe notícia redes: ', '')
                # Calcular como percentual do total
                total_peso = filtered_df['peso'].sum()
                rede_df = filtered_df[filtered_df[rede] == 'Sim']
                if len(rede_df) > 0 and total_peso > 0:
                    noticias_redes[rede_nome] = (rede_df['peso'].sum() / total_peso) * 100
                else:
                    noticias_redes[rede_nome] = 0
        
        if noticias_redes:
            fig_noticias = px.bar(
                x=list(noticias_redes.keys()), 
                y=list(noticias_redes.values()),
                labels={'x': 'Rede Social', 'y': 'Percentual de Recebimento (%)'},
                title='Recebimento de Notícias por Redes Sociais',
                color=list(noticias_redes.values()),
                color_continuous_scale='Reds'
            )
            fig_noticias.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        else:
            fig_noticias = go.Figure()
            fig_noticias.update_layout(title='Dados insuficientes para recebimento de notícias')
        
        # Frequência de leitura de notícias - Ponderada
        freq_col = 'com que frequência lê notícias da cidade/ região'
        if freq_col in filtered_df.columns:
            freq_noticias = weighted_percentage(filtered_df, freq_col)
            if not freq_noticias.empty:
                fig_freq = px.pie(
                    values=freq_noticias.values, 
                    names=freq_noticias.index,
                    title='Frequência de Leitura de Notícias (%)',
                    color_discrete_sequence=px.colors.sequential.Blues
                )
                fig_freq.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
            else:
                fig_freq = go.Figure()
                fig_freq.update_layout(title='Dados insuficientes para frequência de leitura')
        else:
            fig_freq = go.Figure()
            fig_freq.update_layout(title='Coluna de frequência de leitura não encontrada')
        
        # Sites/blogs de notícias - Ponderados
        site_col = 'site/ blog de notícias p5a'
        if site_col in filtered_df.columns:
            sites_noticias = weighted_percentage(filtered_df, site_col).nlargest(10)
            if not sites_noticias.empty:
                fig_sites = px.bar(
                    x=sites_noticias.index, 
                    y=sites_noticias.values,
                    labels={'x': 'Site/Blog', 'y': 'Percentual (%)'},
                    title='Top 10 Sites/Blogs de Notícias',
                    color=sites_noticias.values,
                    color_continuous_scale='Blues'
                )
                fig_sites.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
            else:
                fig_sites = go.Figure()
                fig_sites.update_layout(title='Dados insuficientes para sites/blogs')
        else:
            fig_sites = go.Figure()
            fig_sites.update_layout(title='Coluna de sites/blogs não encontrada')
        
        return html.Div([
            html.Div([
                html.Div([
                    create_graph_card(fig_redes, 'Uso de Redes Sociais'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_noticias, 'Recebimento de Notícias por Redes Sociais'),
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.Div([
                    create_graph_card(fig_freq, 'Frequência de Leitura de Notícias'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_sites, 'Sites/Blogs de Notícias'),
                ], className='six columns'),
            ], className='row'),
        ])
    
    elif tab == 'tab-governo':
        # Gráficos para a aba de Avaliação de Governo - Ponderados
        
        # Estado está no rumo certo ou errado - Ponderado
        rumo_col = 'avaliação imagem: sergipe está caminhando no rumo certo ou errado?'
        if rumo_col in filtered_df.columns:
            rumo_count = weighted_percentage(filtered_df, rumo_col)
            if not rumo_count.empty:
                fig_rumo = px.pie(
                    values=rumo_count.values,
                    names=rumo_count.index,
                    title='Sergipe está caminhando no rumo certo ou errado? (%)',
                    color_discrete_sequence=px.colors.sequential.Blues
                )
                fig_rumo.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
            else:
                fig_rumo = go.Figure()
                fig_rumo.update_layout(title='Dados insuficientes para direção do estado')
        else:
            fig_rumo = go.Figure()
            fig_rumo.update_layout(title='Coluna de direção do estado não encontrada')
        
        # Avaliação do Governador - Ponderada
        gov_col = 'avaliação imagem: governador fábio mitidieri'
        if gov_col in filtered_df.columns:
            gov_count = weighted_percentage(filtered_df, gov_col)
            if not gov_count.empty:
                fig_gov = px.pie(
                    values=gov_count.values, 
                    names=gov_count.index,
                    title='Avaliação do Governador (%)',
                    color_discrete_sequence=px.colors.sequential.Reds
                )
                fig_gov.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
            else:
                fig_gov = go.Figure()
                fig_gov.update_layout(title='Dados insuficientes para avaliação do governador')
        else:
            fig_gov = go.Figure()
            fig_gov.update_layout(title='Coluna de avaliação do governador não encontrada')
        
        # Aprovação do Governador - Ponderada
        apr_gov_col = 'aprovação imagem: governador fábio mitidieri'
        if apr_gov_col in filtered_df.columns:
            apr_gov_count = weighted_percentage(filtered_df, apr_gov_col)
            if not apr_gov_count.empty:
                fig_apr_gov = px.pie(
                    values=apr_gov_count.values, 
                    names=apr_gov_count.index,
                    title='Aprovação do Governador (%)',
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig_apr_gov.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
            else:
                fig_apr_gov = go.Figure()
                fig_apr_gov.update_layout(title='Dados insuficientes para aprovação do governador')
        else:
            fig_apr_gov = go.Figure()
            fig_apr_gov.update_layout(title='Coluna de aprovação do governador não encontrada')
        
        # Avaliação de Políticas Públicas - Ponderada
        politicas = [
            'avaliação educação: ensino público e escolas estaduais',
            'avaliação emprego: geração de empregos',
            'avaliação saneamento: abastecimento de água',
            'avaliação saúde: saúde pública no geral',
            'avaliação segurança: segurança pública'
        ]
        
        # Criando um dataframe para as avaliações ponderadas
        politicas_data = []
        for politica in politicas:
            if politica in filtered_df.columns:
                area = politica.split(':')[0].replace('avaliação ', '')
                
                # Calcular a contagem ponderada para cada avaliação
                avaliacao_values = filtered_df[politica].dropna().unique()
                avaliacao_values = [av for av in avaliacao_values if av != '.']
                
                for avaliacao in avaliacao_values:
                    mask = filtered_df[politica] == avaliacao
                    peso_total = filtered_df.loc[mask, 'peso'].sum()
                    all_peso = filtered_df.loc[filtered_df[politica].isin(avaliacao_values), 'peso'].sum()
                    
                    if all_peso > 0:  # Evitar divisão por zero
                        percentual = (peso_total / all_peso) * 100
                        politicas_data.append({
                            'Área': area,
                            'Avaliação': avaliacao,
                            'Percentual': percentual
                        })
        
        if politicas_data:
            df_politicas = pd.DataFrame(politicas_data)
            
            fig_politicas = px.bar(
                df_politicas,
                x='Área',
                y='Percentual',
                color='Avaliação',
                barmode='group',
                title='Avaliação de Políticas Públicas (%)',
                color_discrete_sequence=px.colors.sequential.Plasma_r
            )
            fig_politicas.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        else:
            fig_politicas = go.Figure()
            fig_politicas.update_layout(
                title='Dados insuficientes para avaliação de políticas públicas',
            )
        
        return html.Div([
            html.Div([
                html.Div([
                    create_graph_card(fig_rumo, 'Direção do Estado'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_gov, 'Avaliação do Governador'),
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.Div([
                    create_graph_card(fig_apr_gov, 'Aprovação do Governador'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_politicas, 'Avaliação de Políticas Públicas'),
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.H2('Avaliação de Figuras Políticas', 
                      style={'textAlign': 'center', 'color': colors['text'], 'marginTop': '30px'}),
                
                html.Div([
                    dcc.Dropdown(
                        id='figura-dropdown',
                        options=[
                            {'label': 'Ex-governador Belivaldo Chagas', 'value': 'avaliação imagem: ex-governador belivaldo chagas'},
                            {'label': 'Edvaldo Nogueira (ex-prefeito de Aracaju)', 'value': 'avaliação imagem: edvaldo nogueira, ex-prefeito de aracaju'},
                            {'label': 'Emília Corrêa (prefeita eleita de Aracaju)', 'value': 'avaliação imagem: emília corrêa, prefeita eleita de aracaju'},
                            {'label': 'Presidente Lula', 'value': 'avaliação imagem: presidente lula'},
                            {'label': 'Ex-presidente Jair Bolsonaro', 'value': 'avaliação imagem: ex-presidente jair bolsonaro'},
                        ],
                        value='avaliação imagem: ex-governador belivaldo chagas',
                        style={'width': '100%', 'marginBottom': '20px'}
                    )
                ]),
                
                html.Div(id='figura-graph')
            ]),
        ])
    
    elif tab == 'tab-programas':
        # Gráficos para a aba de Programas - Ponderados
        
        # Conhecimento dos programas - Ponderado como percentual
        programas = grupos_colunas['programas'][:10]  # Limitando a 10 programas para melhor visualização
        
        # Preparar dados para o gráfico com ponderação
        programas_data = []
        for programa in programas:
            if programa in filtered_df.columns:
                nome_programa = programa.split(':')[1].strip() if ':' in programa else programa
                if len(nome_programa) > 30:
                    nome_programa = nome_programa[:27] + '...'
                
                # Total de pesos para este programa (Sim + Não)
                programa_df = filtered_df[(filtered_df[programa] == 'Sim') | (filtered_df[programa] == 'Não')]
                total_peso = programa_df['peso'].sum()
                
                # Calcular percentuais
                sim_df = filtered_df[filtered_df[programa] == 'Sim']
                sim_peso = sim_df['peso'].sum()
                
                nao_df = filtered_df[filtered_df[programa] == 'Não']
                nao_peso = nao_df['peso'].sum()
                
                if total_peso > 0:  # Evitar divisão por zero
                    sim_perc = (sim_peso / total_peso) * 100
                    nao_perc = (nao_peso / total_peso) * 100
                    
                    programas_data.append({
                        'Programa': nome_programa,
                        'Conhece (%)': round(sim_perc, 2),
                        'Não Conhece (%)': round(nao_perc, 2)
                    })
        
        df_programas = pd.DataFrame(programas_data)
        
        # Gráfico de barras empilhadas para conhecimento dos programas
        if not df_programas.empty:
            fig_programas = px.bar(
                df_programas,
                x='Programa',
                y=['Conhece (%)', 'Não Conhece (%)'],
                title='Conhecimento dos Programas do Governo (%)',
                barmode='stack',
                labels={'value': 'Percentual (%)', 'variable': 'Resposta'},
                color_discrete_sequence=['#1E88E5', '#FFC107']
            )
            fig_programas.update_traces(texttemplate='%{y:.2f}%', textposition='inside')
            fig_programas.update_layout(xaxis_tickangle=-45)
        else:
            fig_programas = go.Figure()
            fig_programas.update_layout(
                title='Dados insuficientes para análise de programas',
            )
        
        # Gráfico de pizza para comparar conhecimento de algum programa específico - Ponderado
        programa_destaque = 'evento: verão sergipe, arraiá do povo e vila do forró'
        if programa_destaque in filtered_df.columns:
            prog_dest_count = weighted_percentage(filtered_df, programa_destaque)
            if not prog_dest_count.empty:
                fig_prog_destaque = px.pie(
                    values=prog_dest_count.values, 
                    names=prog_dest_count.index,
                    title=f'Conhecimento: {programa_destaque.split(":")[1].strip()} (%)',
                    color_discrete_sequence=px.colors.sequential.Blues
                )
                fig_prog_destaque.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
            else:
                fig_prog_destaque = go.Figure()
                fig_prog_destaque.update_layout(title='Dados insuficientes para programa destaque')
        else:
            fig_prog_destaque = go.Figure()
            fig_prog_destaque.update_layout(title='Programa destaque não encontrado nos dados')
        
        # Top programas mais conhecidos - Ponderado como percentual
        conhecimento_programas = {}
        for programa in grupos_colunas['programas']:
            if programa in filtered_df.columns:
                # Total para este programa
                programa_df = filtered_df[(filtered_df[programa] == 'Sim') | (filtered_df[programa] == 'Não')]
                total_peso = programa_df['peso'].sum()
                
                # Contagem de 'Sim'
                sim_df = filtered_df[filtered_df[programa] == 'Sim']
                sim_peso = sim_df['peso'].sum()
                
                if total_peso > 0:  # Evitar divisão por zero
                    conhecimento_programas[programa] = (sim_peso / total_peso) * 100
        
        top_programas = dict(sorted(conhecimento_programas.items(), key=lambda x: x[1], reverse=True)[:5])
        top_programas_nomes = [p.split(':')[1].strip() if ':' in p else p for p in top_programas.keys()]
        
        if len(top_programas_nomes) > 0:
            # Abreviar nomes muito longos
            top_programas_nomes = [n[:27] + '...' if len(n) > 30 else n for n in top_programas_nomes]
            
            fig_top_prog = px.bar(
                x=top_programas_nomes, 
                y=list(top_programas.values()),
                labels={'x': 'Programa', 'y': 'Conhecimento (%)'},
                title='Top 5 Programas Mais Conhecidos',
                color=list(top_programas.values()),
                color_continuous_scale='Blues'
            )
            fig_top_prog.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
            fig_top_prog.update_layout(xaxis_tickangle=-45)
        else:
            fig_top_prog = go.Figure()
            fig_top_prog.update_layout(
                title='Dados insuficientes para Top 5 Programas',
            )
        
        return html.Div([
            html.Div([
                html.Div([
                    create_graph_card(fig_programas, 'Conhecimento dos Programas'),
                ], className='twelve columns'),
            ], className='row'),
            
            html.Div([
                html.Div([
                    create_graph_card(fig_prog_destaque, 'Destaque: Eventos de Verão e Arraiá'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_top_prog, 'Top Programas Mais Conhecidos'),
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.H2('Análise de Programa Específico', 
                       style={'textAlign': 'center', 'color': colors['text'], 'marginTop': '30px'}),
                
                html.Div([
                    dcc.Dropdown(
                        id='programa-dropdown',
                        options=[{'label': p.split(':')[1].strip() if ':' in p else p, 
                                 'value': p} for p in grupos_colunas['programas']],
                        value=grupos_colunas['programas'][0],
                        style={'width': '100%', 'marginBottom': '20px'}
                    )
                ]),
                
                html.Div(id='programa-graph')
            ]),
        ])
    
    elif tab == 'tab-figuras':
        # Gráficos para a aba de Figuras Públicas - Ponderados
        
        # Pegar algumas figuras públicas populares para análise
        figuras_populares = [
            'conhece figura: linda brasil',
            'conhece figura: narcizo machado',
            'conhece figura: adiberto de souza',
            'conhece figura: luiz carlos focca',
            'conhece figura: claudio nunes'
        ]
        
        # Conhecimento das figuras públicas - Ponderado como percentual
        conhecimento_figuras = {}
        for figura in figuras_populares:
            if figura in filtered_df.columns:
                # Total para esta figura
                figura_df = filtered_df[(filtered_df[figura] == 'Sim') | (filtered_df[figura] == 'Não')]
                total_peso = figura_df['peso'].sum()
                
                # Contagem de 'Sim'
                sim_df = filtered_df[filtered_df[figura] == 'Sim']
                sim_peso = sim_df['peso'].sum()
                
                if total_peso > 0:  # Evitar divisão por zero
                    conhecimento_figuras[figura.replace('conhece figura: ', '')] = (sim_peso / total_peso) * 100
        
        if conhecimento_figuras:
            fig_conhecimento = px.bar(
                x=list(conhecimento_figuras.keys()), 
                y=list(conhecimento_figuras.values()),
                labels={'x': 'Figura Pública', 'y': 'Percentual que Conhece (%)'},
                title='Conhecimento de Figuras Públicas',
                color=list(conhecimento_figuras.values()),
                color_continuous_scale='Blues'
            )
            fig_conhecimento.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        else:
            fig_conhecimento = go.Figure()
            fig_conhecimento.update_layout(title='Dados insuficientes para conhecimento de figuras públicas')
        
        # Imagem das figuras - Ponderada
        figura_destaque = 'linda brasil'
        imagem_col = f'imagem figura: {figura_destaque}'
        if imagem_col in filtered_df.columns:
            img_figura = weighted_percentage(filtered_df, imagem_col)
            if not img_figura.empty:
                fig_imagem = px.pie(
                    values=img_figura.values, 
                    names=img_figura.index,
                    title=f'Imagem de {figura_destaque.title()} (%)',
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig_imagem.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
            else:
                fig_imagem = go.Figure()
                fig_imagem.update_layout(title=f'Dados insuficientes para Imagem de {figura_destaque.title()}')
        else:
            fig_imagem = go.Figure()
            fig_imagem.update_layout(title=f'Coluna de imagem para {figura_destaque} não encontrada')
        
        # Frequência de acompanhamento - Ponderada
        freq_col = f'freq. Acompanhamento figura: {figura_destaque}'
        if freq_col in filtered_df.columns:
            freq_df = filtered_df[filtered_df[freq_col] != '.']
            freq_acompanhamento = weighted_percentage(freq_df, freq_col) if not freq_df.empty else pd.Series()
            
            if not freq_acompanhamento.empty:
                fig_freq = px.pie(
                    values=freq_acompanhamento.values, 
                    names=freq_acompanhamento.index,
                    title=f'Frequência de Acompanhamento: {figura_destaque.title()} (%)',
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig_freq.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
            else:
                fig_freq = go.Figure()
                fig_freq.update_layout(title=f'Dados insuficientes para Frequência de Acompanhamento')
        else:
            fig_freq = go.Figure()
            fig_freq.update_layout(title=f'Coluna de frequência para {figura_destaque} não encontrada')
        
        # Análise de conhecimento por região - Ponderada
        conhece_col = f'conhece figura: {figura_destaque}'
        
        try:
            if conhece_col in filtered_df.columns:
                conhecimento_por_regiao = weighted_crosstab(filtered_df, 'região', conhece_col)
                
                if not conhecimento_por_regiao.empty and 'Sim' in conhecimento_por_regiao.columns:
                    fig_regiao = px.bar(
                        x=conhecimento_por_regiao.index,
                        y=conhecimento_por_regiao['Sim'],
                        labels={'x': 'Região', 'y': 'Percentual que Conhece (%)'},
                        title=f'Conhecimento de {figura_destaque.title()} por Região',
                        color=conhecimento_por_regiao['Sim'],
                        color_continuous_scale='Viridis'
                    )
                    fig_regiao.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
                else:
                    fig_regiao = go.Figure()
                    fig_regiao.update_layout(title=f'Dados insuficientes para análise por região')
            else:
                fig_regiao = go.Figure()
                fig_regiao.update_layout(title=f'Coluna de conhecimento para {figura_destaque} não encontrada')
        except:
            fig_regiao = go.Figure()
            fig_regiao.update_layout(title=f'Erro ao calcular conhecimento por região')
        
        return html.Div([
            html.Div([
                html.Div([
                    create_graph_card(fig_conhecimento, 'Conhecimento de Figuras Públicas'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_imagem, f'Imagem de {figura_destaque.title()}'),
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.Div([
                    create_graph_card(fig_freq, f'Frequência de Acompanhamento: {figura_destaque.title()}'),
                ], className='six columns'),
                
                html.Div([
                    create_graph_card(fig_regiao, f'Conhecimento por Região: {figura_destaque.title()}'),
                ], className='six columns'),
            ], className='row'),
            
            html.Div([
                html.H2('Análise de Figura Pública Específica', 
                      style={'textAlign': 'center', 'color': colors['text'], 'marginTop': '30px'}),
                
                html.Div([
                    dcc.Dropdown(
                        id='figura-publica-dropdown',
                        options=[{'label': f.replace('conhece figura: ', ''), 
                                 'value': f} for f in figuras_populares],
                        value=figuras_populares[0],
                        style={'width': '100%', 'marginBottom': '20px'}
                    )
                ]),
                
                html.Div(id='figura-publica-graph')
            ]),
        ])

# Callbacks para gráficos dinâmicos considerando filtros e ponderação

# Callback para atualizar os dropdowns quando os filtros são limpos
@callback(
    [Output({'type': 'filtro-dropdown', 'index': filtro}, 'value') for filtro in filtros_config],
    Input('limpar-filtros', 'n_clicks'),
    prevent_initial_call=True
)
def limpar_todos_filtros(n_clicks):
    if n_clicks:
        return [[] for _ in filtros_config]
    raise dash.exceptions.PreventUpdate

# Callback para atualizar o gráfico de figura política
@callback(
    Output('figura-graph', 'children'),
    [Input('figura-dropdown', 'value'),
     Input('filtros-aplicados', 'data')]
)
def update_figura_graph(figura_col, filtros_aplicados):
    # Filtrar o dataframe com base nos filtros aplicados
    filtered_df = filter_dataframe(df, filtros_aplicados)
    
    if len(filtered_df) == 0:
        return html.Div([
            html.H3("Nenhum dado encontrado com os filtros aplicados.", 
                   style={'textAlign': 'center', 'color': 'red', 'margin': '50px'})
        ])
    
    # Verificar se a coluna existe no DataFrame
    if figura_col not in filtered_df.columns:
        return html.Div([
            html.H3(f"Coluna '{figura_col}' não encontrada no conjunto de dados.", 
                   style={'textAlign': 'center', 'color': 'red', 'margin': '50px'})
        ])
    
    # Filtrar valores vazios e calcular contagem ponderada
    figura_data = weighted_percentage(filtered_df, figura_col)
    
    if figura_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f'Dados insuficientes para {figura_col.split(":")[1].strip() if ":" in figura_col else figura_col}',
        )
    else:
        fig = px.pie(
            values=figura_data.values, 
            names=figura_data.index,
            title=f'Avaliação: {figura_col.split(":")[1].strip() if ":" in figura_col else figura_col} (%)',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
    
    return create_graph_card(fig, 'Detalhes da Avaliação')

# Callback para atualizar o gráfico de programa específico
@callback(
    Output('programa-graph', 'children'),
    [Input('programa-dropdown', 'value'),
     Input('filtros-aplicados', 'data')]
)
def update_programa_graph(programa_col, filtros_aplicados):
    # Filtrar o dataframe com base nos filtros aplicados
    filtered_df = filter_dataframe(df, filtros_aplicados)
    
    if len(filtered_df) == 0:
        return html.Div([
            html.H3("Nenhum dado encontrado com os filtros aplicados.", 
                   style={'textAlign': 'center', 'color': 'red', 'margin': '50px'})
        ])
    
    # Verificar se a coluna existe no DataFrame
    if programa_col not in filtered_df.columns:
        return html.Div([
            html.H3(f"Coluna '{programa_col}' não encontrada no conjunto de dados.", 
                   style={'textAlign': 'center', 'color': 'red', 'margin': '50px'})
        ])
    
    # Filtrar valores vazios e calcular percentual ponderado
    programa_data = weighted_percentage(filtered_df, programa_col)
    
    # Gráfico de pizza para o programa
    if programa_data.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f'Dados insuficientes para {programa_col.split(":")[1].strip() if ":" in programa_col else programa_col}',
        )
    else:
        fig = px.pie(
            values=programa_data.values, 
            names=programa_data.index,
            title=f'Conhecimento: {programa_col.split(":")[1].strip() if ":" in programa_col else programa_col} (%)',
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
    
    # Análise por região - Ponderada
    try:
        conhecimento_por_regiao = weighted_crosstab(filtered_df, 'região', programa_col)
        
        if not conhecimento_por_regiao.empty and 'Sim' in conhecimento_por_regiao.columns:
            fig_regiao = px.bar(
                x=conhecimento_por_regiao.index,
                y=conhecimento_por_regiao['Sim'],
                labels={'x': 'Região', 'y': 'Percentual que Conhece (%)'},
                title=f'Conhecimento por Região',
                color=conhecimento_por_regiao['Sim'],
                color_continuous_scale='Viridis'
            )
            fig_regiao.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
        else:
            fig_regiao = go.Figure()
            fig_regiao.update_layout(
                title=f'Dados insuficientes para análise por região',
            )
    except:
        fig_regiao = go.Figure()
        fig_regiao.update_layout(
            title=f'Erro ao calcular conhecimento por região',
        )
    
    return html.Div([
        html.Div([
            create_graph_card(fig, 'Detalhes do Programa'),
        ], className='six columns'),
        
        html.Div([
            create_graph_card(fig_regiao, 'Conhecimento por Região'),
        ], className='six columns'),
    ], className='row')

# Callback para atualizar o gráfico de figura pública específica
@callback(
    Output('figura-publica-graph', 'children'),
    [Input('figura-publica-dropdown', 'value'),
     Input('filtros-aplicados', 'data')]
)
def update_figura_publica_graph(figura_col, filtros_aplicados):
    # Filtrar o dataframe com base nos filtros aplicados
    filtered_df = filter_dataframe(df, filtros_aplicados)
    
    if len(filtered_df) == 0:
        return html.Div([
            html.H3("Nenhum dado encontrado com os filtros aplicados.", 
                   style={'textAlign': 'center', 'color': 'red', 'margin': '50px'})
        ])
    
    # Verificar se a coluna existe no DataFrame
    if figura_col not in filtered_df.columns:
        return html.Div([
            html.H3(f"Coluna '{figura_col}' não encontrada no conjunto de dados.", 
                   style={'textAlign': 'center', 'color': 'red', 'margin': '50px'})
        ])
    
    figura_nome = figura_col.replace('conhece figura: ', '')
    
    # Conhecimento da figura - Ponderado
    conhecimento_data = weighted_percentage(filtered_df, figura_col)
    
    if conhecimento_data.empty:
        fig_conhecimento = go.Figure()
        fig_conhecimento.update_layout(
            title=f'Dados insuficientes para Conhecimento de {figura_nome}',
        )
    else:
        fig_conhecimento = px.pie(
            values=conhecimento_data.values, 
            names=conhecimento_data.index,
            title=f'Conhecimento: {figura_nome} (%)',
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig_conhecimento.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
    
    # Imagem da figura - Ponderada
    imagem_col = f'imagem figura: {figura_nome}'
    if imagem_col in filtered_df.columns:
        # Filtrar valores vazios
        imagem_df = filtered_df[filtered_df[imagem_col] != '.']
        imagem_data = weighted_percentage(imagem_df, imagem_col)
        
        if imagem_data.empty:
            fig_imagem = go.Figure()
            fig_imagem.update_layout(
                title=f'Dados insuficientes para Imagem de {figura_nome}',
            )
        else:
            fig_imagem = px.pie(
                values=imagem_data.values, 
                names=imagem_data.index,
                title=f'Imagem: {figura_nome} (%)',
                color_discrete_sequence=px.colors.sequential.RdBu
            )
            fig_imagem.update_traces(texttemplate='%{percent:.2%}', textposition='inside')
    else:
        fig_imagem = go.Figure()
        fig_imagem.update_layout(
            title=f'Dados de Imagem não disponíveis para {figura_nome}',
        )
    
    return html.Div([
        html.Div([
            create_graph_card(fig_conhecimento, f'Conhecimento: {figura_nome}'),
        ], className='six columns'),
        
        html.Div([
            create_graph_card(fig_imagem, f'Imagem: {figura_nome}'),
        ], className='six columns'),
    ], className='row')

# Executar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=False, host:'0.0.0.0')
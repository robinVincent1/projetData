import pandas as pd
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
from pathlib import Path
from scipy import stats

# Load the data
df = pd.read_excel(Path(__file__).parent / 'Extraction-finale_enquete-2023DS.xlsx')

app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1(children='Salary Analysis Dashboard', style={'textAlign': 'center'}),

    html.H2(children='Salary Distribution by Gender', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='genre-dropdown',
        options=[{'label': i, 'value': i} for i in df['Genre'].dropna().unique()],
        value=df['Genre'].dropna().unique()[0]
    ),
    dcc.Graph(id='genre-graph'),

    html.H2(children='Salary Distribution by Company Size', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='company-size-dropdown',
        options=[{'label': i, 'value': i} for i in df['Nombre de salarié·e·s de votre employeur / entreprise'].dropna().unique()],
        value=df['Nombre de salarié·e·s de votre employeur / entreprise'].dropna().unique()[0]
    ),
    dcc.Graph(id='company-size-graph'),

    html.Div(id='anova-result'),

    html.H2(children='Salary Distribution by Education', style={'textAlign': 'center'}),
    dcc.Graph(id='education-graph')
])

# Callback to update the genre graph
@app.callback(
    Output('genre-graph', 'figure'),
    Input('genre-dropdown', 'value')
)
def update_genre_graph(selected_genre):
    dff = df[df['Genre'] == selected_genre]
    fig = px.box(dff, x='Genre', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?',
                 labels={'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'Annual Salary with Bonuses'})
    return fig

# Callback to update the company size graph and perform ANOVA
@app.callback(
    Output('company-size-graph', 'figure'),
    Output('anova-result', 'children'),
    Input('company-size-dropdown', 'value')
)
def update_company_size_graph(selected_size):
    dff = df[df['Nombre de salarié·e·s de votre employeur / entreprise'] == selected_size]
    fig = px.box(dff, x='Nombre de salarié·e·s de votre employeur / entreprise', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?',
                 labels={'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'Annual Salary with Bonuses'})

    # Perform ANOVA for company size
    anova_data = [df[df['Nombre de salarié·e·s de votre employeur / entreprise'] == size]['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].dropna() 
                  for size in df['Nombre de salarié·e·s de votre employeur / entreprise'].dropna().unique()]
    anova_result = stats.f_oneway(*anova_data)
    anova_text = f'ANOVA Result for Company Size: F-statistic = {anova_result.statistic:.2f}, p-value = {anova_result.pvalue:.2e}'

    return fig, anova_text

# Callback to update the education graph
@app.callback(
    Output('education-graph', 'figure'),
    [Input('genre-dropdown', 'value'),  # Maintaining the dependency to refresh the graph.
     Input('company-size-dropdown', 'value')]
)
def update_education_graph(_, __):
    dff = df.groupby('Formation')['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].mean().reset_index()
    fig = px.bar(dff, x='Formation', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?',
    labels={'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'Average Annual Salary with Bonuses'})
    return fig


app.run_server(debug=True)
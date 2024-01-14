import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from pathlib import Path

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

    html.H2(children='Salary Distribution by Sector', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='sector-dropdown',
        options=[{'label': i, 'value': i} for i in df['Quel est le statut de votre employeur / entreprise ?'].dropna().unique()],
        value=df['Quel est le statut de votre employeur / entreprise ?'].dropna().unique()[0]
    ),
    dcc.Graph(id='sector-graph')
])

# Callbacks to update the graphs
@app.callback(
    Output('genre-graph', 'figure'),
    Input('genre-dropdown', 'value')
)
def update_genre_graph(selected_genre):
    dff = df[df['Genre'] == selected_genre]
    fig = px.box(dff, x='Genre', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?',
                 labels={'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'Annual Salary with Bonuses'})
    return fig

@app.callback(
    Output('sector-graph', 'figure'),
    Input('sector-dropdown', 'value')
)
def update_sector_graph(selected_sector):
    dff = df[df['Quel est le statut de votre employeur / entreprise ?'] == selected_sector]
    fig = px.box(dff, x='Quel est le statut de votre employeur / entreprise ?', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?',
                 labels={'Rémunération brute annuelle AVEC primes (AJ)': 'Annual Salary with Bonuses'})
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)

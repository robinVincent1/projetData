import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
from pathlib import Path

df = pd.read_excel(Path(__file__).parent / 'Extraction-finale_enquete-2023DS.xlsx')

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(
        id='genre-dropdown',
        options=[{'label': i, 'value': i} for i in df['Genre'].dropna().unique()],
        value=df['Genre'].dropna().unique()[0]
    ),
    dcc.Graph(id='graph-content')
])

@app.callback(
    Output('graph-content', 'figure'),
    Input('genre-dropdown', 'value')
)
def update_graph(selected_genre):
    dff = df[df['Genre'] == selected_genre]
    fig = px.box(dff, x='Genre', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
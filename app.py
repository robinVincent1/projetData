import pandas as pd
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
from sklearn.cluster import KMeans
from pathlib import Path
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Load the data
df = pd.read_excel(Path(__file__).parent / 'Extraction-finale_enquete-2023DS.xlsx')
telework_salary_df = df.groupby('Combien de jours par semaine êtes-vous en télétravail ? ')['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].mean().reset_index()
pca_columns = ['Quel est votre salaire brut ANNUEL AVEC PRIMES ?','Quelle est la durée de votre CDD ?','Depuis combien de mois occupez-vous cet emploi ?'] # Replace with actual column names
pca_df = df[pca_columns].dropna()
pca_df = StandardScaler().fit_transform(pca_df)

# Perform PCA
pca = PCA(n_components=2)
principal_components = pca.fit_transform(pca_df)
pca_result_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])

app = Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1(children='Dashboard des analyses des salaires', style={'textAlign': 'center'}),

    html.H2(children='Distribution des salaires par sexe', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='genre-dropdown',
        options=[{'label': i, 'value': i} for i in df['Genre'].dropna().unique()],
        value=df['Genre'].dropna().unique()[0]
    ),
    dcc.Graph(id='genre-graph'),

    html.H2(children="Distribution des salaires par taille d'entreprise", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='company-size-dropdown',
        options=[{'label': i, 'value': i} for i in df['Nombre de salarié·e·s de votre employeur / entreprise'].dropna().unique()],
        value=df['Nombre de salarié·e·s de votre employeur / entreprise'].dropna().unique()[0]
    ),
    dcc.Graph(id='company-size-graph'),

    html.Div(id='anova-result'),

    html.H2(children="Distribution des salaires en fonction de la filiaire d'origine", style={'textAlign': 'center'}),
    dcc.Graph(id='education-graph'),

    html.H2(children='Principal Component Analysis (PCA)', style={'textAlign': 'center'}),
    dcc.Graph(id='pca-graph'),
    
    html.H2(children='Salaire moyen en fonction du nombre de jours en télétravail', style={'textAlign': 'center'}),
    dcc.Graph(id='telework-days-bar-chart'),
    
    html.Div(id='telework-anova-result'),

    html.H2(children='Matrice des corrélations ', style={'textAlign': 'center'}),
    dcc.Graph(id='correlation-heatmap'),

    html.H2(children='Analyse de clusters', style={'textAlign': 'center'}),
    dcc.Graph(id='clustering-result'),

    html.H2(children='Salaire moyen en fonction de la région', style={'textAlign': 'center'}),
    html.Iframe(
        id='map',
        srcDoc=open('carteSalaireMoyen.html', 'r').read(),
        width='100%',
        height='600px'
    ),

    html.H2(children='Salaire moyen en fonction du pays', style={'textAlign': 'center'}),
    html.Iframe(
        id='map',
        srcDoc=open('carteSalaireMoyenWorld.html', 'r').read(),
        width='100%',
        height='600px'
    ),
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

@app.callback(
    Output('pca-graph', 'figure'),
    [Input('genre-dropdown', 'value'),  # Maintaining the dependency to refresh the graph.
     Input('company-size-dropdown', 'value')]
)
def update_pca_graph(_, __):
    fig = px.scatter(pca_result_df, x='PC1', y='PC2', title='PCA Result')
    return fig

# Callback to update the telework days bar chart
@app.callback(
    Output('telework-days-bar-chart', 'figure'),
    Input('genre-dropdown', 'value')  # Using an existing dropdown as a trigger
)
def update_telework_days_bar_chart(_):
    fig = px.bar(telework_salary_df, x='Combien de jours par semaine êtes-vous en télétravail ? ', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?',
                 labels={'Combien de jours par semaine êtes-vous en télétravail ? ': 'Telework Days per Week',
                         'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'Average Annual Salary with Bonuses'})
    return fig

# Callback pour calculer et afficher le résultat de l'ANOVA
@app.callback(
    Output('telework-anova-result', 'children'),
    Input('genre-dropdown', 'value')  # Utiliser n'importe quel Input existant pour déclencher le callback
)
def perform_telework_anova(_):
    # Préparer les données pour l'ANOVA
    anova_groups = [group['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].dropna() for name, group in df.groupby('Combien de jours par semaine êtes-vous en télétravail ? ')]

    # Réaliser l'ANOVA
    anova_result = stats.f_oneway(*anova_groups)

    # Renvoyer le résultat de l'ANOVA
    return html.Div([
        html.P(f'ANOVA F-statistic: {anova_result.statistic:.2f}'),
        html.P(f'ANOVA p-value: {anova_result.pvalue:.4f}')
    ])

@app.callback(
    Output('correlation-heatmap', 'figure'),
    [Input('genre-dropdown', 'value'),  # Utiliser un Input existant pour déclencher le callback
     Input('company-size-dropdown', 'value')]
)
def update_correlation_heatmap(_, __):
    # Sélectionner les colonnes pertinentes pour la corrélation
    cols_for_correlation = ['Quel est votre salaire brut ANNUEL AVEC PRIMES ?', 'Combien de jours par semaine êtes-vous en télétravail ? ', 'Depuis combien de mois occupez-vous cet emploi ?']  # Ajoutez d'autres colonnes si nécessaire
    correlation_df = df[cols_for_correlation].dropna()

    # Calculer la matrice de corrélation
    corr_matrix = correlation_df.corr()

    # Créer la heatmap de corrélation
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", 
                    labels=dict(x="Variable", y="Variable", color="Correlation"),
                    x=corr_matrix.columns, y=corr_matrix.columns)

    return fig

@app.callback(
    Output('clustering-result', 'figure'),
    [Input('genre-dropdown', 'value'),  # Peut utiliser n'importe quel Input existant
     Input('company-size-dropdown', 'value')]
)
def perform_clustering_analysis(_, __):
    # Sélectionner et préparer les données pour le clustering
    clustering_columns = ['Quel est votre salaire brut ANNUEL AVEC PRIMES ?','Combien de jours par semaine êtes-vous en télétravail ? ']
    clustering_df = df[clustering_columns].dropna()
    clustering_df = StandardScaler().fit_transform(clustering_df)

    # Effectuer le clustering
    kmeans = KMeans(n_clusters=4)  # Choisissez le nombre de clusters approprié
    clusters = kmeans.fit_predict(clustering_df)

    # Créer une visualisation pour les clusters
    fig = px.scatter(x=clustering_df[:, 0], y=clustering_df[:, 1], color=clusters, 
                     labels={'x': clustering_columns[0], 'y': clustering_columns[1]},
                     title='Cluster Analysis of Graduates')

    return fig

app.run_server(debug=True)
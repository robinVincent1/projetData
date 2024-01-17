import pandas as pd
from dash import Dash, dcc, html, Output, Input
import plotly.express as px
from sklearn.cluster import KMeans
from pathlib import Path
from scipy import stats
import plotly.tools as tls
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np


# Load the data
df = pd.read_excel(Path(__file__).parent / 'Extraction finale_enquete 2023DS (1).xlsx')
telework_salary_df = df.groupby('Combien de jours par semaine êtes-vous en télétravail ? ')['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].mean().reset_index()
pca_columns = ['Quel est votre salaire brut ANNUEL AVEC PRIMES ?','Quelle est la durée de votre CDD ?','Depuis combien de mois occupez-vous cet emploi ?'] # Replace with actual column names
pca_df = df[pca_columns].dropna()
pca_df = StandardScaler().fit_transform(pca_df)

# Perform PCA
pca = PCA(n_components=2)
principal_components = pca.fit_transform(pca_df)
pca_result_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
# Calculer le salaire moyen par secteur
mean_salary_by_sector = df.groupby('Quel est le secteur d\'activité de votre entreprise (celle qui vous rémunère)?')['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].mean().reset_index()

sectors = df['Quel est le secteur d\'activité de votre entreprise (celle qui vous rémunère)?'].unique()
anova_data = [df[df['Quel est le secteur d\'activité de votre entreprise (celle qui vous rémunère)?'] == sector]['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].dropna() for sector in sectors]


app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}
def perform_sector_anova():
    # Définir un seuil minimum de réponses par secteur
    min_responses_per_sector = 5

    # Filtrer les secteurs avec suffisamment de réponses
    anova_data = [df[df['Quel est le secteur d\'activité de votre entreprise (celle qui vous rémunère)?'] == sector]['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].dropna() 
                  for sector in sectors if len(df[df['Quel est le secteur d\'activité de votre entreprise (celle qui vous rémunère)?'] == sector]) >= min_responses_per_sector]

    # Vérifier s'il y a suffisamment de données pour effectuer l'ANOVA
    if len(anova_data) > 1:
        anova_result = stats.f_oneway(*anova_data)
        return html.Div([
            html.P(f'ANOVA sur le secteur d\'activité - F-statistic: {anova_result.statistic:.2f}'),
            html.P(f'ANOVA sur le secteur d\'activité - p-value: {anova_result.pvalue:.4f}')
        ])
    else:
        return html.Div([
            html.P('Pas assez de données pour effectuer l\'ANOVA sur les secteurs d\'activité.')
        ])
    
anova_result = perform_sector_anova()


def create_genre_graph():
    filtered_df = df[df['Genre'].isin(['Femme', 'Homme'])]
    fig = px.box(filtered_df, x='Genre', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?')
    return fig

genre_graph = create_genre_graph()

def create_employee_count_graph():
    choices = ["De 50 à 249 salarié·e·s", "5 000 salarié·e·s ou plus", "De 20 à 49 salarié·e·s", "De 10 à 19 salarié·e·s ", "250 à  4 999 salarié·e·s ", " Moins de 10 salarié·e·s"]
    filtered_df = df[df['Nombre de salarié·e·s de votre employeur / entreprise'].isin(choices)]
    fig = px.box(filtered_df, x='Nombre de salarié·e·s de votre employeur / entreprise', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?')
    return fig

employee_count_graph = create_employee_count_graph()

def create_executive_status_boxplot():
    # Filtrer le DataFrame
    filtered_df = df[df['Avez-vous un statut de cadre ou assimilé ?'].isin(['Oui', 'Non'])]

    # Créer le boxplot
    fig = px.box(filtered_df, x='Avez-vous un statut de cadre ou assimilé ?', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?')

    return fig

boxplot_cadre = create_executive_status_boxplot()

def create_employer_status_boxplot():
    # Filtrer le DataFrame
    filtered_df = df[df['Quel est le statut de votre employeur / entreprise ?'].isin(['Secteur privé', 'Secteur public'])]

    # Créer le boxplot
    fig = px.box(filtered_df, x='Quel est le statut de votre employeur / entreprise ?', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?')

    return fig

boxplot_employer = create_employer_status_boxplot()



def create_seaborn_plot():
    # Sélectionner les données pour le graphique
    salary_data = df['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].dropna()

    # Créer le graphique
    plt.figure(figsize=(10, 6))
    sns.distplot(salary_data, hist=True, kde=True, 
                 bins=int(180/5), color = 'darkblue', 
                 hist_kws={'edgecolor':'black'},
                 kde_kws={'linewidth': 4})

    plt.title('Distribution des salaires brut annuel avec primes')
    plt.xlabel('Salaire brut annuel avec primes'); plt.ylabel('Densité');

    # Convert the matplotlib figure to a Plotly figure and return it
    plotly_fig = tls.mpl_to_plotly(plt.gcf())
    return plotly_fig

loi_normale = create_seaborn_plot()
# Callback to update the genre graph


def create_education_graph():
    dff = df.groupby('Formation')['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].mean().reset_index()
    fig = px.bar(dff, x='Formation', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?',
    labels={'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'Average Annual Salary with Bonuses'})
    return fig

salaire_formation = create_education_graph()

def create_pca_graph():
    fig = px.scatter(pca_result_df, x='PC1', y='PC2', title='PCA Result')
    return fig

pca = create_pca_graph()

def create_telework_days_bar_chart():
    fig = px.bar(telework_salary_df, x='Combien de jours par semaine êtes-vous en télétravail ? ', y='Quel est votre salaire brut ANNUEL AVEC PRIMES ?',
                 labels={'Combien de jours par semaine êtes-vous en télétravail ? ': 'Telework Days per Week',
                         'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'Average Annual Salary with Bonuses'})
    return fig

telework_days_bar_chart = create_telework_days_bar_chart()
# Callback pour calculer et afficher le résultat de l'ANOVA


def perform_telework_anova():
    # Préparer les données pour l'ANOVA
    anova_groups = [group['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].dropna() for name, group in df.groupby('Combien de jours par semaine êtes-vous en télétravail ? ')]

    # Réaliser l'ANOVA
    anova_result = stats.f_oneway(*anova_groups)

    # Renvoyer le résultat de l'ANOVA
    return html.Div([
        html.P(f'ANOVA F-statistic: {anova_result.statistic:.2f}'),
        html.P(f'ANOVA p-value: {anova_result.pvalue:.4f}')
    ])

telework_anova_result = perform_telework_anova()

def create_correlation_heatmap():
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

correlation_heatmap = create_correlation_heatmap()

def perform_clustering_analysis():
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

clustering_result = perform_clustering_analysis()
# App layout
app.layout = html.Div([
    html.H1(children='Dashboard des analyses des salaires', style={'textAlign': 'center', "font-size": "300%"}),
    dcc.Graph(id='seaborn-graph'
              ,figure=loi_normale),
    html.Div([
        html.Div([
    dcc.Graph(id='executive-status-boxplot',
              figure=boxplot_cadre),
], className='six columns'),  # Utilisez les classes de grille CSS pour définir la largeur
    html.Div([
     dcc.Graph(id='employer-status-boxplot'
               ,figure=boxplot_employer),
], className='six columns'),  # Utilisez les classes de grille CSS pour définir la largeur
], className='row'),  # Utilisez la classe de grille CSS pour aligner les éléments horizontalement
    html.Div([
        html.Div([
            html.H2(children='Distribution des salaires par sexe', style={'textAlign': 'center'}),
            dcc.Graph(id='genre-graph',
                      figure=genre_graph),
        ], className='six columns'),  # Utilisez les classes de grille CSS pour définir la largeur

        html.Div([
            html.H2(children="Distribution des salaires par taille d'entreprise", style={'textAlign': 'center'}),
            dcc.Graph(id='company-size-graph',
                      figure=employee_count_graph),
        ], className='six columns'),  # Utilisez les classes de grille CSS pour définir la largeur
    ], className='row'),  # Utilisez la classe de grille CSS pour aligner les éléments horizontalement

    html.Div(id='anova-result'),
    html.H2(children="Distribution des salaires en fonction de la filiaire d'origine", style={'textAlign': 'center'}),
    dcc.Graph(id='education-graph',
              figure=salaire_formation),

    html.H2(children='Principal Component Analysis (PCA)', style={'textAlign': 'center'}),
    dcc.Graph(id='pca-graph',
              figure=pca),

    html.H2(children='Salaire moyen en fonction du nombre de jours en télétravail', style={'textAlign': 'center'}),
    dcc.Graph(id='telework-days-bar-chart',
              figure=telework_days_bar_chart),

    html.Div(id='telework-anova-result'),

    html.H2(children='Matrice des corrélations', style={'textAlign': 'center'}),
    dcc.Graph(id='correlation-heatmap',
              figure=correlation_heatmap),

    html.H2(children='Analyse de clusters', style={'textAlign': 'center'}),
    dcc.Graph(id='clustering-result',
              figure=clustering_result),
html.H2(children="L'influence de la situation géographique", style={'textAlign': 'center',"font-size": "500%"}),
html.Div([
    html.Div([
        html.H2(children='Salaire moyen en fonction de la région', style={'textAlign': 'center'}),
        html.Iframe(
            id='map',
            srcDoc=open('carteSalaireMoyen.html', 'r').read(),
            width='100%',
            height='600px'
        ),
    ], className='six columns'),

    html.Div([
        html.H2(children='Salaire moyen en fonction du pays', style={'textAlign': 'center'}),
        html.Iframe(
            id='map',
            srcDoc=open('carteSalaireMoyenWorld.html', 'r').read(),
            width='100%',
            height='600px'
        ),
    ], className='six columns'),
], className='row'),
])






app.run_server(debug=True)
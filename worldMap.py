import pandas as pd
import folium
import geopandas as gpd
import json
from jinja2 import Template
from pathlib import Path


# Charger le fichier de données de l'utilisateur
df = pd.read_excel(Path(__file__).parent / 'Extraction-finale_enquete-2023DS.xlsx')

# Calculer la moyenne des salaires par région
salaires_par_region = df.groupby('Dans quel pays ?')['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].mean().reset_index()
salaires_par_region = salaires_par_region.rename(columns={'Dans quel pays ?': 'name_fr', 'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'salaire_moyen'})

# Charger les données géographiques des régions françaises
gdf_regions = gpd.read_file('worldMap.json')

# Fusionner les données des salaires avec les données géographiques
gdf_regions = gdf_regions.merge(salaires_par_region, on='name_fr')

# Convertir GeoDataFrame en JSON
geojson_regions = json.loads(gdf_regions.to_json())

# Créer une carte centrée sur la France
m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)

# Création d'une couche choroplèthe pour les salaires moyens
choropleth = folium.Choropleth(
    geo_data=geojson_regions,
    name='Salaire Moyen',
    data=gdf_regions,
    columns=['name_fr', 'salaire_moyen'],
    key_on='feature.properties.name_fr',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    highlight=True,
    reset=True
).add_to(m)

# Ajouter des popups pour afficher les informations lors d'un clic sur une région
choropleth.geojson.add_child(
    folium.GeoJsonPopup(['name_fr', 'salaire_moyen'],
                        aliases=['Région: ', 'Salaire moyen annuel avec primes: '],
                        labels=True)
)

# Ajouter une couche de contrôle pour permettre l'affichage ou non des couches
folium.LayerControl().add_to(m)

# Sauvegarder la carte dans un fichier HTML
m.save('carteSalaireMoyenWorld.html') 
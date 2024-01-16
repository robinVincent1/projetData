import pandas as pd
import folium
import geopandas as gpd
import json
from jinja2 import Template
from pathlib import Path


# Charger le fichier de données de l'utilisateur
df = pd.read_excel(Path(__file__).parent / 'Extraction-finale_enquete-2023DS.xlsx')

# Calculer la moyenne des salaires par région
salaires_par_region = df.groupby('Région de votre entreprise d\'accueil')['Quel est votre salaire brut ANNUEL AVEC PRIMES ?'].mean().reset_index()
salaires_par_region = salaires_par_region.rename(columns={'Région de votre entreprise d\'accueil': 'nom', 'Quel est votre salaire brut ANNUEL AVEC PRIMES ?': 'salaire_moyen'})

# Charger les données géographiques des régions françaises
gdf_regions = gpd.read_file('regionFrance.json')

# Fusionner les données des salaires avec les données géographiques
gdf_regions = gdf_regions.merge(salaires_par_region, on='nom')

# Convertir GeoDataFrame en JSON
geojson_regions = json.loads(gdf_regions.to_json())

# Créer une carte centrée sur la France
m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)

# Création d'une couche choroplèthe pour les salaires moyens
choropleth = folium.Choropleth(
    geo_data=geojson_regions,
    name='Salaire Moyen',
    data=gdf_regions,
    columns=['nom', 'salaire_moyen'],
    key_on='feature.properties.nom',
    fill_color='YlGnBu',
    fill_opacity=0.7,
    line_opacity=0.2,
    highlight=True,
    reset=True
).add_to(m)

# Ajouter des popups pour afficher les informations lors d'un clic sur une région
choropleth.geojson.add_child(
    folium.GeoJsonPopup(['nom', 'salaire_moyen'],
                        aliases=['Région: ', 'Salaire moyen annuel avec primes: '],
                        labels=True)
)

# Ajouter une couche de contrôle pour permettre l'affichage ou non des couches
folium.LayerControl().add_to(m)

# Sauvegarder la carte dans un fichier HTML
m.save('carteSalaireMoyen.html') 


# def extract_departement(code):
#     # Convertir en string si ce n'est pas une chaîne de caractères
#     code = str(code)

#     # Gère les cas comme '2A' ou '2B' pour la Corse
#     if code[:2].isalpha():
#         return code[:2]
#     else:  # Gère les cas numériques normaux
#         return code.zfill(5)[:2]


# # Charger les données des véhicules rechargeables électriques
# df_vehicules = pd.read_csv('voiture:commune.csv',
#                            sep=';', low_memory=False, header=0)
# df_vehicules['departement'] = df_vehicules['codgeo'].apply(extract_departement)
# df_vehicules['commune_id'] = df_vehicules['codgeo'] + \
#     '_' + df_vehicules['libgeo'].astype(str)
# df_vehicules_filtered = df_vehicules.drop_duplicates(
#     subset='commune_id', keep='last')
# total_vehicules_par_departement = df_vehicules_filtered.groupby(
#     'departement')['nb_vp_rechargeables_el'].sum()

# # Charger les données des points de charge
# df_pdc = pd.read_csv('borneIRVE.csv')
# df_pdc['departement'] = df_pdc['code_insee_commune'].apply(extract_departement)
# df_pdc = df_pdc[df_pdc['departement'].str.match(
#     '^[0-9]{2}|2[AB]$')]  # Filtre les départements valides
# total_pdc_par_departement = df_pdc.groupby('departement')['nbre_pdc'].sum()


# # Calculer la densité de points de charge par département
# densite_pdc_par_departement = total_pdc_par_departement / \
#     total_vehicules_par_departement
# densite_pdc_df = pd.DataFrame(densite_pdc_par_departement).reset_index()
# densite_pdc_df.columns = ['departement', 'densite_pdc']

# # Ajouter les colonnes pour le nombre total de véhicules et de points de charge
# densite_pdc_df = densite_pdc_df.merge(
#     total_vehicules_par_departement, on='departement')
# densite_pdc_df = densite_pdc_df.merge(
#     total_pdc_par_departement, on='departement')
# densite_pdc_df.rename(columns={
#                       'nb_vp_rechargeables_el': 'nb_vehicules', 'nbre_pdc': 'nb_bornes'}, inplace=True)

# # Définir les bornes pour les nuances de couleurs
# bornes = [0, 0.06, 0.0925, 0.122, 0.18, 0.37, 2, 9]
# bornesStr = ["0", "0.06", "0.0925", "0.122", "0.18", "0.37", "2", "9"]


# # Les couleurs correspondant à vos bornes
# couleurs_hex = ['#ffffd1', '#cde8b9', '#91cbbb',
#                 '#64b4c2', '#458fbc', '#335da3', '#152b7f']

# # Charger les données géographiques des départements français
# gdf_departements = gpd.read_file('departement.geojson')
# gdf_departements = gdf_departements.merge(
#     densite_pdc_df, left_on='code', right_on='departement')

# # Convertir GeoDataFrame en JSON
# geojson_departements = json.loads(gdf_departements.to_json())

# # Créer une carte centrée sur la France
# m = folium.Map(location=[46.2276, 2.2137], zoom_start=6)

# # Assigner une nuance de couleur à chaque département en utilisant des numéros
# def assigner_couleur_numerique(valeur):
#     for i in range(6):
#         if valeur < bornes[i + 1]:
#             return i
#     return 6


# densite_pdc_df['couleur_numerique'] = densite_pdc_df['densite_pdc'].apply(
#     assigner_couleur_numerique)

# # Création d'une couche choroplèthe avec les bornes et les couleurs personnalisées
# choropleth = folium.Choropleth(
#     geo_data=geojson_departements,
#     name='Densité',
#     data=densite_pdc_df,
#     columns=['departement', 'densite_pdc'],
#     key_on='feature.properties.code',
#     fill_color='YlGnBu',  # Utilisez votre palette de couleurs personnalisée ici
#     threshold_scale=bornes,  # Utilisez vos bornes personnalisées ici
#     # pour utiliser des strings comme bornes il ne faut pas utiliser threshold_scale mais utiliser fill_color=linear ou fill_color=step ou fill_color=div (voir doc)
#     fill_opacity=0.7,
#     line_opacity=0.2,
#     highlight=True,
#     reset=True  # Pour réinitialiser la légende à chaque fois que vous exécutez
# ).add_to(m)

# # Ajouter des popups pour afficher les informations lors d'un clic sur un département
# choropleth.geojson.add_child(
#     folium.GeoJsonPopup(['nom', 'densite_pdc', 'nb_vehicules', 'nb_bornes'],
#                         aliases=['Département: ', 'Densité: ',
#                                  'Nombre de véhicules: ', 'Nombre de bornes: '],
#                         labels=True,
#                         localize=True)
# )

# # Légende personnalisée en HTML
# legend_html = '''
# <div style="position: fixed; 
#             bottom: 50px; left: 50px; width: 250px; height: auto;
#             border:2px solid grey; border-radius: 3px; z-index:9999; font-size:14px;
#             background:white; padding:10px; box-sizing: border-box;">
#     <div style="text-align: center; margin-bottom: 10px;"><b>Légende</b></div>
#     <div style="text-align: center; margin-bottom: 10px; font-size: 14px; font-weight: normal;">Densité de points de charge par véhicule électrique</div>

#     <div style="display: flex; align-items: center; margin-bottom: 4px; margin-left: 10px;">
#         <i style="background:#ffffd1; width: 32px; height: 20px;"></i>
#         <span style="margin-left: 6px;">0 - 0.06</span>
#     </div>
#     <div style="display: flex; align-items: center; margin-bottom: 4px; margin-left: 10px;">
#         <i style="background:#cde8b9; width: 32px; height: 20px;"></i>
#         <span style="margin-left: 6px;">0.06 - 0.09</span>
#     </div>
#     <div style="display: flex; align-items: center; margin-bottom: 4px; margin-left: 10px;">
#         <i style="background:#91cbbb; width: 32px; height: 20px;"></i>
#         <span style="margin-left: 6px;">0.09 - 0.12</span>
#     </div>
#     <div style="display: flex; align-items: center; margin-bottom: 4px; margin-left: 10px;">
#         <i style="background:#64b4c2; width: 32px; height: 20px;"></i>
#         <span style="margin-left: 6px;">0.12 - 0.18</span>
#     </div>
#     <div style="display: flex; align-items: center; margin-bottom: 4px; margin-left: 10px;">
#         <i style="background:#458fbc; width: 32px; height: 20px;"></i>
#         <span style="margin-left: 6px;">0.18 -  0.37</span>
#     </div>
#     <div style="display: flex; align-items: center; margin-bottom: 4px; margin-left: 10px;">
#         <i style="background:#335da3; width: 32px; height: 20px;"></i>
#         <span style="margin-left: 6px;">0.37 - 2</span>
#     </div>
#     <div style="display: flex; align-items: center;">
#         <i style="background:#152b7f; width: 32px; height: 20px; margin-left: 10px;"></i>
#         <span style="margin-left: 6px;">2+</span>
#     </div>
# </div>


# '''

# # Retrait de la légende par défaut
# for key in choropleth._children:
#     if key.startswith('color_map'):
#         del choropleth._children[key]

# # Ajouter la légende personnalisée à la carte
# m.get_root().html.add_child(folium.Element(legend_html))


# # Charger les données géographiques des régions françaises
# gdf_regions = gpd.read_file('region.geojson')

# # Convertir GeoDataFrame des régions en JSON
# geojson_regions = json.loads(gdf_regions.to_json())

# # Création d'une couche pour les contours des régions avec folium.GeoJson
# contours_des_regions = folium.GeoJson(
#     geojson_regions,
#     style_function=lambda feature: {
#         'fillColor': 'none',
#         'fillOpacity': 0,
#         'color': 'darkblue',
#         'weight': 3,
#         'opacity': 1,
#     },
#     name='Contours des Régions'
# ).add_to(m)


# # Charger les données géographiques des autoroutes françaises à partir du fichier GeoJSON
# gdf_autoroutes = gpd.read_file('autoroutes.geojson')

# # Créer une fonction de style pour les autoroutes
# def style_function(feature):
#     return {
#         'fillColor': 'none',
#         'color': 'black',  # La couleur que vous voulez appliquer
#         'weight': 3,
#         'opacity': 1,
#     }

# # Ajouter les autoroutes à la carte avec la fonction de style
# autoroutes = folium.GeoJson(
#     gdf_autoroutes,
#     style_function=style_function,  # Utiliser la fonction de style ici
#     name='Autoroutes'
# ).add_to(m)

# # Ajouter une couche de contrôle pour permettre l'affichage ou non des autoroutes
# folium.LayerControl().add_to(m)


# # Sauvegarder la carte dans un fichier HTML
# m.save('carteFinale.html') 
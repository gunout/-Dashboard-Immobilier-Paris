# dashboard_paris_multi_arrondissements.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import requests
import io
from datetime import datetime

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Immobilier Paris",
    page_icon="🏙️",
    layout="wide"
)

# --- Dictionnaire des arrondissements de Paris (Code INSEE -> Nom) ---
# NOTE : Paris est divisé en 20 arrondissements avec des codes INSEE de 75101 à 75120
ARRONDISSEMENTS_PARIS = {
    "75101": "Paris 1er Arrondissement",
    "75102": "Paris 2ème Arrondissement",
    "75103": "Paris 3ème Arrondissement",
    "75104": "Paris 4ème Arrondissement",
    "75105": "Paris 5ème Arrondissement",
    "75106": "Paris 6ème Arrondissement",
    "75107": "Paris 7ème Arrondissement",
    "75108": "Paris 8ème Arrondissement",
    "75109": "Paris 9ème Arrondissement",
    "75110": "Paris 10ème Arrondissement",
    "75111": "Paris 11ème Arrondissement",
    "75112": "Paris 12ème Arrondissement",
    "75113": "Paris 13ème Arrondissement",
    "75114": "Paris 14ème Arrondissement",
    "75115": "Paris 15ème Arrondissement",
    "75116": "Paris 16ème Arrondissement",
    "75117": "Paris 17ème Arrondissement",
    "75118": "Paris 18ème Arrondissement",
    "75119": "Paris 19ème Arrondissement",
    "75120": "Paris 20ème Arrondissement",
}

# Inverser le dictionnaire pour avoir Nom -> Code INSEE (plus pratique pour le selectbox)
NOMS_ARRONDISSEMENTS = {v: k for k, v in ARRONDISSEMENTS_PARIS.items()}

# --- Fonction de chargement des données (générique) ---
@st.cache_data
def load_arrondissement_data(insee_code: str):
    """
    Charge les données DVF 2024 pour un arrondissement de Paris donné par son code INSEE.
    """
    url = f"https://files.data.gouv.fr/geo-dvf/latest/csv/2024/communes/75/{insee_code}.csv"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        df = pd.read_csv(io.StringIO(response.text), sep=',', low_memory=False)
        
        if df.empty:
            return pd.DataFrame()

        # Nettoyage (identique à la version précédente)
        df["date_mutation"] = pd.to_datetime(df["date_mutation"], format='%Y-%m-%d', errors='coerce')
        df["valeur_fonciere"] = pd.to_numeric(df["valeur_fonciere"], errors='coerce')
        df = df[df["type_local"].isin(['Maison', 'Appartement'])]
        
        if df.empty:
            return pd.DataFrame()

        df = df.dropna(subset=["valeur_fonciere", "surface_reelle_bati", "code_postal", "date_mutation"])
        df["surface_reelle_bati"] = pd.to_numeric(df["surface_reelle_bati"], errors='coerce')
        df = df.dropna(subset=["surface_reelle_bati"])

        if df.empty:
            return pd.DataFrame()

        df['prix_m2'] = df['valeur_fonciere'] / df['surface_reelle_bati']
        df = df[(df['prix_m2'] > 200) & (df['prix_m2'] < 15000)]
        
        if df.empty:
            return pd.DataFrame()
        
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Erreur de connexion pour l'arrondissement {insee_code} : {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Une erreur est survenue : {e}")
        return pd.DataFrame()

# --- Interface Utilisateur ---
st.title("🏙️ Dashboard Immobilier Paris")

# Sélection de l'arrondissement dans la barre latérale
st.sidebar.header("Sélection de l'arrondissement")
selected_arrondissement_name = st.sidebar.selectbox(
    "Choisissez un arrondissement :",
    options=sorted(NOMS_ARRONDISSEMENTS.keys())
)

# Récupérer le code INSEE correspondant
selected_insee_code = NOMS_ARRONDISSEMENTS[selected_arrondissement_name]

# Afficher un message d'information dynamique
st.info(f"ℹ️ Données réelles DVF 2024 pour l'arrondissement de **{selected_arrondissement_name}** (INSEE {selected_insee_code}), provenant de data.gouv.fr")

# --- Chargement et Traitement des Données ---
df = load_arrondissement_data(selected_insee_code)

if df.empty:
    st.warning(f"Aucune donnée de vente (Maison/Appartement) valide trouvée pour {selected_arrondissement_name} en 2024.")
    st.stop()

# --- Filtres ---
st.sidebar.header("Filtres")
codes_postaux_disponibles = sorted(df['code_postal'].astype(str).unique())
code_postal_selectionne = st.sidebar.multiselect("Code postal", codes_postaux_disponibles, default=codes_postaux_disponibles)
type_local = st.sidebar.selectbox("Type de bien", ['Tous', 'Maison', 'Appartement'])
prix_min = st.sidebar.number_input("Prix minimum (€)", value=0, step=10000)
prix_max = st.sidebar.number_input("Prix maximum (€)", value=int(df['valeur_fonciere'].max()), step=10000)

# Application des filtres
df_filtre = df[
    (df['code_postal'].astype(str).isin(code_postal_selectionne)) &
    (df['valeur_fonciere'] >= prix_min) &
    (df['valeur_fonciere'] <= prix_max)
].copy()

if type_local != 'Tous':
    df_filtre = df_filtre[df_filtre['type_local'] == type_local]

if df_filtre.empty:
    st.warning("Aucune transaction ne correspond à vos filtres.")
    st.stop()

# --- KPIs et Visualisations ---
st.header(f"Indicateurs Clés pour {selected_arrondissement_name}")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Prix Moyen / m²", f"{df_filtre['prix_m2'].mean():.0f} €")
with col2:
    st.metric("Prix Médian", f"{df_filtre['valeur_fonciere'].median():.0f} €")
with col3:
    st.metric("Transactions", f"{len(df_filtre):,}")
with col4:
    surface_moyenne = df_filtre['surface_reelle_bati'].mean()
    st.metric("Surface Moyenne", f"{surface_moyenne:.0f} m²")

st.header(f"Visualisations pour {selected_arrondissement_name}")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Répartition des Prix au m²")
    fig = px.histogram(df_filtre, x='prix_m2', nbins=50, color='type_local', marginal="box")
    st.plotly_chart(fig, use_container_width=True)
with col2:
    st.subheader("Répartition des Types de Biens")
    fig = px.pie(df_filtre, names='type_local', title='Répartition par type')
    st.plotly_chart(fig, use_container_width=True)

st.subheader(f"Carte des Transactions à {selected_arrondissement_name}")
if 'latitude' in df_filtre.columns and 'longitude' in df_filtre.columns:
    df_carte = df_filtre.sample(min(5000, len(df_filtre)))
    fig = px.scatter_mapbox(df_carte, lat="latitude", lon="longitude", color="prix_m2", size="surface_reelle_bati", hover_data=["valeur_fonciere", "type_local", "date_mutation"], color_continuous_scale=px.colors.sequential.Viridis, size_max=15, zoom=11, mapbox_style="open-street-map", title=f"Carte de {len(df_carte)} transactions (échantillon)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Les données de localisation (latitude/longitude) ne sont pas disponibles pour afficher la carte.")

st.subheader("Détail des Transactions (dernières)")
st.dataframe(df_filtre.sort_values('date_mutation', ascending=False).head(100).drop(columns=['latitude', 'longitude'], errors='ignore'))
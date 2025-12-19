import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")

st.title("🏠 Dashboard Immobilier Interactif")

st.markdown("""
### 🎯 Problématique
Comment les caractéristiques d’un bien immobilier (surface, localisation,
nombre de pièces, options, DPE) influencent-elles le prix de vente et le prix au m² ?
""")

st.markdown("""
### 📍 Périmètre de l’étude
L’analyse se concentre sur **18 grandes villes françaises** afin d’assurer :
- un volume suffisant de transactions
- une meilleure comparabilité des prix
- une réduction de l’hétérogénéité du marché
""")

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "..", "DATA", "ANNONCES_CLEAN.CSV")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df

df = load_data()

st.markdown("### 📊 Résumé du jeu de données")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Annonces", f"{len(df):,}")
col2.metric("Villes", df["ville"].nunique())
col3.metric("Prix médian", f"{int(df['prix_de_vente'].median()):,} €")
col4.metric("Surface médiane", f"{int(df['surface_m2'].median())} m²")

st.markdown("""
**Source des données** : ParuVendu.fr  
**Méthode** : Web scraping, nettoyage et analyse exploratoire
""")

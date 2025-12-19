import streamlit as st

st.set_page_config(layout="wide")

st.title("🧪 Méthodologie – Scraping & ETL")

st.markdown("""
## 🔍 Étape 1 – Web Scraping
Les données ont été collectées à partir du site **ParuVendu.fr** via :
- requêtes HTTP
- parsing HTML
- extraction des informations clés (prix, surface, ville, DPE, options…)

## 🧹 Étape 2 – Nettoyage des données
- suppression des annonces incomplètes
- conversion des variables numériques
- harmonisation des noms de colonnes
- création de variables dérivées (prix au m²)

## 🔄 Étape 3 – ETL
- **Extract** : récupération des annonces
- **Transform** : nettoyage, enrichissement
- **Load** : stockage dans un fichier CSV exploitable

## 🎯 Objectif
Garantir un jeu de données :
- fiable
- homogène
- prêt pour l’analyse exploratoire
""")

import streamlit as st
from theme import load_css, load_matplotlib_theme

# ------------------------------------------------------------
# THEME GLOBAL
# ------------------------------------------------------------
load_css()
load_matplotlib_theme()

# ------------------------------------------------------------
# PAGE CONTENT
# ------------------------------------------------------------
st.title("🧪 Méthodologie – Scraping & Nettoyage des données immobilières")

# Onglets
tabs = st.tabs(["🔍 Scraping", "🧹 Cleaning / ETL"])

# ------------------------------------------------------------
# ONGLET 1 : SCRAPING
# ------------------------------------------------------------
with tabs[0]:
    st.header("🔍 Étape 1 – Scraping")
    st.markdown("""
    Le scraping consiste à **collecter automatiquement les annonces immobilières**
    depuis ParuVendu.fr.
    
    ### Méthode
    - Requêtes HTTP avec `requests` et User-Agent personnalisé.
    - Parsing HTML avec `BeautifulSoup`.
    - Extraction des informations clés :
      - **Titre** et **lien** de l'annonce
      - **Prix**
      - **Ville**
      - **Description courte**
      - **Détails** (pièces, chambres, options comme garage, balcon, ascenseur)
      - **Localisation** de l’annonce

    ### Gestion des enjeux
    - Détection et arrêt en cas de **CAPTCHA** pour éviter le blocage.
    - Limitation du nombre d'annonces par exécution (`MAX_ANNONCES_PAR_RUN`).
    - Checkpointing : sauvegarde automatique de la dernière ville et page
      pour pouvoir **reprendre le scraping en cas d’interruption**.
    - Fusion et déduplication avec les anciennes annonces pour éviter les doublons.

    ### Difficultés surmontées
    - Structure HTML variable selon les annonces.
    - Informations manquantes ou mal formatées.
    - Gestion de volumes importants de données.
    - Nécessité de ralentir les requêtes pour ne pas être bloqué.

    ### Résultat
    À la fin du scraping, on obtient un fichier CSV brut
    (**ANNONCES_RAW.csv**) contenant :
    - Ville, titre, lien, description, prix, localisation, détails
    - Données encore susceptibles de contenir doublons ou valeurs manquantes
    """)

# ------------------------------------------------------------
# ONGLET 2 : CLEANING / ETL
# ------------------------------------------------------------
with tabs[1]:
    st.header("🧹 Étape 2 – Nettoyage et ETL")
    st.markdown("""
    Après le scraping, les données brutes sont transformées pour devenir
    **fiables et exploitables**.

    ### Étapes de nettoyage
    - Standardisation des noms de villes et des types de biens.
    - Nettoyage des textes (`description`, `détails`).
    - Extraction des informations :
      - Nombre de pièces et chambres
      - Options : garage, balcon, ascenseur
      - Terrain, DPE
    - Conversion des prix et surfaces en valeurs numériques.
    - Détection et suppression des doublons.
    - Filtrage des biens indésirables (terrains, garages, commerces…).
    - Suppression des valeurs aberrantes (outliers).
    - Optionnel : géocodage (latitude / longitude).

    ### Difficultés surmontées
    - Données manquantes ou incohérentes.
    - Formats hétérogènes (prix, surfaces, textes).
    - Extraction complexe à partir de descriptions libres.

    ### Résultat
    Le nettoyage produit un fichier CSV propre
    (**ANNONCES_CLEAN.csv**) prêt pour l’analyse et les visualisations.
    """)



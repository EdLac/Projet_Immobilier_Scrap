import streamlit as st

# Configuration de la page
st.set_page_config(layout="wide", page_title="Méthodologie – Scraping & Cleaning")

st.title("🧪 Méthodologie – Scraping & Nettoyage des données immobilières")

# Onglets
tabs = st.tabs(["🔍 Scraping", "🧹 Cleaning / ETL"])


# Onglet 1 : Scraping

with tabs[0]:
    st.header("🔍 Étape 1 – Scraping")
    st.markdown("""
    Le scraping consiste à **collecter automatiquement les annonces immobilières** depuis ParuVendu.fr.
    
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
    - Checkpointing : sauvegarde automatique de la dernière ville et page pour pouvoir **reprendre le scraping en cas d’interruption**.
    - Fusion et déduplication avec les anciennes annonces pour éviter les doublons.

    ### Difficultés surmontées
    - Structure HTML variable selon les annonces.
    - Informations manquantes ou mal formatées.
    - Gestion de volumes importants de données.
    - Besoin de ralentir les requêtes pour ne pas être bloqué.

    ### Résultat
    À la fin du scraping, on obtient un fichier CSV brut (**ANNONCES_RAW.csv**) contenant pour chaque annonce :
    - Ville, titre, lien, description, prix, localisation, détails
    - Chaque ligne correspond à une annonce unique, mais **les données peuvent encore contenir des doublons, des valeurs manquantes ou mal formatées**.
    """)


# Onglet 2 : Cleaning / ETL

with tabs[1]:
    st.header("🧹 Étape 2 – Nettoyage et ETL")
    st.markdown("""
    Après le scraping, les données brutes sont transformées pour devenir **fiables et exploitables**.

    ### Étapes de nettoyage
    - Standardisation des noms de villes et des types de biens.
    - Nettoyage des textes (`Description`, `Détails`) pour supprimer retours à la ligne, espaces inutiles ou caractères spéciaux.
    - Extraction des informations des détails :
      - Nombre de pièces et chambres
      - Options : garage, balcon, ascenseur
      - Terrain, DPE
    - Conversion des prix et surfaces en valeurs numériques.
    - Détection et suppression des doublons.
    - Filtrage des biens indésirables (terrains, garages, commerces, hôtels...).
    - Suppression des valeurs aberrantes (outliers) sur le prix et le prix au m².
    - Optionnel : géocodage pour obtenir latitude et longitude.

    ### Difficultés surmontées
    - Valeurs manquantes ou incohérentes dans certains champs.
    - Formats différents pour le prix, la surface et les détails.
    - Extraction des informations à partir de chaînes de texte complexes.
    - Besoin de standardiser les types de biens pour l’analyse.

    ### Résultat
    À la fin du nettoyage, on obtient un fichier CSV propre (**ANNONCES_CLEAN.csv**) contenant pour chaque annonce :
    - Ville standardisée
    - Type de bien homogène
    - Prix de vente et prix au m²
    - Surface, nombre de pièces et chambres
    - Options : garage, balcon, ascenseur
    - Terrain et DPE si disponibles
    - Localisation exploitable et éventuellement coordonnées GPS
    - Données dédupliquées, filtrées et prêtes pour analyse et visualisations
    """)

# 🏠 Analyse du marché immobilier en France  
### Projet – DU Data Analytics

## 📌 Contexte du projet

Ce projet s’inscrit dans le cadre de la formation **DU Data Analytics**.  
Il a été réalisé en **binôme (Edouard & Élise)** avec pour objectif pédagogique de :

- découvrir et maîtriser le **web scraping**,
- nettoyer et structurer des données réelles,
- réaliser une **analyse exploratoire de données**,
- concevoir un **dashboard interactif** permettant de visualiser et interpréter les résultats.

Le projet s’adresse à la fois :
- à un **public académique** (enseignants, jury),
- et au **grand public**, souhaitant comprendre les dynamiques du marché immobilier français.

---

## 🎯 Problématique

> **Comment le prix au mètre carré varie-t-il en fonction de la localisation, de la surface et du type de biens immobiliers en France ?**

Pour répondre à cette question, l’analyse se concentre sur **20 grandes villes françaises**, choisies pour leur représentativité et leur dynamisme immobilier.

---

## 🌐 Source des données

- **Site scrappé** : [ParuVendu.fr](https://www.paruvendu.fr/immobilier/)
- **Type de données** : annonces immobilières de vente
- **Périmètre** :
  - 20 grandes villes françaises
  - 5 premières pages de résultats par ville
  - > 2 000 annonces finales exploitables

---

## 🛠️ Technologies & outils utilisés

### Scraping
- `requests`
- `BeautifulSoup`
- Gestion de sessions HTTP
- Détection de CAPTCHA
- Système de **checkpoint (JSON)** pour reprise automatique

### Data processing
- `pandas`
- `numpy`
- `regex`
- Nettoyage, normalisation, déduplication
- Enrichissement des données (prix/m², options, DPE…)

### Analyse & visualisation
- `matplotlib`
- `seaborn`
- Histogrammes
- Boxplots
- Scatterplots + régression
- Matrice de corrélation

### Dashboard
- `Streamlit`
- `pydeck` (heatmap géographique)
- Interface interactive avec filtres dynamiques

---

## 🧱 Architecture du projet

Projet_Immobilier_Scrap/
│
├── SRC/
│   ├── app.py                     # App Streamlit principale
│   ├── theme.py                   # Thème graphique (néon)
│   ├── scraper.py                 # Scraping + gestion anti-bot
│   └── pages/
│       ├── 1_🏠_Accueil.py
│       ├── 2_🛠️_Methodologie.py
│       └── 3_📊_Analyse.py
│
├── DATA/
│   ├── ANNONCES_RAW.csv           # Données brutes scrappées
│   └── ANNONCES_CLEAN.csv         # Données nettoyées
│
├── checkpoint.json                # Sauvegarde de l’état du scraping
├── EXPLORATION.ipynb              # Analyses exploratoires
├── ANALYSE.py                     # Analyse statistique standalone
├── Rapport-Python-Avance.pdf      # Rapport final
└── README.md



---

## 🔐 Stratégie de scraping & anti-bot

Le scraping des pages de résultats ne posait pas de difficulté majeure.  
En revanche, l’accès aux pages **individuelles des annonces**, nécessaire pour récupérer la localisation précise, a entraîné des **blocages fréquents** du site.

Pour y faire face, plusieurs mécanismes ont été mis en place :

- détection automatique des pages CAPTCHA ;
- limitation du nombre d’annonces récupérées par exécution ;
- pauses entre les requêtes (`sleep`) ;
- système de **checkpoint** (ville + page) stocké dans un fichier JSON ;
- reprise automatique du scraping à partir du dernier point valide.

Cette stratégie a permis de construire un **processus robuste et résilient**, capable de fonctionner malgré les restrictions du site.

`---

## 📊 Analyses réalisées

### Statistiques descriptives
- moyenne et médiane du prix au m²,
- distribution des prix de vente,
- distribution des surfaces.

### Analyses visuelles
- histogrammes des prix et surfaces,
- boxplots par :
  - type de bien,
  - options (balcon, garage, ascenseur),
  - classe énergétique (DPE),
- scatterplots surface vs prix avec régression,
- carte de chaleur géographique (heatmap),
- matrice de corrélation.

---

## 🧠 Principaux enseignements

- forte **dispersion des prix**, traduisant l’hétérogénéité du marché ;
- **corrélation positive forte** entre surface et prix de vente ;
- influence marquée de la **localisation** sur le prix au m² ;
- écarts significatifs entre **appartements et maisons** ;
- impact observable de la **performance énergétique (DPE)** sur les prix.

---

## 🚀 Lancer le projet

### Installation des dépendances

`pip install -r requirements.txt`

Lancer le dashboard Streamlit

`streamlit run SRC/app.py`

👥 Auteurs

Edouard  
Élise

Projet réalisé en binôme dans le cadre du DU Data Analytics.

📄 Licence & usage

Projet réalisé à des fins pédagogiques.
Les données proviennent de ParuVendu.fr et sont utilisées uniquement à des fins d’analyse et de démonstration.

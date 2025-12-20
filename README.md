# 🏠 Analyse du marché immobilier en France  
### Projet – DU Data Analytics

## 📌 Contexte du projet

Ce projet s’inscrit dans le cadre de la formation **DU Data Analytics**.  
Il a été réalisé en **binôme (Edouard & Yves)** avec pour objectif pédagogique de :

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

Pour répondre à cette question, l’analyse se concentre sur **18 grandes villes françaises**, choisies pour leur représentativité et leur dynamisme immobilier.

---

## 🌐 Source des données

- **Site scrappé** : [ParuVendu.fr](https://www.paruvendu.fr/immobilier/)
- **Type de données** : annonces immobilières de vente
- **Périmètre** :
  - 18 grandes villes françaises
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

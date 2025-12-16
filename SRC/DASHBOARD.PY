import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os


# Chargement des données

@st.cache_data  #garder les données en mémoire pour accélérer le rechargement
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "DATA", "ANNONCES_CLEAN.CSV")
    df = pd.read_csv(csv_path)
    # Nettoyer les noms de colonnes : enlever espaces et mettre en minuscules
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df

df = load_data()


# Configuration de la page 

st.set_page_config(page_title="Dashboard Immobilier", layout="wide")  # utiliser toute la largeur de l'écran
st.title("Dashboard Immobilier Interactif")
st.write("Analyse des prix, options, corrélations et distributions.")

# Filtres dans la sidebar

st.sidebar.header("Filtres")

villes = st.sidebar.multiselect(
    "Ville",
    options=sorted(df["ville"].unique()),
    default=sorted(df["ville"].unique())
)

surface_min, surface_max = st.sidebar.slider(
    "Surface (m²)",
    int(df["surface_m2"].min()),
    int(df["surface_m2"].max()),
    (int(df["surface_m2"].min()), int(df["surface_m2"].max()))
)

prix_min, prix_max = st.sidebar.slider(
    "Prix (€)",
    int(df["prix_de_vente"].min()),
    int(df["prix_de_vente"].max()),
    (int(df["prix_de_vente"].min()), int(df["prix_de_vente"].max()))
)

pieces = st.sidebar.multiselect(
    "Nombre de pièces",
    options=sorted(df["pieces"].dropna().unique()),
    default=sorted(df["pieces"].dropna().unique())
)

types_bien = st.sidebar.multiselect(
    "Type de bien",
    options=sorted(df["type"].dropna().unique()),
    default=sorted(df["type"].dropna().unique())
)

dpe_options = df["dpe"].dropna().unique()
dpe_selected = st.sidebar.multiselect(
    "DPE",
    options=sorted(dpe_options),
    default=sorted(dpe_options)
)

garage_filter = st.sidebar.checkbox("Avec garage")
balcon_filter = st.sidebar.checkbox("Avec balcon")
ascenseur_filter = st.sidebar.checkbox("Avec ascenseur")


# Application des filtres

df_filtre = df[
    (df["ville"].isin(villes)) &
    (df["surface_m2"].between(surface_min, surface_max)) &
    (df["prix_de_vente"].between(prix_min, prix_max)) &
    (df["pieces"].isin(pieces)) &
    (df["type"].isin(types_bien)) &
    (df["dpe"].isin(dpe_selected))
]

# Si les cases sont cochées, on filtre pour garder uniquement les biens avec ces options
if garage_filter:
    df_filtre = df_filtre[df_filtre["garage"] > 0]
if balcon_filter:
    df_filtre = df_filtre[df_filtre["balcon"] > 0]
if ascenseur_filter:
    df_filtre = df_filtre[df_filtre["ascenseur"] > 0]


# KPIs par type de bien

st.subheader("KPIs principaux par type de bien")
for t in types_bien:
    df_type = df_filtre[df_filtre["type"] == t]
    with st.expander(f"{t}"):  # permet de cacher ou montrer les kpis
        col1, col2, col3 = st.columns(3)
        col1.metric("Nb annonces", len(df_type))
        col2.metric("Prix moyen au m²", f"{df_type['prix_m2'].mean():.0f} €")
        col3.metric("Prix médian au m²", f"{df_type['prix_m2'].median():.0f} €")

        col1, col2, col3 = st.columns(3)
        col1.metric("Prix min", f"{df_type['prix_m2'].min():.0f} €")
        col2.metric("Prix max", f"{df_type['prix_m2'].max():.0f} €")
        col3.metric("Écart-type", f"{df_type['prix_m2'].std():.0f} €")

        col1, col2, col3 = st.columns(3)
        col1.metric("Surface moyenne", f"{df_type['surface_m2'].mean():.1f} m²")
        col2.metric("Nb pièces moyen", f"{df_type['pieces'].mean():.1f}")
        col3.metric("Nb chambres moyen", f"{df_type['chambres'].mean():.1f}")


# ---Graphiques Analyse des prix et surfaces---

st.subheader("Analyse des prix et surfaces")

# Histogrammes prix et surface côte à côte
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(6,4))
    sns.histplot(df_filtre['prix_de_vente'], bins=30, kde=True, color="#69b3a2", ax=ax)  # kde=True trace une courbe lisse
    ax.set_title("Distribution des prix")
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(6,4))
    sns.histplot(df_filtre['surface_m2'], bins=30, kde=True, color="#FFA07A", ax=ax)
    ax.set_title("Distribution des surfaces")
    st.pyplot(fig)

# Boxplot prix vs nombre de pièces
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(6,4))
    sns.boxplot(data=df_filtre, x='pieces', y='prix_de_vente', palette="pastel", ax=ax)
    ax.set_title("Prix vs Nombre de pièces")
    st.pyplot(fig)

# Scatter plot amélioré Prix vs Surface
with col2:
    fig, ax = plt.subplots(figsize=(6,4))
    sizes = df_filtre['chambres'].fillna(1) * 30  # taille des points selon nb de chambres
    sns.scatterplot(
        data=df_filtre,
        x='surface_m2',
        y='prix_de_vente',
        hue='type',          # couleur selon type de bien
        size='chambres',     # taille selon chambres
        sizes=(20, 200),
        alpha=0.7,
        palette='Set2',
        ax=ax
    )
    ax.set_title("Prix vs Surface (taille selon chambres, couleur type)")
    ax.set_xlabel("Surface (m²)")
    ax.set_ylabel("Prix (€)")
    st.pyplot(fig)


# Histogramme prix au m² par ville

st.subheader("Prix au m² par ville")
fig, ax = plt.subplots(figsize=(8,4))
order = df_filtre.groupby("ville")["prix_m2"].median().sort_values().index
sns.barplot(
    data=df_filtre,
    x="ville",
    y="prix_m2",
    order=order,
    estimator=np.median,  # utilise la médiane pour chaque ville
    errorbar=None,         # pas d'erreur bar affichée
    palette="pastel",
    ax=ax
)
plt.xticks(rotation=45, ha="right")
ax.set_ylabel("Prix au m² (€)")
st.pyplot(fig)


# Diagramme de corrélation Prix vs Surface

st.subheader("Corrélation Prix vs Surface")
fig, ax = plt.subplots(figsize=(8,5))
sns.regplot(
    data=df_filtre,
    x='surface_m2',
    y='prix_de_vente',
    scatter_kws={'alpha':0.5, 'color':'#FFA07A'},  # alpha pour rendre les points transparents
    line_kws={'color':'#69b3a2'},                   # ligne de régression
    ax=ax
)
ax.set_xlabel("Surface (m²)")
ax.set_ylabel("Prix (€)")
st.pyplot(fig)


# Analyse des options

st.subheader("Analyse des options")
col1, col2, col3 = st.columns(3)
options = ['balcon', 'garage', 'ascenseur']
for idx, opt in enumerate(options):
    with [col1, col2, col3][idx]:
        counts = df_filtre[opt].fillna(0).apply(lambda x: 'Oui' if x>0 else 'Non').value_counts()
        fig, ax = plt.subplots(figsize=(4,4))
        counts.plot.pie(autopct='%1.1f%%', startangle=90, colors=['#69b3a2','#FFA07A'], ax=ax)
        ax.set_ylabel('')
        ax.set_title(f"{opt.capitalize()}")
        st.pyplot(fig)

# Stacked bar chart DPE/type
st.write("Proportion des biens par type et DPE")
fig, ax = plt.subplots(figsize=(10,4))
stacked_df = df_filtre.groupby(['type','dpe']).size().unstack(fill_value=0)  # unstack transforme les DPE en colonnes
stacked_df.plot(kind='bar', stacked=True, ax=ax, colormap='Pastel1')
plt.ylabel("Nombre d'annonces")
st.pyplot(fig)


# Heatmap corrélations

st.subheader("Matrice de corrélation")
fig, ax = plt.subplots(figsize=(8,6))
corr_vars = ['prix_de_vente', 'surface_m2', 'pieces', 'chambres', 'prix_m2']
sns.heatmap(df_filtre[corr_vars].corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)  # annot=True affiche les valeurs sur la heatmap
ax.set_title("Matrice de corrélation")
st.pyplot(fig)

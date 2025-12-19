# 3_📊_Analyse.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Configuration page
st.set_page_config(page_title="Analyse Immobilier", layout="wide")

st.title("📊 Analyse du marché immobilier")


# CHARGEMENT DES DONNÉES

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Remontée de deux dossiers pour atteindre la racine du projet
    csv_path = os.path.join(base_dir, "..", "..", "DATA", "ANNONCES_CLEAN.CSV")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df

df = load_data()


# SIDEBAR – FILTRES

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

dpe_selected = st.sidebar.multiselect(
    "DPE",
    options=sorted(df["dpe"].dropna().unique()),
    default=sorted(df["dpe"].dropna().unique())
)

garage_filter = st.sidebar.checkbox("Avec garage")
balcon_filter = st.sidebar.checkbox("Avec balcon")
ascenseur_filter = st.sidebar.checkbox("Avec ascenseur")

if st.sidebar.button("🔄 Réinitialiser les filtres"):
    st.session_state.clear()
    st.experimental_rerun()


# FILTRAGE DES DONNÉES

df_filtre = df[
    (df["ville"].isin(villes)) &
    (df["surface_m2"].between(surface_min, surface_max)) &
    (df["prix_de_vente"].between(prix_min, prix_max)) &
    (df["pieces"].isin(pieces)) &
    (df["type"].isin(types_bien)) &
    (df["dpe"].isin(dpe_selected))
]

if garage_filter:
    df_filtre = df_filtre[df_filtre["garage"] > 0]
if balcon_filter:
    df_filtre = df_filtre[df_filtre["balcon"] > 0]
if ascenseur_filter:
    df_filtre = df_filtre[df_filtre["ascenseur"] > 0]


# KPIs

st.subheader("📌 Indicateurs clés par type de bien")

for t in types_bien:
    df_type = df_filtre[df_filtre["type"] == t]
    if df_type.empty:
        continue

    with st.expander(f"{t}", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Annonces", f"{len(df_type):,}")
        col2.metric("Prix médian", f"{int(df_type['prix_de_vente'].median()):,} €")
        col3.metric("Prix médian €/m²", f"{int(df_type['prix_m2'].median()):,} €")
        col4.metric("Surface médiane", f"{int(df_type['surface_m2'].median())} m²")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Pièces moyennes", f"{df_type['pieces'].mean():.1f}")
        col2.metric("Chambres moyennes", f"{df_type['chambres'].mean():.1f}")

        pct_balcon = (df_type["balcon"] > 0).mean() * 100
        pct_garage = (df_type["garage"] > 0).mean() * 100

        col3.metric("Avec balcon", f"{pct_balcon:.0f} %")
        col4.metric("Avec garage", f"{pct_garage:.0f} %")


# TABS ANALYSE

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Vue d’ensemble",
    "📐 Prix & Surfaces",
    "🏙️ Localisation",
    "🏠 Caractéristiques",
    "⚡ DPE",
    "🔗 Corrélations"
])

with tab1:
    st.subheader("Vue d’ensemble du marché")
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        sns.histplot(df_filtre["prix_de_vente"], bins=30, kde=True, ax=ax)
        ax.set_title("Distribution des prix de vente")
        st.pyplot(fig)
    with col2:
        fig, ax = plt.subplots()
        sns.histplot(df_filtre["surface_m2"], bins=30, kde=True, ax=ax)
        ax.set_title("Distribution des surfaces")
        st.pyplot(fig)

with tab2:
    st.subheader("Relation entre surface et prix")
    fig, ax = plt.subplots(figsize=(7,5))
    sns.scatterplot(
        data=df_filtre,
        x="surface_m2",
        y="prix_de_vente",
        hue="type",
        alpha=0.6,
        ax=ax
    )
    sns.regplot(
        data=df_filtre,
        x="surface_m2",
        y="prix_de_vente",
        scatter=False,
        color="black",
        ax=ax
    )
    ax.set_xlabel("Surface (m²)")
    ax.set_ylabel("Prix (€)")
    st.pyplot(fig)

with tab3:
    st.subheader("Prix médian au m² par ville")
    order = df_filtre.groupby("ville")["prix_m2"].median().sort_values().index
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(
        data=df_filtre,
        x="ville",
        y="prix_m2",
        order=order,
        estimator=np.median,
        errorbar=None,
        ax=ax
    )
    plt.xticks(rotation=45, ha="right")
    ax.set_ylabel("Prix médian au m² (€)")
    st.pyplot(fig)

with tab4:
    st.subheader("Impact des caractéristiques sur le prix au m²")
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        sns.boxplot(data=df_filtre, x="type", y="prix_m2", ax=ax)
        ax.set_title("Prix au m² par type de bien")
        st.pyplot(fig)
    with col2:
        for opt in ["balcon", "garage", "ascenseur"]:
            fig, ax = plt.subplots()
            sns.boxplot(
                data=df_filtre,
                x=df_filtre[opt].map({0: "Non", 1: "Oui"}),
                y="prix_m2",
                ax=ax
            )
            ax.set_title(f"Impact du {opt}")
            ax.set_xlabel("")
            st.pyplot(fig)

with tab5:
    st.subheader("Impact du DPE sur le prix au m²")
    fig, ax = plt.subplots()
    sns.boxplot(
        data=df_filtre,
        x="dpe",
        y="prix_m2",
        order=["A","B","C","D","E","F","G"],
        ax=ax
    )
    ax.set_xlabel("Classe DPE")
    ax.set_ylabel("Prix au m² (€)")
    st.pyplot(fig)

with tab6:
    st.subheader("Matrice de corrélation")
    vars_corr = ["prix_de_vente","prix_m2","surface_m2","pieces","chambres"]
    fig, ax = plt.subplots(figsize=(6,5))
    sns.heatmap(
        df_filtre[vars_corr].corr(),
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        ax=ax
    )
    st.pyplot(fig)

    st.subheader("🧠 Insights clés")
    st.markdown("""
    - 📈 Forte corrélation entre surface et prix de vente
    - 🏙️ Prix au m² plus élevés pour les appartements
    - 🚗 Les options valorisent significativement le bien
    - ⚡ Le DPE influence positivement la valorisation
    """)

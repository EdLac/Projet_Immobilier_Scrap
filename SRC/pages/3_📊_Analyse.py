import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

st.set_page_config(layout="wide")

st.title("📊 Analyse du marché immobilier")

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "..", "DATA", "ANNONCES_CLEAN.CSV")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df

df = load_data()

# =======================
# SIDEBAR – FILTRES
# =======================
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

types_bien = st.sidebar.multiselect(
    "Type de bien",
    options=sorted(df["type"].dropna().unique()),
    default=sorted(df["type"].dropna().unique())
)

# =======================
# FILTRAGE
# =======================
df_filtre = df[
    (df["ville"].isin(villes)) &
    (df["surface_m2"].between(surface_min, surface_max)) &
    (df["prix_de_vente"].between(prix_min, prix_max)) &
    (df["type"].isin(types_bien))
]

# =======================
# KPIs
# =======================
st.subheader("📌 Indicateurs clés")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Annonces", f"{len(df_filtre):,}")
col2.metric("Prix médian", f"{int(df_filtre['prix_de_vente'].median()):,} €")
col3.metric("Surface médiane", f"{int(df_filtre['surface_m2'].median())} m²")
col4.metric("Prix médian €/m²", f"{int(df_filtre['prix_m2'].median()):,} €")

# =======================
# TABS ANALYSE
# =======================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vue d’ensemble",
    "📐 Prix & Surfaces",
    "🏙️ Localisation",
    "🔗 Corrélations"
])

with tab1:
    fig, ax = plt.subplots()
    sns.histplot(df_filtre["prix_de_vente"], bins=30, kde=True, ax=ax)
    ax.set_title("Distribution des prix")
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots()
    sns.scatterplot(
        data=df_filtre,
        x="surface_m2",
        y="prix_de_vente",
        hue="type",
        alpha=0.6,
        ax=ax
    )
    st.pyplot(fig)

with tab3:
    fig, ax = plt.subplots(figsize=(8,4))
    sns.barplot(
        data=df_filtre,
        x="ville",
        y="prix_m2",
        estimator=np.median,
        errorbar=None,
        ax=ax
    )
    plt.xticks(rotation=45)
    st.pyplot(fig)

with tab4:
    fig, ax = plt.subplots()
    sns.heatmap(
        df_filtre[["prix_de_vente","prix_m2","surface_m2","pieces"]].corr(),
        annot=True,
        cmap="coolwarm",
        ax=ax
    )
    st.pyplot(fig)

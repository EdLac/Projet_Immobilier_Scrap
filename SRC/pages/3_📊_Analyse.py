# 3_📊_Analyse.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import pydeck as pdk
from matplotlib.colors import LinearSegmentedColormap
from theme import load_css, load_matplotlib_theme, COLORS

# ------------------------------------------------------------
# PAGE CONFIG (COMME AVANT)
# ------------------------------------------------------------
st.set_page_config(page_title="Analyse Immobilier", layout="wide")

# THEME (APRES set_page_config)
load_css()
load_matplotlib_theme()

st.title("📊 Analyse du marché immobilier")

# ------------------------------------------------------------
# LOAD DATA (INCHANGÉ)
# ------------------------------------------------------------
@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "..", "DATA", "ANNONCES_CLEAN.CSV")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df

df = load_data()

# ------------------------------------------------------------
# HELPERS (STATE) — INCHANGÉ
# ------------------------------------------------------------
def init_state(_df: pd.DataFrame):
    villes_all = sorted(_df["ville"].dropna().unique().tolist())
    pieces_all = sorted(_df["pieces"].dropna().unique().tolist())
    types_all = sorted(_df["type"].dropna().unique().tolist())
    dpe_all = sorted(_df["dpe"].dropna().unique().tolist())

    min_s = int(_df["surface_m2"].min())
    max_s = int(_df["surface_m2"].max())
    min_p = int(_df["prix_de_vente"].min())
    max_p = int(_df["prix_de_vente"].max())

    st.session_state["villes"] = villes_all
    st.session_state["surface"] = (min_s, max_s)
    st.session_state["prix"] = (min_p, max_p)
    st.session_state["pieces"] = pieces_all
    st.session_state["types"] = types_all
    st.session_state["dpe"] = dpe_all

    st.session_state["garage"] = False
    st.session_state["balcon"] = False
    st.session_state["ascenseur"] = False

    st.session_state["_reset_filters"] = False
    st.session_state["_inited"] = True


def request_reset():
    st.session_state["_reset_filters"] = True


# ------------------------------------------------------------
# RESET / INIT LOGIC — INCHANGÉ
# ------------------------------------------------------------
if "_inited" not in st.session_state:
    st.session_state["_inited"] = False
if "_reset_filters" not in st.session_state:
    st.session_state["_reset_filters"] = False

if (not st.session_state["_inited"]) or st.session_state["_reset_filters"]:
    init_state(df)

min_s, max_s = int(df["surface_m2"].min()), int(df["surface_m2"].max())
min_p, max_p = int(df["prix_de_vente"].min()), int(df["prix_de_vente"].max())

# ------------------------------------------------------------
# SIDEBAR — INCHANGÉ
# ------------------------------------------------------------
st.sidebar.header("Filtres")
st.sidebar.button("🔄 Réinitialiser les filtres", on_click=request_reset)

villes = st.sidebar.multiselect(
    "Ville",
    options=sorted(df["ville"].dropna().unique()),
    key="villes",
)

surface_range = st.sidebar.slider(
    "Surface (m²)",
    min_value=min_s,
    max_value=max_s,
    value=(min_s, max_s),   # 👈 OBLIGATOIRE
    key="surface",
)

prix_range = st.sidebar.slider(
    "Prix (€)",
    min_value=min_p,
    max_value=max_p,
    value=(min_p, max_p),   # 👈 OBLIGATOIRE
    key="prix",
)

surface_min, surface_max = surface_range
prix_min, prix_max = prix_range

pieces = st.sidebar.multiselect(
    "Nombre de pièces",
    options=sorted(df["pieces"].dropna().unique()),
    key="pieces",
)

types_bien = st.sidebar.multiselect(
    "Type de bien",
    options=sorted(df["type"].dropna().unique()),
    key="types",
)

dpe_selected = st.sidebar.multiselect(
    "DPE",
    options=sorted(df["dpe"].dropna().unique()),
    key="dpe",
)

garage_filter = st.sidebar.checkbox("Avec garage", key="garage")
balcon_filter = st.sidebar.checkbox("Avec balcon", key="balcon")
ascenseur_filter = st.sidebar.checkbox("Avec ascenseur", key="ascenseur")

# ------------------------------------------------------------
# APPLY FILTERS — INCHANGÉ
# ------------------------------------------------------------
df_filtre = df.copy()

if villes:
    df_filtre = df_filtre[df_filtre["ville"].isin(villes)]

df_filtre = df_filtre[
    df_filtre["surface_m2"].between(surface_min, surface_max)
    & df_filtre["prix_de_vente"].between(prix_min, prix_max)
]

if pieces:
    df_filtre = df_filtre[df_filtre["pieces"].isin(pieces)]
if types_bien:
    df_filtre = df_filtre[df_filtre["type"].isin(types_bien)]
if dpe_selected:
    df_filtre = df_filtre[df_filtre["dpe"].isin(dpe_selected)]
if garage_filter:
    df_filtre = df_filtre[df_filtre["garage"].fillna(0) > 0]
if balcon_filter:
    df_filtre = df_filtre[df_filtre["balcon"].fillna(0) > 0]
if ascenseur_filter:
    df_filtre = df_filtre[df_filtre["ascenseur"].fillna(0) > 0]

# ------------------------------------------------------------
# TABS — INCHANGÉ
# ------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Vue d’ensemble",
    "📐 Prix & Surfaces",
    "🏙️ Localisation",
    "🏠 Caractéristiques",
    "⚡ DPE",
    "🔗 Corrélations"
])

# ------------------------------------------------------------
# TAB 1 — DISTRIBUTIONS (NÉON)
# ------------------------------------------------------------
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        sns.histplot(
            df_filtre["prix_de_vente"],
            bins=30,
            kde=True,
            color=COLORS["prix"],
            ax=ax
        )
        ax.set_title("Distribution des prix de vente")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col2:
        fig, ax = plt.subplots()
        sns.histplot(
            df_filtre["surface_m2"],
            bins=30,
            kde=True,
            color=COLORS["surface"],
            ax=ax
        )
        ax.set_title("Distribution des surfaces")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.subheader("Carte de chaleur par grandes villes")
    df_map = df_filtre.dropna(subset=["latitude", "longitude", "prix_m2"])

    layer = pdk.Layer(
        "HeatmapLayer",
        data=df_map,
        get_position='[longitude, latitude]',
        radiusPixels=70,
    )

    view_state = pdk.ViewState(
        latitude=float(df_map["latitude"].median()),
        longitude=float(df_map["longitude"].median()),
        zoom=4.5
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# ------------------------------------------------------------
# TAB 2 — PRIX VS SURFACE (NÉON)
# ------------------------------------------------------------
with tab2:
    fig, ax = plt.subplots(figsize=(8, 3))
    sns.scatterplot(
        data=df_filtre,
        x="surface_m2",
        y="prix_de_vente",
        hue="type",
        palette="bright",
        alpha=0.6,
        s=25,
        ax=ax
    )
    ax.legend(
    title="Type",
    fontsize=9,        
    title_fontsize=10, 
    markerscale=0.8,   
    frameon=True
    )
    sns.regplot(
        data=df_filtre,
        x="surface_m2",
        y="prix_de_vente",
        scatter=False,
        color="#ffd166",
        ax=ax
    )
    ax.set_xlabel("Surface (m²)")
    ax.set_ylabel("Prix (€)")
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ------------------------------------------------------------
# TAB 3 — VILLES (NÉON)
# ------------------------------------------------------------
with tab3:
    order = df_filtre.groupby("ville")["prix_m2"].median().sort_values().index
    fig, ax = plt.subplots(figsize=(8, 3))
    sns.barplot(
        data=df_filtre,
        x="ville",
        y="prix_m2",
        order=order,
        estimator=np.median,
        palette="rocket",
        ax=ax
    )
    plt.xticks(rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Prix médian au m² (€)", fontsize=9)
    ax.tick_params(axis="y", labelsize=9)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ------------------------------------------------------------
# TAB 4 — CARACTÉRISTIQUES (NÉON)
# ------------------------------------------------------------
with tab4:
    fig, ax = plt.subplots(figsize=(7, 3))

    sns.boxplot(
        data=df_filtre,
        x="type",
        y="prix_m2",
        palette="cool",
        flierprops=dict(
            marker='o',
            markersize=4,          # 👈 plus petit
            markerfacecolor='#00e5ff',  # 👈 couleur néon visible
            markeredgecolor='none',
            alpha=0.6              # 👈 léger
        ),
        ax=ax
    )

    ax.tick_params(axis="y", labelsize=9)
    ax.tick_params(axis="x", labelsize=9)
    ax.set_title("Type de bien", fontsize=11)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ------------------------------------------------------------
# TAB 5 — DPE (NÉON)
# ------------------------------------------------------------
with tab5:
    fig, ax = plt.subplots(figsize=(7, 4))

    sns.boxplot(
        data=df_filtre,
        x="dpe",
        y="prix_m2",
        order=["A", "B", "C", "D", "E", "F", "G"],
        palette="viridis",
        flierprops=dict(
            marker='o',
            markersize=4,             # 👈 plus petit
            markerfacecolor='#ffd166', # 👈 néon jaune (lisible sur viridis)
            markeredgecolor='none',
            alpha=0.6
        ),
        ax=ax
    )

    # Texte plus petit (optionnel mais conseillé)
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)
    ax.set_xlabel("Classe DPE", fontsize=10)
    ax.set_ylabel("Prix au m² (€)", fontsize=10)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ------------------------------------------------------------
# TAB 6 — CORRÉLATIONS (NÉON)
# ------------------------------------------------------------
with tab6:
    vars_corr = ["prix_de_vente", "prix_m2", "surface_m2", "pieces", "chambres"]
    df_corr = df_filtre[vars_corr].dropna()

    # 🎨 COLORMAP NÉON BLEU → VIOLET
    neon_cmap = LinearSegmentedColormap.from_list(
        "neon_blue_purple",
        ["#020617", "#1e3a8a", "#3b82f6", "#a855f7", "#f0abfc"]
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.heatmap(
        df_corr.corr(),
        annot=True,
        fmt=".2f",
        cmap=neon_cmap,     # 👈 ICI la vraie différence
        center=0,
        linewidths=0.6,
        linecolor="#020617",
        annot_kws={"size": 9, "color": "white"},
        cbar_kws={"shrink": 0.8},
        ax=ax
    )

    ax.set_title("Matrice de corrélation", fontsize=12)
    ax.tick_params(axis="x", labelsize=9)
    ax.tick_params(axis="y", labelsize=9)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)






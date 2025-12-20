# 3_📊_Analyse.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import pydeck as pdk


# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="Analyse Immobilier", layout="wide")
st.title("📊 Analyse du marché immobilier")

# ------------------------------------------------------------
# LOAD DATA
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
# HELPERS (state)
# ------------------------------------------------------------
def init_state(_df: pd.DataFrame):
    """Initialize ALL widget keys with safe defaults (range sliders as tuples)."""
    villes_all = sorted(_df["ville"].dropna().unique().tolist())
    pieces_all = sorted(_df["pieces"].dropna().unique().tolist())
    types_all = sorted(_df["type"].dropna().unique().tolist())
    dpe_all = sorted(_df["dpe"].dropna().unique().tolist())

    min_s = int(_df["surface_m2"].min())
    max_s = int(_df["surface_m2"].max())
    min_p = int(_df["prix_de_vente"].min())
    max_p = int(_df["prix_de_vente"].max())

    st.session_state["villes"] = villes_all
    st.session_state["surface"] = (min_s, max_s)   # ✅ RANGE SLIDER
    st.session_state["prix"] = (min_p, max_p)      # ✅ RANGE SLIDER
    st.session_state["pieces"] = pieces_all
    st.session_state["types"] = types_all
    st.session_state["dpe"] = dpe_all

    st.session_state["garage"] = False
    st.session_state["balcon"] = False
    st.session_state["ascenseur"] = False

    st.session_state["_reset_filters"] = False
    st.session_state["_inited"] = True


def request_reset():
    # ✅ Do NOT touch widget keys here. Just request a reset.
    st.session_state["_reset_filters"] = True


# ------------------------------------------------------------
# RESET / INIT LOGIC
# ------------------------------------------------------------
# First run: ensure internal flags exist
if "_inited" not in st.session_state:
    st.session_state["_inited"] = False
if "_reset_filters" not in st.session_state:
    st.session_state["_reset_filters"] = False

# If asked to reset OR first init -> set defaults BEFORE widgets are created
if (not st.session_state["_inited"]) or st.session_state["_reset_filters"]:
    init_state(df)

# Extra safety: if old state has wrong types, coerce BEFORE widgets
min_s, max_s = int(df["surface_m2"].min()), int(df["surface_m2"].max())
min_p, max_p = int(df["prix_de_vente"].min()), int(df["prix_de_vente"].max())

surf_state = st.session_state.get("surface")
if not (isinstance(surf_state, (tuple, list)) and len(surf_state) == 2):
    st.session_state["surface"] = (min_s, max_s)

prix_state = st.session_state.get("prix")
if not (isinstance(prix_state, (tuple, list)) and len(prix_state) == 2):
    st.session_state["prix"] = (min_p, max_p)

for k in ["villes", "pieces", "types", "dpe"]:
    if not isinstance(st.session_state.get(k), list):
        st.session_state[k] = list(st.session_state.get(k, []))

for k in ["garage", "balcon", "ascenseur"]:
    if not isinstance(st.session_state.get(k), bool):
        st.session_state[k] = False

# ------------------------------------------------------------
# SIDEBAR WIDGETS
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
    key="surface",
)

prix_range = st.sidebar.slider(
    "Prix (€)",
    min_value=min_p,
    max_value=max_p,
    key="prix",
)

# if Streamlit still returns a scalar (old state), handle it
if isinstance(surface_range, (tuple, list)) and len(surface_range) == 2:
    surface_min, surface_max = surface_range
else:
    surface_min, surface_max = min_s, max_s

if isinstance(prix_range, (tuple, list)) and len(prix_range) == 2:
    prix_min, prix_max = prix_range
else:
    prix_min, prix_max = min_p, max_p

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
# APPLY FILTERS (empty selection = no filter)
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
# KPIs
# ------------------------------------------------------------
st.subheader("📌 Indicateurs clés par type de bien")

types_for_kpi = types_bien if types_bien else sorted(df_filtre["type"].dropna().unique())

for t in types_for_kpi:
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

        pct_balcon = (df_type["balcon"].fillna(0) > 0).mean() * 100
        pct_garage = (df_type["garage"].fillna(0) > 0).mean() * 100

        col3.metric("Avec balcon", f"{pct_balcon:.0f} %")
        col4.metric("Avec garage", f"{pct_garage:.0f} %")

# ------------------------------------------------------------
# TABS
# ------------------------------------------------------------
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
        st.pyplot(fig, use_container_width=True)

    with col2:
        fig, ax = plt.subplots()
        sns.histplot(df_filtre["surface_m2"], bins=30, kde=True, ax=ax)
        ax.set_title("Distribution des surfaces")
        st.pyplot(fig, use_container_width=True)

    df_map = df_filtre.dropna(subset=["latitude", "longitude", "prix_m2"]).copy()

    layer = pdk.Layer(
        "HeatmapLayer",
        data=df_map,
        get_position='[longitude, latitude]',
        get_weight=1, # ou 1 pour densité pure
        radiusPixels=70, # ajuste (40-100)
        )

    view_state = pdk.ViewState(
        latitude=float(df_map["latitude"].median()),
        longitude=float(df_map["longitude"].median()),
        zoom=10
    )

    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

with tab2:
    st.subheader("Relation entre surface et prix")
    fig, ax = plt.subplots(figsize=(7, 5))
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
    st.pyplot(fig, use_container_width=True)

with tab3:
    st.subheader("Prix médian au m² par ville")
    if df_filtre.empty:
        st.info("Aucune donnée après filtres.")
    else:
        order = df_filtre.groupby("ville")["prix_m2"].median().sort_values().index
        fig, ax = plt.subplots(figsize=(8, 4))
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
        st.pyplot(fig, use_container_width=True)

with tab4:
    st.subheader("Impact des caractéristiques sur le prix au m²")

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=df_filtre, x="type", y="prix_m2", ax=ax)
        ax.set_title("Type de bien")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with r1c2:
        fig, ax = plt.subplots(figsize=(6, 4))
        x_vals = df_filtre["balcon"].fillna(0).astype(int).clip(0, 1).map({0:"Non", 1:"Oui"})
        sns.boxplot(data=df_filtre, x=x_vals, y="prix_m2", ax=ax)
        ax.set_title("Balcon")
        ax.set_xlabel("")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        fig, ax = plt.subplots(figsize=(6, 4))
        x_vals = df_filtre["garage"].fillna(0).astype(int).clip(0, 1).map({0:"Non", 1:"Oui"})
        sns.boxplot(data=df_filtre, x=x_vals, y="prix_m2", ax=ax)
        ax.set_title("Garage")
        ax.set_xlabel("")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with r2c2:
        fig, ax = plt.subplots(figsize=(6, 4))
        x_vals = df_filtre["ascenseur"].fillna(0).astype(int).clip(0, 1).map({0:"Non", 1:"Oui"})
        sns.boxplot(data=df_filtre, x=x_vals, y="prix_m2", ax=ax)
        ax.set_title("Ascenseur")
        ax.set_xlabel("")
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)


with tab5:
    st.subheader("Impact du DPE sur le prix au m²")
    fig, ax = plt.subplots()
    sns.boxplot(
        data=df_filtre,
        x="dpe",
        y="prix_m2",
        order=["A", "B", "C", "D", "E", "F", "G"],
        ax=ax
    )
    ax.set_xlabel("Classe DPE")
    ax.set_ylabel("Prix au m² (€)")
    st.pyplot(fig, use_container_width=True)

with tab6:
    st.subheader("Matrice de corrélation")
    vars_corr = ["prix_de_vente", "prix_m2", "surface_m2", "pieces", "chambres"]
    df_corr = df_filtre[vars_corr].dropna()

    if df_corr.empty:
        st.info("Pas assez de données pour calculer la corrélation.")
    else:
        fig, ax = plt.subplots(figsize=(6, 5))
        sns.heatmap(
            df_corr.corr(),
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            ax=ax
        )
        st.pyplot(fig, use_container_width=True)

    st.subheader("🧠 Insights clés")
    st.markdown("""
    - 📈 Forte corrélation entre surface et prix de vente
    - 🏙️ Prix au m² plus élevés pour les appartements
    - 🚗 Les options valorisent significativement le bien
    - ⚡ Le DPE influence positivement la valorisation
    """)


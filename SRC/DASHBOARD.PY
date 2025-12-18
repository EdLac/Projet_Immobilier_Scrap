import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Configuration de la page 
st.set_page_config(page_title="Dashboard Immobilier", layout="wide")  # utiliser toute la largeur de l'écran

# Style professionnel
st.markdown(
    """
    <style>
    /* Fond général */
    .stApp {
        background-color: #0E1117;
        color: #E6EDF3;
    }

    /* Titres */
    h1, h2, h3, h4 {
        color: #E6EDF3;
    }

    /* Texte secondaire */
    p, span, label {
        color: #E6EDF3;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161B22;
    }

    /* Boutons */
    button {
        background-color: #4F8BF9 !important;
        color: white !important;
        border-radius: 8px;
    }

    /* Sliders */
    .stSlider > div > div {
        color: #4F8BF9;
    }

    </style>
    """,
    unsafe_allow_html=True
)

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

#Definition des valeurs par defaut pour Reset Filter
if "init" not in st.session_state:
    st.session_state["villes"] = sorted(df["ville"].unique())
    st.session_state["surface"] = (
        int(df["surface_m2"].min()),
        int(df["surface_m2"].max())
    )
    st.session_state["prix"] = (
        int(df["prix_de_vente"].min()),
        int(df["prix_de_vente"].max())
    )
    st.session_state["pieces"] = sorted(df["pieces"].dropna().unique())
    st.session_state["types"] = sorted(df["type"].dropna().unique())
    st.session_state["dpe"] = sorted(df["dpe"].dropna().unique())
    st.session_state["garage"] = False
    st.session_state["balcon"] = False
    st.session_state["ascenseur"] = False
    st.session_state["init"] = True


nb_annonces = len(df)
nb_villes = df["ville"].nunique()
prix_median = int(df["prix_de_vente"].median())
surface_mediane = int(df["surface_m2"].median())
periode = "Non précisée"

# Bloc Problematique
st.markdown(
    """
    <style>
    .problem-card {
        background: linear-gradient(135deg, #0F3D91, #0B2A5B);
        padding: 26px;
        border-radius: 16px;
        border-left: 6px solid #60A5FA;
        box-shadow: 0 10px 30px rgba(0,0,0,0.45);
        margin-bottom: 32px;
    }

    .problem-card h3 {
        color: #FFFFFF;
        margin-top: 0;
        font-weight: 600;
    }

    .problem-card p {
        color: #E5EDFF;
        font-size: 15px;
        line-height: 1.7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Bloc resume data
st.markdown(
    """
    <style>
    .data-summary {
        background-color: #161B22;
        padding: 20px 24px;
        border-radius: 14px;
        border: 1px solid #1F2937;
        margin-bottom: 32px;
    }

    .data-summary h4 {
        color: #E6EDF3;
        margin-top: 0;
        margin-bottom: 16px;
    }

    .data-summary p {
        color: #9BA3AF;
        font-size: 14px;
        margin: 4px 0;
    }

    .data-summary strong {
        color: #E6EDF3;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#Hero Header
st.markdown(
    """
    <div style="
        margin-bottom: 24px;
    ">
        <h1 style="margin-bottom: 4px;">🏠 Dashboard Immobilier Interactif</h1>
        <p style="font-size:16px; color:#9BA3AF;">
            Cette application interactive vise à explorer les relations entre les caractéristiques des biens immobiliers et leurs prix de vente, à travers une analyse exploratoire des données.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

#Problematique et explication de l'etude
st.markdown(
"""
<div class="problem-card">
<h3>🎯 Problématique</h3>

<p>
Comment les caractéristiques d’un bien immobilier
(surface, localisation, nombre de pièces, options, DPE)
influencent-elles le prix de vente et le prix au m² ?
</p>

<div style="margin-top:16px;">
<h4 style="margin-bottom:6px;">📍 Périmètre de l’étude</h4>

<p style="color:#E5EDFF; font-size:14px; line-height:1.6;">
Dans le cadre de cette analyse, nous avons choisi de nous concentrer sur les
<strong>18 principales villes françaises</strong>.
Ce choix méthodologique permet de réduire la complexité de l’étude tout en
conservant un niveau de représentativité élevé du marché immobilier français.
</p>

<p style="color:#E5EDFF; font-size:14px; line-height:1.6;">
Les grandes villes concentrent un volume important de transactions,
une forte diversité de biens et des dynamiques de prix plus stables et comparables.
À l’inverse, l’intégration de l’ensemble du territoire, notamment des petites villes
et zones rurales, aurait introduit une forte hétérogénéité des marchés,
rendant l’analyse plus complexe et moins lisible dans le cadre de ce projet.
</p>
</div>
</div>
""",
unsafe_allow_html=True
)

#Resume dataframe
with st.container():
    st.markdown(
        f"""
        <div class="data-summary">
            <h4>📊 Résumé du jeu de données</h4>
            <p><strong>Nombre d’annonces :</strong> {nb_annonces}</p>
            <p><strong>Nombre de villes couvertes :</strong> {nb_villes}</p>
            <p><strong>Prix médian :</strong> {prix_median:,} €</p>
            <p><strong>Surface médiane :</strong> {surface_mediane} m²</p>
            <p><strong>Source :</strong> ParuVendu.fr (scraping)</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Filtres dans la sidebar
st.sidebar.header("Filtres")

villes = st.sidebar.multiselect(
    "Ville",
    options=sorted(df["ville"].unique()),
    key="villes"
)

surface_min, surface_max = st.sidebar.slider(
    "Surface (m²)",
    int(df["surface_m2"].min()),
    int(df["surface_m2"].max()),
    key="surface"
)

prix_min, prix_max = st.sidebar.slider(
    "Prix (€)",
    int(df["prix_de_vente"].min()),
    int(df["prix_de_vente"].max()),
    key="prix"
)

pieces = st.sidebar.multiselect(
    "Nombre de pièces",
    options=sorted(df["pieces"].dropna().unique()),
    key="pieces"
)

types_bien = st.sidebar.multiselect(
    "Type de bien",
    options=sorted(df["type"].dropna().unique()),
    key="types"
)

dpe_selected = st.sidebar.multiselect(
    "DPE",
    options=sorted(df["dpe"].dropna().unique()),
    key="dpe"
)

garage_filter = st.sidebar.checkbox("Avec garage", key="garage")
balcon_filter = st.sidebar.checkbox("Avec balcon", key="balcon")
ascenseur_filter = st.sidebar.checkbox("Avec ascenseur", key="ascenseur")

if st.sidebar.button("🔄 Réinitialiser les filtres"):
    st.session_state.clear()
    st.rerun()

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


# KPIs par type de bien (appartement VS maison)
st.subheader("📌 KPIs principaux par type de bien")

for t in types_bien:
    df_type = df_filtre[df_filtre["type"] == t]

    if df_type.empty:
        continue

    with st.expander(f"{t}", expanded=True):

        # --- Ligne 1 : KPIs marché ---
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Annonces", f"{len(df_type):,}")
        col2.metric("Prix médian", f"{int(df_type['prix_de_vente'].median()):,} €")
        col3.metric("Prix médian €/m²", f"{int(df_type['prix_m2'].median()):,} €")
        col4.metric("Surface médiane", f"{int(df_type['surface_m2'].median())} m²")

        # --- Ligne 2 : Profil du bien ---
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Pièces moyennes", f"{df_type['pieces'].mean():.1f}")
        col2.metric("Chambres moyennes", f"{df_type['chambres'].mean():.1f}")

        pct_balcon = (df_type["balcon"] > 0).mean() * 100
        pct_garage = (df_type["garage"] > 0).mean() * 100

        col3.metric("Avec balcon", f"{pct_balcon:.0f} %")
        col4.metric("Avec garage", f"{pct_garage:.0f} %")



# ---Graphiques Analyse des prix et surfaces---

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

    order = (
        df_filtre.groupby("ville")["prix_m2"]
        .median()
        .sort_values()
        .index
    )

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

    vars_corr = [
        "prix_de_vente",
        "prix_m2",
        "surface_m2",
        "pieces",
        "chambres"
    ]

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

import streamlit as st
import pandas as pd
import os

# Configuration de la page

st.set_page_config(page_title="Dashboard Immobilier", layout="wide")

# Style professionnel
st.markdown(
    """
    <style>
    /* Fond général */
    .stApp { background-color: #0E1117; color: #E6EDF3; }

    /* Titres et textes */
    h1, h2, h3, h4, p, span, label { color: #E6EDF3; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background-color: #161B22; }

    /* Boutons */
    button { background-color: #4F8BF9 !important; color: white !important; border-radius: 8px; }

    /* Sliders */
    .stSlider > div > div { color: #4F8BF9; }

    /* Encadrés */
    .problem-card { background: linear-gradient(135deg, #0F3D91, #0B2A5B); padding: 26px; border-radius: 16px; border-left: 6px solid #60A5FA; box-shadow: 0 10px 30px rgba(0,0,0,0.45); margin-bottom: 32px; }
    .problem-card h3 { color: #FFFFFF; margin-top: 0; font-weight: 600; }
    .problem-card p { color: #E5EDFF; font-size: 15px; line-height: 1.7; }
    </style>
    """,
    unsafe_allow_html=True
)

# Chargement des données

@st.cache_data
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "..", "..", "DATA", "ANNONCES_CLEAN.CSV")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
    return df

df = load_data()


# Hero Header

st.markdown(
    """
    <div style="margin-bottom:24px;">
        <h1 style="margin-bottom:4px;">🏠 Dashboard Immobilier Interactif</h1>
        <p style="font-size:16px; color:#9BA3AF;">
            Cette application interactive vise à explorer les relations entre les caractéristiques des biens immobiliers et leurs prix de vente, à travers une analyse exploratoire des données.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Problématique

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


# Résumé du jeu de données

st.markdown("### 📊 Résumé du jeu de données")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Annonces", f"{len(df):,}")
col2.metric("Villes", df["ville"].nunique())
col3.metric("Prix médian", f"{int(df['prix_de_vente'].median()):,} €")
col4.metric("Surface médiane", f"{int(df['surface_m2'].median())} m²")

st.markdown("""
**Source des données** : ParuVendu.fr  
**Méthode** : Web scraping, nettoyage et analyse exploratoire
""")

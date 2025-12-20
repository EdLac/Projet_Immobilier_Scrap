import streamlit as st
import pandas as pd
import os
from theme import load_css, load_matplotlib_theme

# ------------------------------------------------------------
# THEME GLOBAL
# ------------------------------------------------------------
load_css()
load_matplotlib_theme()

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
# HERO HEADER
# ------------------------------------------------------------
st.markdown(
    """<div style="margin-bottom:32px;">
        <h1 style="margin-bottom:6px;">🏠 Dashboard Immobilier Interactif</h1>
        <p style="font-size:16px; color:#94a3b8;">
            Cette application interactive vise à explorer les relations entre les
            caractéristiques des biens immobiliers et leurs prix de vente,
            à travers une analyse exploratoire des données.
        </p>
    </div>""",
    unsafe_allow_html=True
)

# ------------------------------------------------------------
# PROBLÉMATIQUE — CARTE NÉON (PLEINE LARGEUR)
# ------------------------------------------------------------
st.markdown("""
<div class="problem-card">
<h3>🎯 Problématique</h3>

<p>
Comment les caractéristiques d’un bien immobilier
(<strong>surface</strong>, <strong>localisation</strong>,
<strong>nombre de pièces</strong>, <strong>options</strong>,
<strong>DPE</strong>)
influencent-elles le <strong>prix de vente</strong>
et le <strong>prix au m²</strong> ?
</p>

<h3 style="margin-top:16px;">📍 Périmètre de l’étude</h3>

<p>
Dans le cadre de cette analyse, nous avons choisi de nous concentrer sur les
<strong>18 principales villes françaises</strong>.
</p>

<p>
Les grandes villes concentrent un volume important de transactions,
une forte diversité de biens et des dynamiques de prix plus stables et comparables.
</p>
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# DATASET SUMMARY
# ------------------------------------------------------------
st.markdown("### 📊 Résumé du jeu de données")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Annonces", f"{len(df):,}")
col2.metric("Villes", df["ville"].nunique())
col3.metric("Variables", df.shape[1])
col4.metric("Prix m² médian", f"{df['prix_m2'].median():,.0f} €")

st.markdown(
"""
**Source des données** : [ParuVendu.fr](https://www.paruvendu.fr/immobilier/)  
**Méthode** : Web scraping, nettoyage et analyse exploratoire
"""
)

with st.expander("📂 Voir la base de données"):
    st.dataframe(df)

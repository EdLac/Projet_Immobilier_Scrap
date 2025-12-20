import streamlit as st
from theme import load_css, load_matplotlib_theme

st.set_page_config(
    page_title="Dashboard Immobilier",
    layout="wide"
)

load_css()
load_matplotlib_theme()

st.title("🏠 Dashboard Immobilier")

st.markdown(
    """
    Utilisez le menu de gauche pour naviguer :
    - 🏠 Accueil
    - 🧪 Méthodologie
    - 📊 Analyse
    """
)


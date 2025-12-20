import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

# =========================
# 🎨 STREAMLIT CSS GLOBAL
# =========================
def load_css():
    st.markdown(
        """
        <style>
        /* ---------- GLOBAL ---------- */
        .stApp {
            background: radial-gradient(circle at top, #0b1220, #050812);
            color: #e5e7eb;
        }

        h1, h2, h3, h4 {
            color: white;
            font-weight: 700;
        }

        section[data-testid="stSidebar"] {
            background-color: #0f172a;
        }

        /* ---------- METRICS ---------- */
        div[data-testid="metric-container"] {
            background-color: #0f172a;
            border-radius: 14px;
            padding: 16px;
            box-shadow: 0 0 25px rgba(0,255,200,0.05);
        }

        /* ---------- PROBLEM CARD (SAFE & WORKING) ---------- */
        .problem-card {
            background: linear-gradient(135deg, #0f3d91, #0b2a5b);
            padding: 26px;
            border-radius: 16px;
            border-left: 6px solid #60a5fa;
            box-shadow: 0 10px 30px rgba(0,0,0,0.45);
            margin: 32px 0;
            width: 100%;
        }

        .problem-card h3 {
            color: #ffffff;
            margin-top: 0;
            font-weight: 600;
        }

        .problem-card p {
            color: #e5edff;
            font-size: 15px;
            line-height: 1.7;
            margin-bottom: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================
# 📊 MATPLOTLIB / SEABORN
# =========================
_THEME_LOADED = False

def load_matplotlib_theme():
    global _THEME_LOADED
    if _THEME_LOADED:
        return

    sns.set_theme(style="darkgrid", context="talk")

    plt.rcParams.update({
        "figure.facecolor": "#0b1220",
        "axes.facecolor": "#0b1220",
        "axes.edgecolor": "#0b1220",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "text.color": "white",
        "grid.color": "white",
        "grid.alpha": 0.08,
        "axes.titleweight": "bold",
        "axes.titlesize": 16,
        "axes.labelsize": 12,
    })

    _THEME_LOADED = True


# =========================
# 🌈 PALETTE FLUO
# =========================
COLORS = {
    "prix": "#ff4d4d",
    "surface": "#00e5ff",
    "revenus": "#00ff9c",
    "inflation": "#ffd166",
    "neutral": "#cbd5f5"
}


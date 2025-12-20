# =====================================
# ANALYSE.PY
# Calculs statistiques et graphiques
# =====================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib

# ⚠️ utile sur macOS si problème d’affichage
matplotlib.use("TkAgg")

# =====================================
# CHARGEMENT DES DONNÉES
# =====================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "..", "DATA", "ANNONCES_CLEAN.csv")

df = pd.read_csv(csv_path)

print("Dataset chargé :", df.shape)
print(df.head())

# =====================================
# CALCULS STATISTIQUES GLOBAUX
# =====================================

print("\n--- INDICATEURS GLOBAUX ---")
print("Nombre d'annonces :", len(df))
print("Nombre de villes :", df["Ville"].nunique())
print("Prix médian :", int(df["Prix_de_vente"].median()), "€")
print("Prix au m² médian :", int(df["Prix_m2"].median()), "€")
print("Surface médiane :", int(df["Surface_m2"].median()), "m²")

# =====================================
# DISTRIBUTION DES PRIX
# =====================================

plt.figure(figsize=(8, 5))
sns.histplot(df["Prix_de_vente"], bins=30, kde=True)
plt.title("Distribution des prix de vente")
plt.xlabel("Prix (€)")
plt.ylabel("Nombre d'annonces")
plt.tight_layout()
plt.show()

# =====================================
# DISTRIBUTION DES SURFACES
# =====================================

plt.figure(figsize=(8, 5))
sns.histplot(df["Surface_m2"], bins=30, kde=True)
plt.title("Distribution des surfaces")
plt.xlabel("Surface (m²)")
plt.ylabel("Nombre d'annonces")
plt.tight_layout()
plt.show()

# =====================================
# RELATION SURFACE / PRIX
# =====================================

plt.figure(figsize=(7, 5))
sns.scatterplot(
    data=df,
    x="Surface_m2",
    y="Prix_de_vente",
    hue="Type",
    alpha=0.6
)
sns.regplot(
    data=df,
    x="Surface_m2",
    y="Prix_de_vente",
    scatter=False,
    color="black"
)
plt.title("Relation entre surface et prix de vente")
plt.xlabel("Surface (m²)")
plt.ylabel("Prix (€)")
plt.tight_layout()
plt.show()

# =====================================
# PRIX AU M² PAR TYPE DE BIEN
# =====================================

plt.figure(figsize=(7, 5))
sns.boxplot(
    data=df,
    x="Type",
    y="Prix_m2"
)
plt.title("Prix au m² par type de bien")
plt.xlabel("Type de bien")
plt.ylabel("Prix au m² (€)")
plt.tight_layout()
plt.show()

# =====================================
# IMPACT DES CARACTÉRISTIQUES
# =====================================

for opt in ["Balcon", "Garage", "Ascenseur"]:
    plt.figure(figsize=(5, 4))
    sns.boxplot(
        data=df,
        x=df[opt].map({0: "Non", 1: "Oui"}),
        y="Prix_m2"
    )
    plt.title(f"Impact du {opt} sur le prix au m²")
    plt.xlabel("")
    plt.ylabel("Prix au m² (€)")
    plt.tight_layout()
    plt.show()

# =====================================
# PRIX MÉDIAN AU M² PAR VILLE
# =====================================

plt.figure(figsize=(10, 5))
order = (
    df.groupby("Ville")["Prix_m2"]
    .median()
    .sort_values()
    .index
)

sns.barplot(
    data=df,
    x="Ville",
    y="Prix_m2",
    order=order,
    estimator=np.median,
    errorbar=None
)
plt.xticks(rotation=45, ha="right")
plt.title("Prix médian au m² par ville")
plt.ylabel("Prix au m² (€)")
plt.tight_layout()
plt.show()

# =====================================
# MATRICE DE CORRÉLATION
# =====================================

vars_corr = ["Prix_de_vente", "Prix_m2", "Surface_m2", "Pieces", "Chambres"]

plt.figure(figsize=(6, 5))
sns.heatmap(
    df[vars_corr].corr(),
    annot=True,
    fmt=".2f",
    cmap="coolwarm"
)
plt.title("Matrice de corrélation")
plt.tight_layout()
plt.show()

print("\nAnalyse terminée.")

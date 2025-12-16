import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Créer le chemin relatif depuis le fichier Python
base_dir = os.path.dirname(os.path.abspath(__file__))  # dossier SRC
csv_path = os.path.join(base_dir, "..", "DATA", "ANNONCES_CLEAN.CSV")

# Charger le CSV
df = pd.read_csv(csv_path)
print(df.head())

#Graphique Prix m2 (median) par ville

plt.figure(figsize=(16,6))

order = (
    df.groupby("Ville")["Prix_m2"]
      .median()
      .sort_values(ascending=True)
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

plt.xticks(rotation=55, ha="right")
plt.title("Prix au m² médian par ville (ordre croissant)")
plt.show()

# Graphique Prix m2 vs surface

plt.figure(figsize=(16,6))

sns.scatterplot(
    data=df,
    x="Prix_m2",
    y="Surface_m2",
    alpha=0.5,
    hue="type"
    )

plt.title("Répartition du prix m2 par rapport à la surface")
plt.show()

# Distribution des Prix par ville (violin plot)

plt.figure(figsize=(16,6))
order = df.groupby("Ville")["Prix_m2"].median().sort_values().index

sns.violinplot(
    data=df,
    x = "Ville",
    y = "Prix_m2",
    order=order,
    cut=0
)

plt.xticks(rotation=55, ha="right")
plt.title("Distribution des Prix par ville (violin plot)")
plt.show()

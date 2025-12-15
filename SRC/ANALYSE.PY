import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

df = pd.read_csv("/Users/edouardlacroix/Desktop/DU Data Analytics/COURS/Python Avance/Projet/Projet_Immobilier/Projet_Immobilier_Scrap/DATA/ANNONCES_CLEAN.CSV")
print(df.head())

#Graphique Prix m2 (median) par ville

plt.figure(figsize=(16,6))
plt.xticks(rotation = 45, ha="right")
sns.boxplot(x = df["Ville"], y = df["Prix_m2"], data= df)
order = (
    df.groupby("Ville")["Prix_m2"].median().sort_values(ascending=True).index
)
plt.show()
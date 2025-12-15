import pandas as pd
import re
import os
import numpy as np
from geopy.geocoders import Nominatim
from time import sleep
import numpy as np

# Chargement du CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(BASE_DIR, "..", "DATA", "ANNONCES_RAW.csv")
clean_csv_file = os.path.join(BASE_DIR, "..", "DATA", "ANNONCES_CLEAN.csv")

print("Chemin CSV raw :", os.path.abspath(csv_file))
print("Fichier existe ?", os.path.exists(csv_file))

df = pd.read_csv(csv_file)

# Nettoyage Détails
df["Détails"] = df["Détails"].astype(str).str.replace("\n"," ").str.replace("\xa0"," ")
df["Description"] = df["Description"].astype(str)\
    .str.replace("\n"," ")\
    .str.replace("_", " ")\
    .str.replace(" -", " ")\
    .str.replace(r"\s+", " ", regex=True)

# Extraction détails
def parse_details(details_str):
    details_str = str(details_str)
    out = {
        "Pieces": None,
        "Chambres": None,
        "Garage": 0,
        "Balcon": 0,
        "Ascenseur": 0,
        "Terrain_m2": None,
        "DPE": None,
    }

    # Pièces
    pieces_match = re.search(r"(\d+)\s*pi[eè]ce", details_str, re.I)
    if pieces_match:
        out["Pieces"] = int(pieces_match.group(1))

    # Chambres
    chambres_match = re.search(r"(\d+)\s*chambre", details_str, re.I)
    if chambres_match:
        out["Chambres"] = int(chambres_match.group(1))

    # Garage / Balcon / Ascenseur
    for col in ["Garage", "Balcon", "Ascenseur"]:
        if col.lower() in details_str.lower():
            out[col] = 1

    # Terrain
    terrain_match = re.search(r"terrain\s*(\d+)", details_str, re.I)
    if terrain_match:
        out["Terrain_m2"] = float(terrain_match.group(1))

    # DPE
    dpe_match = re.search(r"DPE\s*:\s*([A-G])", details_str, re.I)
    if dpe_match:
        out["DPE"] = dpe_match.group(1).upper()

    return out

#Prix m2
df["Prix_m2"] = (
    df["Prix"]
    .str.extract(r"([\d\s\u202f\xa0]+)\s*€\s*/\s*m2")[0]
    .str.replace(r"[\s\u202f\xa0]", "", regex=True)
    .astype(float)
)

#Prix de vente
df["Prix"] = df["Prix"].str.replace(r"\*?\d[\d\s\u202f]+€ / m2", "", regex = True)
df["Prix"] = df["Prix"].str.strip().str.replace("€", "", regex=False).str.replace(" ", "", regex=False).str.replace("*", "", regex=False).replace("NC", np.nan).astype(float)
df = df.rename(columns={"Prix" : "Prix_de_vente"})

# Parsing
details_df = df["Détails"].apply(parse_details).apply(pd.Series)

# Surface depuis le titre
def extract_surface(title):
    if pd.isna(title):
        return None
    match = re.search(r"(\d+)\s*m²", title.replace("\xa0",""))
    return int(match.group(1)) if match else None

df["Surface_m2"] = df["Titre"].apply(extract_surface)

# Type de bien depuis le titre
df["type"] = df["Titre"].str.split("-").str[0].str.strip()
df["type"] = df["type"].str.replace("loft", "appartement", case=False)
df["type"] = df["type"].str.replace("villa", "maison", case=False)
df["type"] = df["type"].str.replace("Duplex/triplex", "appartement", case=False)

# CONCAT sans créer de doublons
df_final = pd.concat([df.drop(columns=["Détails"], errors="ignore"), details_df], axis=1)

cols_int = ["Pieces", "Chambres", "Garage", "Balcon", "Ascenseur"]
cols_float = ["Terrain_m2", "Surface_m2", "Prix_m2", "Prix_de_vente"]

for col in cols_int:
    if col in df_final.columns:
        df_final[col] = pd.to_numeric(df_final[col], errors="coerce").astype("Int64")

for col in cols_float:
    if col in df_final.columns:
        df_final[col] = pd.to_numeric(df_final[col], errors="coerce")

print(df_final["Pieces"].isna().sum())

# Liste des types à exclure
types_a_exclure = [
    "terrain", "hotel", "hôtel", "peniche", "péniche", "garage", "boutique",
    "commerce", "bureau", "immeuble", "chateau", "château", "grange",
    "hangar", "parking", "box","ferme","plateau", "Parking / Garage", "Hôtel Particulier"
]

# Filtrer les types indésirables
df_final = df_final[~df_final["type"].str.lower().isin([t.lower() for t in types_a_exclure])]

print("Début du géocodage des localisations...")

geolocator = Nominatim(user_agent="projet_immo_sorbonne", timeout=5)

def geocode_loc (loc) :
    if not isinstance(loc, str) or loc.strip() == "" :
       return None, None
    
    query = loc + ", France"

    for attempt in range(3):
        try:
            location = geolocator.geocode(query, timeout=5)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except Exception as e:
            print(f"Tentative {attempt+1}/3 échouée pour '{loc}' -> {e}")
            sleep(1)  # courte pause avant retry

    return None, None

geo_cache = {}
longitude = []
latitude = []

loc_series = df_final["Localisation"] if "Localisation" in df_final.columns else df["Localisation"]

for i, loc in enumerate(loc_series):
    loc_str = "" if pd.isna(loc) else str(loc).strip()

    if loc_str == "":
        latitude.append(None)
        longitude.append(None)
        continue

    if loc_str in geo_cache:
        lat, lon = geo_cache[loc_str]
    else:
        lat, lon = geocode_loc(loc_str)
        geo_cache[loc_str] = (lat, lon)
        #petit log
        print(f"{i+1}/{len(loc_series)} | {loc_str} -> {lat}, {lon}")
        sleep(1)  # respecter Nominatim

    latitude.append(lat)
    longitude.append(lon)

df_final["Latitude"] = latitude
df_final["Longitude"] = longitude

# Filtrer les outliers avec l'IQR
def remove_outliers_iqr(df_final, col):
    Q1 = df_final[col].quantile(0.25)
    Q3 = df_final[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df_final[(df_final[col] >= lower_bound) & (df_final[col] <= upper_bound)]

df_final = remove_outliers_iqr(df_final, "Prix_m2")
df_final = remove_outliers_iqr(df_final, "Prix_de_vente")

# Sauvegarde CSV propre 
df_final.to_csv(clean_csv_file, index=False, encoding="utf-8")
print("✅ ANNONCES_CLEAN.csv généré :", os.path.abspath(clean_csv_file))

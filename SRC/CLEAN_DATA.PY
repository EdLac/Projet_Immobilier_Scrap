import pandas as pd
import re
import os
from geopy.geocoders import Nominatim
from time import sleep

# Chargement du CSV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(BASE_DIR, "..", "DATA", "ANNONCES_RAW.csv")

print("Chemin utilisé :", os.path.abspath(csv_file))
print("Fichier existe ?", os.path.exists(csv_file))

df = pd.read_csv(csv_file)
# Nettoyage Détails
df["Détails"] = df["Détails"].astype(str).str.replace("\n"," ").str.replace("\xa0"," ")
df["Description"] = df["Description"].astype(str).str.replace("\n"," ").str.replace("_", " ").str.replace(" -", " ").str.replace(r"\s+", " ", regex=True)

# Fonction simple
def parse_details(details_str):
    details_str = str(details_str)

    out = {
        "Pieces": "Non communiqué",
        "Chambres": "Non communiqué",
        "Garage": "Non communiqué",
        "Balcon": "Non communiqué",
        "Ascenseur": "Non communiqué",
        "Terrain_m2": "Non communiqué",
        "DPE": "Non communiqué",
    }
    # Pièces
    pieces_match = re.search(r"(\d+)(?:/(\d+))?\s*pi[eè]ce(?:s|\(s\))?", details_str, re.I)
    if pieces_match:
        out["Pieces"] = pieces_match.group(1)

    # Chambres
    chambres_match = re.search(r"(\d+)\s*chambre", details_str, re.I)
    if chambres_match:
        out["Chambres"] = chambres_match.group(1)

    # Garage / Balcon / Ascenseur
    for col in ["Garage", "Balcon", "Ascenseur"]:
        if col.lower() in details_str.lower():
            out[col] = "Oui"
        else :
            out[col] = "Non communiqué"

    # Terrain
    terrain_match = re.search(r"terrain\s*(\d+)", details_str, re.I)
    if terrain_match:
        out["Terrain_m2"] = terrain_match.group(1)
    else :
        out["Terrain_m2"] = "Non communiqué"

    # DPE
    dpe_match = re.search(r"DPE\s*:\s*([A-G])", details_str, re.I)
    if dpe_match:
        out["DPE"] = dpe_match.group(1)
    else :
        out["DPE"] = "Non communiqué"

    return out

#Prix m2
df["Prix_m2"] = df["Prix"].str.extract(r"(\d[\d\s\u202f]+€ / m2)")
df["Prix"] = df["Prix"].str.replace(r"\*?\d[\d\s\u202f]+€ / m2", "", regex = True)
df["Prix"] = df["Prix"].str.strip()
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

# CONCAT sans créer de doublons
df_final = pd.concat([df.drop(columns=["Détails"], errors="ignore"), details_df], axis=1)


# PARTIE Cleaning des données

# Transformer quelques types de biens
df["type"] = df["type"].str.replace("loft", "appartement", case=False)
df["type"] = df["type"].str.replace("villa", "maison", case=False)
df["type"] = df["type"].str.replace("Duplex/triplex", "appartement", case=False)


#Liste des types à exclure (outliers)
types_a_exclure = [
    "terrain", "hotel", "hôtel", "peniche", "péniche", "garage", "boutique",
    "commerce", "bureau", "immeuble", "chateau", "château", "grange",
    "hangar", "parking", "box","ferme","plateau"
]

print("Début du géocodage des localisations...")

geolocator = Nominatim(user_agent="projet_immo_sorbonne", timeout=5)

def geocode_loc (loc) :
    if not isinstance(loc, str) or loc.strip() == "" :
        return None, None
    
    query = loc + ", France"

    for attempt in range(3):
        try:
            location = geolocator.geocode(query, timeout=5)  # ❤️ timeout augmenté
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
        # petit log
        print(f"{i+1}/{len(loc_series)} | {loc_str} -> {lat}, {lon}")
        sleep(1)  # respecter Nominatim

    latitude.append(lat)
    longitude.append(lon)

df_final["Latitude"] = latitude
df_final["Longitude"] = longitude

clean_file = os.path.join(BASE_DIR, "..", "DATA", "ANNONCES_CLEAN.csv")

df_final.to_csv(clean_file, index=False, encoding="utf-8")
print("OK : ANNONCES_CLEAN.csv généré dans :", os.path.abspath(clean_file))

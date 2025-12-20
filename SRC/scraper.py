import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import re
import json

# CONFIG GÉNÉRALE

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

villes = [
    "paris-75", "marseille", "lyon", "toulouse", "nice",
    "nantes", "montpellier", "strasbourg", "bordeaux", "lille",
    "rennes", "reims", "toulon", "saint-etienne", "le-havre",
    "grenoble", "dijon", "angers", "nimes", "clermont-ferrand"
]

nb_pages = 5  
url_base = "https://www.paruvendu.fr/immobilier/vente/"
MAX_ANNONCES_PAR_RUN = 1000          # limite de sécurité par exécution
CHECKPOINT_FILE = "checkpoint.json"

# CHEMIN CSV  

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(BASE_DIR, "..", "DATA", "ANNONCES_RAW.csv")

# lignes déjà présentes dans le CSV (si le fichier existe)
existing_rows = []

if os.path.exists(csv_file):
    print(f"CSV existant trouvé, chargement : {csv_file}")
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_rows.append(row)
    print(f"{len(existing_rows)} annonces déjà présentes dans le CSV.")
else:
    print("Pas de CSV existant, on part de zéro.")

# nouvelles lignes à ajouter pour CE run
scraped_rows = []


#  OUTILS CHECKPOINT 


def load_checkpoint():
    """Charge la position sauvegardée (ville/page) si elle existe."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    "ville_index": int(data.get("ville_index", 0)),
                    "page": int(data.get("page", 1)),
                }
        except Exception:
            pass
    return {"ville_index": 0, "page": 1}


def save_checkpoint(ville_index, page):
    """Sauvegarde la position actuelle (ville/page)."""
    data = {"ville_index": ville_index, "page": page}
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


# DÉTECTION CAPTCHA


def is_captcha(html: str) -> bool:
    """Renvoie True si la page semble être la page CAPTCHA de ParuVendu."""
    return (
        "Nos systèmes ont détecté un trafic inhabituel" in html
        or "Je ne suis pas un robot" in html
    )


# SESSION HTTP 

session = requests.Session()
session.headers.update(headers)

# SCRAPING 

checkpoint = load_checkpoint()
start_ville_index = checkpoint["ville_index"]
start_page = checkpoint["page"]

print("Reprise à partir de : ville_index =", start_ville_index, ", page =", start_page)

stop_scraping = False
nb_annonces_run = 0  # nombre d'annonces récupérées sur CETTE exécution

for i_ville, ville in enumerate(villes):
    if stop_scraping:
        break

    # on saute les villes déjà traitées dans des runs précédents
    if i_ville < start_ville_index:
        continue

    print(f"\n=== Scraping {ville} ===")

    for page in range(1, nb_pages + 1):
        if stop_scraping:
            break

        # si on reprend en cours de route
        if i_ville == start_ville_index and page < start_page:
            continue

        url_ville = f"{url_base}{ville}/?p={page}&allp=1"
        print(f"  -> Page {page} : {url_ville}")

        # requête sur la page de LISTE
        try:
            response = session.get(url_ville, timeout=10)
        except requests.exceptions.RequestException as e:
            print("  !! Erreur requête liste :", e)
            continue

        if is_captcha(response.text):
            print("⚠️ CAPTCHA détecté sur une page de LISTE. Arrêt du scraping.")
            save_checkpoint(i_ville, page)
            stop_scraping = True
            break

        soup = BeautifulSoup(response.text, "lxml")
        annonces = soup.find_all("div", class_="blocAnnonce")

        if not annonces:
            print("  (aucune annonce trouvée sur cette page)")
            save_checkpoint(i_ville, page + 1)
            time.sleep(2)
            continue

        for a in annonces:
            if stop_scraping:
                break

            # limite de sécurité PAR RUN
            if nb_annonces_run >= MAX_ANNONCES_PAR_RUN:
                print(f"\nLimite de {MAX_ANNONCES_PAR_RUN} annonces atteinte pour ce run, arrêt.")
                save_checkpoint(i_ville, page)
                stop_scraping = True
                break

            #  Titre + lien depuis la LISTE 
            annonce_h3 = a.find("h3")
            if not annonce_h3:
                continue

            annonce_title = annonce_h3.find("a")
            if not annonce_title or not annonce_title.has_attr("href"):
                continue

            title = annonce_title.get("title", "").strip()
            lien = "https://www.paruvendu.fr" + annonce_title["href"]

            # Description
            description_tag = a.find("p", class_="text-justify")
            description = description_tag.get_text(strip=True) if description_tag else ""

            # Prix 
            price_tag = a.find("div", class_="encoded-lnk")
            price = price_tag.get_text(strip=True) if price_tag else ""

            # LOCALISATION SUR PAGE DÉTAIL
            localisation = ""

            try:
                detail = session.get(lien, timeout=10)
            except requests.exceptions.RequestException as e:
                print("  !! Erreur requête détail :", e, "pour", lien)
                continue

            if is_captcha(detail.text):
                print("⚠️ CAPTCHA détecté sur une page de DÉTAIL. Arrêt du scraping.")
                print("URL concernée :", lien)
                save_checkpoint(i_ville, page)
                stop_scraping = True
                break

            soup_loc = BeautifulSoup(detail.text, "lxml")

            # 1. id=detail_loc (cas normal)
            loc_tag = soup_loc.find("span", id="detail_loc")

            # 2. fallback : classe (selon HTML)
            if not loc_tag:
                loc_tag = soup_loc.find("span", class_="ttldetail_loc1h")
            if not loc_tag:
                loc_tag = soup_loc.find("span", class_="ttldetail_loch1")

            if loc_tag:
                localisation = loc_tag.get_text(strip=True)
            else:
                print("  PAS DE LOC ➜", lien, "| status:", detail.status_code)

            # on ralentit un peu les requêtes DETAIL
            time.sleep(1)

            #  Détails (pièces, surface, etc.) depuis la LISTE
            details = []
            for df in a.select("div.flex.flex-wrap.gap-x-3 > *"):
                details.append(df.get_text(strip=True))

            scraped_rows.append({
                "Ville": ville,
                "Titre": title,
                "Lien": lien,
                "Description": description,
                "Prix": price,
                "Localisation": localisation,
                "Détails": ", ".join(details),
            })

            nb_annonces_run += 1

        # après la page, on met à jour le checkpoint pour reprendre sur la suivante
        save_checkpoint(i_ville, page + 1)

        # pause entre pages de résultats
        time.sleep(2)

# FUSION ANCIEN + NOUVEAU & SAUVEGARDE

print(f"\nAnnonces récupérées sur ce run : {len(scraped_rows)}")

# fusion : anciennes annonces + nouvelles
all_rows = existing_rows + scraped_rows

# dédup par Lien
seen = set()
unique_rows = []
for r in all_rows:
    lien = r.get("Lien")
    if lien and lien not in seen:
        unique_rows.append(r)
        seen.add(lien)

print(f"Total d'annonces uniques après fusion : {len(unique_rows)}")

# Sauvegarde
os.makedirs(os.path.dirname(csv_file), exist_ok=True)

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["Ville", "Titre", "Lien", "Description", "Prix", "Localisation", "Détails"],
    )
    writer.writeheader()
    writer.writerows(unique_rows)

print(f"\n✅ Fichier csv mis à jour : {os.path.abspath(csv_file)}")


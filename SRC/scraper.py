import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import re

headers = {"User-Agent": "Mozilla/5.0"}

# CONFIGURATION
villes = [
    "paris-75", "marseille", "lyon", "toulouse", "nice",
    "nantes", "montpellier", "strasbourg", "bordeaux", "lille",
    "rennes", "reims", "toulon", "saint-etienne", "le-havre",
    "grenoble", "dijon", "angers", "nimes", "clermont-ferrand"
]
nb_pages = 5
url_base = "https://www.paruvendu.fr/immobilier/vente/"

result = []


# BOUCLE SUR LES VILLES ET PAGES

for ville in villes:
    print(f"Scraping {ville}...")
    for page in range(1, nb_pages + 1):

        url_ville = url_base + f'{ville}/?p={page}&allp=1'
        print(f"  Page {page}...")

        response = requests.get(url_ville, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        annonces = soup.find_all("div", class_="blocAnnonce")

        for a in annonces:
            # Titre et lien
            annonce_h3 = a.find("h3")
            if not annonce_h3 :
                continue

            annonce_title = annonce_h3.find("a") 
            if not annonce_title or not annonce_title.has_attr("href") :
                continue

            title = annonce_title["title"].strip()
            lien = "https://www.paruvendu.fr" + annonce_title["href"]

            # Description
            description_tag = a.find("p", class_="text-justify")
            description = description_tag.get_text(strip=True) if description_tag else ""

            # Prix
            price_tag = a.find("div", class_="encoded-lnk")
            price = price_tag.get_text(strip=True) if price_tag else ""

            localisation = ""
            if lien :
                detail = requests.get(lien, headers=headers)
                soup_loc = BeautifulSoup(detail.text, "lxml")
                loc_tag = soup_loc.find("span", id="detail_loc")
                if loc_tag :
                    loc_tag = soup_loc.find("span", class_="ttldetail_loch1")
                if loc_tag :
                    localisation = loc_tag.get_text(strip=True)

            # Pièces, chambres, surface, etc.
            details = []
            for df in a.select("div.flex.flex-wrap.gap-x-3 > *") :
                details.append(df.get_text(strip=True))

            result.append({
                "Ville": ville,
                "Titre": title,
                "Lien": lien,
                "Description": description,
                "Prix": price,
                "Localisation" : localisation,
                "Détails": ", ".join(details)
            })

        # Petit délai pour ne pas surcharger le site
        time.sleep(2)


# SAUVEGARDE CSV

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(BASE_DIR, "..", "DATA", "ANNONCES_RAW.csv")

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Ville", "Titre", "Lien", "Description", "Prix", "Localisation", "Détails"])
    writer.writeheader()
    writer.writerows(result)

    print(f"Fichier csv créé : {os.path.abspath(csv_file)}")

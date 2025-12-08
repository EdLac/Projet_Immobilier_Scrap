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
            annonce_title = annonce_h3.find("a") if annonce_h3 else None
            title = annonce_title["title"].strip() if annonce_title and annonce_title.has_attr("title") else None
            lien = "https://www.paruvendu.fr" + annonce_title["href"] if annonce_title else None

            # Description
            description_tag = a.find("p", class_="text-justify")
            description = description_tag.get_text(strip=True) if description_tag else None

            # Prix
            price_block = a.find("div", class_="encoded-lnk")
            if price_block:
                price_tag = price_block.find("div")
                price = price_tag.get_text(strip=True) if price_tag else None
            else:
                price = None

            #adresse = get_address_from_annonce(lien) if lien else None

            # Pièces, chambres, surface, etc.
            details = []
            detail_tags = a.select("div.flex.flex-wrap.gap-x-3 > *")
            for dt in detail_tags:
                details.append(dt.get_text(strip=True))

            result.append({
                "Ville": ville,
                "Titre": title,
                "Lien": lien,
                "Description": description,
                "Prix": price,
                #"Adresse" : adresse,
                "Détails": ", ".join(details)
            })

        # Petit délai pour ne pas surcharger le site
        time.sleep(2)


# SAUVEGARDE CSV

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(BASE_DIR, "..", "DATA", "ANNONCES_RAW.csv")

try:
    with open(csv_file, "x", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Ville", "Titre", "Lien", "Description", "Prix", "Détails"])
        writer.writeheader()
        for r in result:
            writer.writerow(r)

    print(f"Fichier csv créé : {os.path.abspath(csv_file)}")

except FileExistsError:
    print("Le fichier existe déjà, aucune création effectuée.")
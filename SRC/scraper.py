import requests
from bs4 import BeautifulSoup
import time
import pickle
import os
import pandas as pd

url = "https://www.paruvendu.fr/immobilier/vente/paris-75/?p=1"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

villes_principales = [
    "paris-75",
    "marseille",
    "lyon",
    "toulouse",
    "nice",
    "nantes",
    "montpellier",
    "strasbourg",
    "bordeaux",
    "lille",
    "rennes",
    "reims",
    "toulon",
    "saint-etienne",
    "le-havre",
    "grenoble",
    "dijon",
    "angers",
    "nimes",
    "clermont-ferrand"
]

def scrap_annonces(page) :
    url_base = "https://www.paruvendu.fr/immobilier/vente/"
    url_ville = url_base + f'{ville}/?p={page}&allp=1'
    response = requests.get(url_ville, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    annonces = soup.find_all("div", class_="blocAnnonce")

    result = []
 
    for a in annonces :

        annonce_h3 = a.find("h3")
        annonce_title = annonce_h3.find("a") if annonce_h3 else None
        title = annonce_title["title"].strip() if annonce_title and annonce_title.has_attr("title") else None

        description = a.find("p", class_="text-justify").get_text(strip=True) if a.find("p", class_="text-justify") else None

        price_block = a.find("div", class_="encoded-lnk")
        if price_block :
            price_tag = price_block.find("div")
            price = price_tag.get_text(strip=True) if price_tag else None
        else :
            price = None
    return annonces

def scrap_pages():

    all_annonces = []

    for ville in villes_principales :
        ville_scrap = scrap_annonces(page)

        all_annonces = all_annonces.append(ville_scrap)
        dataframe = pd.DataFrame(all_annonces)
    return all_annonces

nimes_scrap = scrap_annonces(nimes)



if os.path.exists("annonces.pkl"):
    print("Chargement du fichier annonces.pkl (pas de scraping)")
    with open("annonces.pkl", "rb") as f:
        all_annonces_pages = pickle.load(f)
else:
    print("Aucun fichier trouvé → Scraping en cours…")
    all_annonces_pages = scrap_pages()
    with open("annonces.pkl", "wb") as f:
        pickle.dump(all_annonces_pages, f)
    print("Données sauvegardées dans annonces.pkl")

print("\n=== Première annonce ===\n")
print(all_annonces_pages[0].get_text(" ", strip=True))

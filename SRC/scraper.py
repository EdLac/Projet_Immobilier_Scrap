import requests
from bs4 import BeautifulSoup
import time
import pickle
import os

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
    url_ville = url_base + f'{villes_principales}/?p={page}&allp=1'
    response = requests.get(url_ville, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    annonces = soup.find_all("div", class_="blocAnnonce")
    return annonces


def scrap_pages():
    all_annonces = []
    page = 1
    ville = [0]
    
    while True :
        all_annonces = scrap_annonces(page)

        all_annonces += annonces
        page += 1
        time.sleep(0.2)

    return all_annonces

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

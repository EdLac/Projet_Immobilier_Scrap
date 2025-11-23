import requests
from bs4 import BeautifulSoup
import time

url = "https://www.paruvendu.fr/immobilier/annonceimmofo/liste/listeAnnonces?tt=1&tbApp=1&tbDup=1&tbChb=1&tbLof=1&tbAtl=1&tbPla=1&tbMai=1&tbVil=1&tbCha=1&tbPro=1&tbHot=1&tbMou=1&tbFer=1&ddlFiltres=nofilter&prestige=0"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "lxml")


def scrap_annonces(page) :
    url_base = "https://www.paruvendu.fr/immobilier/annonceimmofo/liste/listeAnnonces?tt=1&tbApp=1&tbDup=1&tbChb=1&tbLof=1&tbAtl=1&tbPla=1&tbMai=1&tbVil=1&tbCha=1&tbPro=1&tbHot=1&tbMou=1&tbFer=1&ddlFiltres=nofilter&prestige=0"
    url_all = url_base + f'&p={page}'
    response = requests.get(url_all, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    annonces = soup.find_all("div", class_="blocAnnonce")
    return annonces

def scrap_pages (max_page = 500) :
    all_annonces = []
    page = 1
    while page <= max_page :
        annonces = scrap_annonces(page)
        print(f"Scrapping page : {page}")
        if len(annonces) == 0 :
            print("Plus d'annonce.")
            break

        all_annonces += annonces
        page += 1
        time.sleep(0.5)

    return all_annonces

all_annonces_pages = scrap_pages()
print(f"\nTotal d'annonces récupérées : {len(all_annonces_pages)}")

import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import re

headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get("https://www.paruvendu.fr/immobilier/vente/appartement/1286537676A1KIVHAP000", headers=headers)
soup = BeautifulSoup(response.text, "lxml")

localisation = soup.find("span", id="detail_loc")
localisation = localisation.get_text(strip=True) if localisation else None

print(localisation)
import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import openai

st.set_page_config(page_title="Analyse LeBonCoin", layout="centered")
st.title("🔍 Analyse intelligente d'une annonce LeBonCoin")

# Clé API OpenAI (à activer si test OpenAI)
# openai.api_key = "sk-..."

sites_fiables = {
    "autos": [
        ("La Centrale", "https://www.lacentrale.fr"),
        ("Aramis Auto", "https://www.aramisauto.com"),
        ("AutoHero", "https://www.autohero.com/fr"),
        ("Groupe Schumacher", "https://www.groupe-schumacher.com")
    ],
    "motos": [
        ("Moto Station", "https://www.moto-station.com"),
        ("La Centrale Motos", "https://www.lacentrale.fr/moto"),
        ("ViaMoto", "https://www.viamoto.fr")
    ],
    "immobilier": [
        ("SeLoger", "https://www.seloger.com"),
        ("LeBonCoin Immo", "https://www.leboncoin.fr/immobilier"),
        ("Logic-Immo", "https://www.logic-immo.com")
    ],
    "informatique": [
        ("LDLC", "https://www.ldlc.com"),
        ("Materiel.net", "https://www.materiel.net"),
        ("TopAchat", "https://www.topachat.com")
    ],
    "bricolage": [
        ("ManoMano", "https://www.manomano.fr"),
        ("Leroy Merlin", "https://www.leroymerlin.fr"),
        ("Castorama", "https://www.castorama.fr")
    ],
    "électroménager": [
        ("Darty", "https://www.darty.com"),
        ("Boulanger", "https://www.boulanger.com"),
        ("Electro Dépôt", "https://www.electrodepot.fr")
    ]
}

url = st.text_input("Colle ici l'URL de l'annonce LeBonCoin :")

if url:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.content, 'html.parser')

        # === INFOS ANNONCE ===
        title = soup.find('h1') or soup.find('meta', property='og:title')
        price = soup.find('span', string=re.compile("€")) or soup.find('meta', property='product:price:amount')
        desc = soup.find('div', {'data-qa-id': 'adview_description_container'}) or soup.find('meta', {'name': 'description'})
        images = soup.find_all('img')

        title_text = title.text.strip() if title and hasattr(title, 'text') else title['content'].strip() if title and title.has_attr('content') else "(titre non trouvé)"
        price_text = price.text.strip() if price and hasattr(price, 'text') else price['content'].strip() + " €" if price and price.has_attr('content') else "(prix non trouvé)"
        desc_text = desc.text.strip() if desc and hasattr(desc, 'text') else desc['content'].strip() if desc and desc.has_attr('content') else "(description non trouvée)"

        st.subheader("📄 Informations extraites")
        st.markdown(f"**Titre :** {title_text}")
        st.markdown(f"**Prix :** {price_text}")
        st.markdown(f"**Description :** {desc_text[:300]}...")
        st.markdown(f"**Nombre d'images :** {len(images)}")

        # Le reste du code reste inchangé pour profil vendeur, analyse, IA, etc.

    except Exception as e:
        st.error("Erreur lors de l'analyse de l'annonce :")
        st.text(str(e))


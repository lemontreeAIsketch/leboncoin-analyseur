import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
import openai
import json

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

        script_json = soup.find("script", type="application/ld+json")
        data = json.loads(script_json.string) if script_json else {}

        title_text = data.get("name") or "(titre non trouvé)"
        price_text = str(data.get("offers", {}).get("price", "(prix non trouvé)")) + " €" if data.get("offers") else "(prix non trouvé)"
        desc_text = data.get("description") or "(description non trouvée)"
        image_list = data.get("image", [])
        images = image_list if isinstance(image_list, list) else [image_list]

        st.subheader("📄 Informations extraites")
        st.markdown(f"**Titre :** {title_text}")
        st.markdown(f"**Prix :** {price_text}")
        st.markdown(f"**Description :** {desc_text[:300]}...")
        st.markdown(f"**Nombre d'images :** {len(images)}")

    except Exception as e:
        st.error("Erreur lors de l'analyse de l'annonce :")
        st.text(str(e))

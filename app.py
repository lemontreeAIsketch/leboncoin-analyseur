import streamlit as st
import requests
import re
import numpy as np
import openai
import json
from bs4 import BeautifulSoup

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
        ad_id = url.strip().split("/")[-1]
        api_url = f"https://api.leboncoin.fr/finder/classified/{ad_id}"
        r = requests.get(api_url, headers=headers)

        if r.status_code == 200 and r.text.strip():
            data = r.json()
            title_text = data.get("title") or "(titre non trouvé)"
            price_text = str(data.get("price", {}).get("amount", "(prix non trouvé)")) + " €"
            desc_text = data.get("body", "(description non trouvée)")
            images = data.get("images", {}).get("urls", [])
        else:
            r = requests.get(url, headers=headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            scripts = soup.find_all("script")
            preloaded_json = None
            for script in scripts:
                content = script.string or "".join(script.contents)
                if "window.__PRELOADED_STATE__ = " in content:
                    json_raw = content.split("window.__PRELOADED_STATE__ = ", 1)[1].strip()
                    if json_raw.endswith(";"):
                        json_raw = json_raw[:-1]
                    preloaded_json = json.loads(json_raw)
                    break

            if not preloaded_json:
                raise Exception("Aucune donnée utilisable trouvée sur la page")

            ad_data = preloaded_json.get("ad", {}).get("ad", {})
            title_text = ad_data.get("subject", "(titre non trouvé)")
            price_text = str(ad_data.get("price", "(prix non trouvé)")) + " €"
            desc_text = ad_data.get("body", "(description non trouvée)")
            images = ad_data.get("images", [])

        st.subheader("📄 Informations extraites")
        st.markdown(f"**Titre :** {title_text}")
        st.markdown(f"**Prix :** {price_text}")
        st.markdown(f"**Description :** {desc_text[:300]}...")
        st.markdown(f"**Nombre d'images :** {len(images)}")

    except Exception as e:
        st.error("Erreur lors de l'analyse de l'annonce :")
        st.text(str(e))

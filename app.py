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

        title = soup.find('h1')
        price = soup.find('span', string=re.compile("€"))
        desc = soup.find('div', {'data-qa-id': 'adview_description_container'})
        images = soup.find_all('img')

        title_text = title.text.strip() if title else "(titre non trouvé)"
        price_text = price.text.strip() if price else "(prix non trouvé)"
        desc_text = desc.text.strip() if desc else "(description non trouvée)"

        st.subheader("📄 Informations extraites")
        st.markdown(f"**Titre :** {title_text}")
        st.markdown(f"**Prix :** {price_text}")
        st.markdown(f"**Description :** {desc_text[:300]}...")
        st.markdown(f"**Nombre d'images :** {len(images)}")

        vendeur_bloc = soup.find('div', {'data-qa-id': 'adview_profile_container'})
        vendeur_nom = vendeur_bloc.find('span') if vendeur_bloc else None
        vendeur_anciennete = vendeur_bloc.find(string=re.compile("depuis")) if vendeur_bloc else None
        vendeur_type = "Professionnel" if vendeur_bloc and "pro" in vendeur_bloc.text.lower() else "Particulier"

        vendeur_infos = {
            'nom': vendeur_nom.text.strip() if vendeur_nom else "(non trouvé)",
            'anciennete': vendeur_anciennete.strip() if vendeur_anciennete else "(non trouvée)",
            'type': vendeur_type
        }

        st.subheader("👤 Profil du vendeur")
        st.markdown(f"**Nom :** {vendeur_infos['nom']}")
        st.markdown(f"**Type :** {vendeur_infos['type']}")
        st.markdown(f"**Ancienneté :** {vendeur_infos['anciennete']}")

        risques_vendeur = []
        if vendeur_infos['anciennete'] == "(non trouvée)" or re.search(r'\b(jour|semaine)\b', vendeur_infos['anciennete']):
            risques_vendeur.append("Compte récent")
        if vendeur_infos['nom'] == "(non trouvé)":
            risques_vendeur.append("Nom du vendeur non affiché")

        if risques_vendeur:
            st.error("⚠️ Risques liés au profil vendeur :")
            for r in risques_vendeur:
                st.markdown(f"- {r}")
        else:
            st.success("✅ Profil vendeur sans risque évident")

        try:
            prix_numerique = int(re.sub(r'[^0-9]', '', price_text))
            moyenne = 230
            ecart = 50
            if prix_numerique < moyenne - ecart:
                st.success("💰 Cette annonce semble être une bonne affaire.")
            elif prix_numerique > moyenne + ecart:
                st.warning("💸 Cette annonce est plus chère que la moyenne estimée.")
            else:
                st.info("📊 Prix dans la moyenne estimée.")
        except:
            st.info("(Analyse de prix non disponible)")

        risques_annonce = []
        if len(images) < 2:
            risques_annonce.append("Annonce avec peu ou pas de photos réelles")
        if 'paypal' in desc_text.lower() or 'mandat' in desc_text.lower():
            risques_annonce.append("Mention d’un mode de paiement à risque")
        if len(desc_text) < 100:
            risques_annonce.append("Description trop courte")
        if re.search(r'(urgent|très bon prix|contact uniquement par mail)', desc_text, re.I):
            risques_annonce.append("Langage typique de fraude")

        if risques_annonce:
            st.error("⚠️ Risques potentiels dans l’annonce :")
            for r in risques_annonce:
                st.markdown(f"- {r}")
        else:
            st.success("✅ Aucun indice de fraude détecté dans l’annonce")

        st.subheader("📈 Autres annonces similaires (fictives)")
        autres_annonces = [
            {"titre": "Produit similaire A", "prix": 260},
            {"titre": "Produit similaire B", "prix": 245},
            {"titre": "Produit similaire C", "prix": 295},
            {"titre": "Produit similaire D", "prix": 310},
        ]
        for a in autres_annonces:
            st.markdown(f"- {a['titre']} – {a['prix']} €")

        prix_annonces = [a['prix'] for a in autres_annonces]
        if prix_annonces:
            moyenne_autres = np.mean(prix_annonces)
            st.markdown(f"📊 Prix moyen observé sur annonces similaires : **{int(moyenne_autres)} €**")
            try:
                ecart_pct = ((prix_numerique - moyenne_autres) / moyenne_autres) * 100
                if ecart_pct < -20:
                    st.success("🔥 Cette annonce est nettement moins chère que les autres comparables.")
                elif ecart_pct > 20:
                    st.warning("📈 Cette annonce est significativement plus chère que la moyenne.")
                else:
                    st.info("💡 Le prix est dans la fourchette des annonces similaires.")
            except:
                pass

        st.subheader("🔗 Sites fiables pour comparaison ou achat sécurisé")
        for cat, liens in sites_fiables.items():
            st.markdown(f"**{cat.upper()}**")
            for nom, url_site in liens:
                st.markdown(f"- [{nom}]({url_site})")

    except Exception as e:
        st.error("Erreur lors de l'analyse de l'annonce :")
        st.text(str(e))

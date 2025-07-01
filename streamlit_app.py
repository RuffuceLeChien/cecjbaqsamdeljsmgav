import streamlit as st

import streamlit as st
import requests
import random
import string
import time

# Configuration de la page
st.set_page_config(
    page_title="Générateur d'Emails - Jeu",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 Générateur d'Emails Temporaires pour Jeu")
st.markdown("---")

# Fonction pour générer un email temporaire avec TempMail
def generate_temp_email():
    try:
        # Génération d'un nom d'utilisateur aléatoire
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        
        # Appel à l'API TempMail pour obtenir les domaines disponibles
        domains_response = requests.get("https://www.1secmail.com/api/v1/?action=getDomainList")
        
        if domains_response.status_code == 200:
            domains = domains_response.json()
            domain = random.choice(domains)
            email = f"{username}@{domain}"
            return email
        else:
            # Fallback avec un domaine fixe
            return f"{username}@1secmail.com"
    except:
        # En cas d'erreur, génération d'un email basique
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@1secmail.com"

# Interface utilisateur
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Générateur d'Email")
    
    # Bouton pour générer un email
    if st.button("🔄 Générer un Email Temporaire", type="primary"):
        with st.spinner("Génération en cours..."):
            email = generate_temp_email()
            st.success(f"✅ Email généré : **{email}**")
            
            # Copie automatique dans le presse-papier (instruction)
            st.info("💡 Copiez cet email pour votre jeu !")

with col2:
    st.subheader("Informations")
    st.write("• Emails temporaires valides 1h")
    st.write("• Parfait pour les inscriptions de jeu")
    st.write("• Aucune donnée sauvegardée")

# Section pour les joueurs multiples
st.markdown("---")
st.subheader("🎯 Génération Multiple")

num_players = st.number_input("Nombre de joueurs", min_value=1, max_value=10, value=1)

if st.button("🎮 Générer pour Tous les Joueurs"):
    with st.spinner(f"Génération de {num_players} emails..."):
        emails = []
        for i in range(num_players):
            email = generate_temp_email()
            emails.append(f"Joueur {i+1}: {email}")
            time.sleep(0.5)  # Petite pause pour éviter le spam
        
        st.success("✅ Emails générés pour tous les joueurs !")
        for email in emails:
            st.code(email)

# Footer
st.markdown("---")
st.markdown("*Application créée pour automatiser la génération d'emails temporaires pour les jeux*")
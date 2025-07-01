import streamlit as st
import requests
import random
import string
import time
from datetime import datetime
import json

# Configuration de la page
st.set_page_config(
    page_title="Messagerie de Jeu Multi-Joueurs",
    page_icon="🎮",
    layout="wide"
)

# Initialisation des états de session
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'generated_emails' not in st.session_state:
    st.session_state.generated_emails = []

# Fonction pour générer un email temporaire
def generate_temp_email():
    try:
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        domains_response = requests.get("https://www.1secmail.com/api/v1/?action=getDomainList")
        
        if domains_response.status_code == 200:
            domains = domains_response.json()
            domain = random.choice(domains)
            email = f"{username}@{domain}"
            return email
        else:
            return f"{username}@1secmail.com"
    except:
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"{username}@1secmail.com"

# Fonction pour envoyer un message
def send_message(sender, recipient, content, message_type="private"):
    message = {
        'id': len(st.session_state.messages),
        'sender': sender,
        'recipient': recipient,
        'content': content,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': message_type,  # "private", "broadcast", "group"
        'read': False
    }
    st.session_state.messages.append(message)

# Fonction pour obtenir les messages pour un utilisateur
def get_messages_for_user(user_email):
    messages = []
    for msg in st.session_state.messages:
        if (msg['recipient'] == user_email or 
            msg['sender'] == user_email or 
            msg['recipient'] == 'all' or
            (st.session_state.user_role == 'master' and msg['type'] in ['private', 'group'])):
            messages.append(msg)
    return sorted(messages, key=lambda x: x['timestamp'])

# Fonction pour marquer un message comme lu
def mark_as_read(message_id, user_email):
    for msg in st.session_state.messages:
        if msg['id'] == message_id and msg['recipient'] == user_email:
            msg['read'] = True

# Interface de connexion
def login_interface():
    st.title("🎮 Messagerie de Jeu Multi-Joueurs")
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["🔑 Connexion", "📧 Générer Email", "👑 Maître de Jeu"])
    
    with tab1:
        st.subheader("Connexion Joueur")
        email = st.text_input("Adresse email", placeholder="votre@email.com")
        pseudo = st.text_input("Pseudo (optionnel)", placeholder="VotreNom")
        
        if st.button("Se connecter en tant que Joueur", type="primary"):
            if email:
                if email not in st.session_state.users:
                    st.session_state.users[email] = {
                        'pseudo': pseudo if pseudo else email.split('@')[0],
                        'role': 'player',
                        'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                
                st.session_state.current_user = email
                st.session_state.user_role = 'player'
                st.rerun()
            else:
                st.error("Veuillez entrer une adresse email")
    
    with tab2:
        st.subheader("Générateur d'Email Temporaire")
        
        if st.button("🔄 Générer un Email Temporaire"):
            with st.spinner("Génération en cours..."):
                temp_email = generate_temp_email()
                if temp_email not in st.session_state.generated_emails:
                    st.session_state.generated_emails.append(temp_email)
                st.success(f"✅ Email généré : **{temp_email}**")
                st.info("💡 Copiez cet email pour vous connecter !")
        
        if st.session_state.generated_emails:
            st.subheader("📋 Emails Générés")
            for email in st.session_state.generated_emails[-5:]:  # Afficher les 5 derniers
                st.code(email)
    
    with tab3:
        st.subheader("Connexion Maître de Jeu")
        master_password = st.text_input("Mot de passe maître", type="password")
        master_email = st.text_input("Email du maître", placeholder="maitre@jeu.com")
        
        if st.button("Se connecter en tant que Maître"):
            if master_password == "master123" and master_email:  # Mot de passe simple pour la démo
                if master_email not in st.session_state.users:
                    st.session_state.users[master_email] = {
                        'pseudo': 'Maître du Jeu',
                        'role': 'master',
                        'connected_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                
                st.session_state.current_user = master_email
                st.session_state.user_role = 'master'
                st.rerun()
            else:
                st.error("Mot de passe incorrect ou email manquant")

# Interface principale pour les joueurs
def player_interface():
    current_user_info = st.session_state.users[st.session_state.current_user]
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title(f"🎮 Bienvenue {current_user_info['pseudo']}")
    with col2:
        if st.button("🔄 Actualiser"):
            st.rerun()
    with col3:
        if st.button("🚪 Déconnexion"):
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.rerun()
    
    st.markdown("---")
    
    # Interface de messagerie
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("👥 Utilisateurs connectés")
        
        # Afficher les utilisateurs connectés
        players = [email for email, info in st.session_state.users.items() if info['role'] == 'player']
        masters = [email for email, info in st.session_state.users.items() if info['role'] == 'master']
        
        if masters:
            st.write("**👑 Maîtres de jeu:**")
            for master in masters:
                st.write(f"• {st.session_state.users[master]['pseudo']}")
        
        if players:
            st.write("**🎮 Joueurs:**")
            for player in players:
                if player != st.session_state.current_user:
                    st.write(f"• {st.session_state.users[player]['pseudo']}")
        
        st.markdown("---")
        
        # Zone pour envoyer un message
        st.subheader("✉️ Envoyer un message")
        
        recipients = []
        for email, info in st.session_state.users.items():
            if email != st.session_state.current_user:
                recipients.append(f"{info['pseudo']} ({email})")
        
        if recipients:
            selected_recipient = st.selectbox("Destinataire", recipients)
            message_content = st.text_area("Votre message", height=100)
            
            if st.button("📤 Envoyer", type="primary"):
                if message_content and selected_recipient:
                    recipient_email = selected_recipient.split('(')[1].replace(')', '')
                    send_message(
                        st.session_state.current_user,
                        recipient_email,
                        message_content
                    )
                    st.success("Message envoyé !")
                    st.rerun()
                else:
                    st.error("Veuillez saisir un message")
        else:
            st.info("Aucun autre utilisateur connecté")
    
    with col_right:
        st.subheader("💬 Messages")
        
        # Affichage des messages
        messages = get_messages_for_user(st.session_state.current_user)
        
        if messages:
            for msg in messages[-10:]:  # Afficher les 10 derniers messages
                sender_name = st.session_state.users.get(msg['sender'], {}).get('pseudo', msg['sender'])
                recipient_name = st.session_state.users.get(msg['recipient'], {}).get('pseudo', msg['recipient'])
                
                # Style différent selon l'expéditeur/destinataire
                if msg['sender'] == st.session_state.current_user:
                    # Message envoyé
                    st.markdown(f"""
                    <div style='text-align: right; margin: 10px 0;'>
                        <div style='background-color: #0084ff; color: white; padding: 10px; border-radius: 10px; display: inline-block; max-width: 70%;'>
                            <strong>Vous → {recipient_name}</strong><br>
                            {msg['content']}<br>
                            <small>{msg['timestamp']}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Message reçu
                    st.markdown(f"""
                    <div style='text-align: left; margin: 10px 0;'>
                        <div style='background-color: #f1f1f1; color: black; padding: 10px; border-radius: 10px; display: inline-block; max-width: 70%;'>
                            <strong>{sender_name} → Vous</strong><br>
                            {msg['content']}<br>
                            <small>{msg['timestamp']}</small>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Marquer comme lu
                    mark_as_read(msg['id'], st.session_state.current_user)
        else:
            st.info("Aucun message pour le moment")

# Interface pour le maître de jeu
def master_interface():
    current_user_info = st.session_state.users[st.session_state.current_user]
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.title(f"👑 Panneau Maître - {current_user_info['pseudo']}")
    with col2:
        if st.button("🔄 Actualiser"):
            st.rerun()
    with col3:
        if st.button("🚪 Déconnexion"):
            st.session_state.current_user = None
            st.session_state.user_role = None
            st.rerun()
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["💬 Messagerie", "👥 Gestion Joueurs", "📊 Surveillance"])
    
    with tab1:
        col_send, col_messages = st.columns([1, 2])
        
        with col_send:
            st.subheader("📤 Envoyer des messages")
            
            # Liste des joueurs
            players = [email for email, info in st.session_state.users.items() if info['role'] == 'player']
            
            if players:
                # Option pour message individuel ou broadcast
                message_type = st.radio("Type de message", ["Message individuel", "Message à tous"])
                
                if message_type == "Message individuel":
                    player_options = []
                    for player in players:
                        player_options.append(f"{st.session_state.users[player]['pseudo']} ({player})")
                    
                    selected_player = st.selectbox("Choisir un joueur", player_options)
                    
                    message_content = st.text_area("Votre message", height=100)
                    
                    if st.button("📤 Envoyer au joueur"):
                        if message_content and selected_player:
                            player_email = selected_player.split('(')[1].replace(')', '')
                            send_message(
                                st.session_state.current_user,
                                player_email,
                                message_content
                            )
                            st.success(f"Message envoyé à {selected_player.split(' (')[0]} !")
                            st.rerun()
                
                else:  # Message à tous
                    broadcast_content = st.text_area("Message pour tous les joueurs", height=100)
                    
                    if st.button("📢 Diffuser à tous"):
                        if broadcast_content:
                            send_message(
                                st.session_state.current_user,
                                'all',
                                broadcast_content,
                                'broadcast'
                            )
                            st.success("Message diffusé à tous les joueurs !")
                            st.rerun()
            else:
                st.info("Aucun joueur connecté")
        
        with col_messages:
            st.subheader("💬 Historique des messages")
            
            all_messages = st.session_state.messages
            
            if all_messages:
                for msg in all_messages[-15:]:  # 15 derniers messages
                    sender_name = st.session_state.users.get(msg['sender'], {}).get('pseudo', msg['sender'])
                    recipient_name = st.session_state.users.get(msg['recipient'], {}).get('pseudo', msg['recipient'])
                    
                    if msg['recipient'] == 'all':
                        recipient_name = "TOUS LES JOUEURS"
                    
                    # Affichage avec style
                    if msg['sender'] == st.session_state.current_user:
                        color = "#0084ff"
                        text_color = "white"
                    else:
                        color = "#f1f1f1"
                        text_color = "black"
                    
                    st.markdown(f"""
                    <div style='margin: 10px 0; padding: 10px; background-color: {color}; color: {text_color}; border-radius: 10px;'>
                        <strong>{sender_name} → {recipient_name}</strong><br>
                        {msg['content']}<br>
                        <small>{msg['timestamp']}</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Aucun message dans l'historique")
    
    with tab2:
        st.subheader("👥 Joueurs connectés")
        
        players = [(email, info) for email, info in st.session_state.users.items() if info['role'] == 'player']
        
        if players:
            for email, info in players:
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{info['pseudo']}**")
                    st.write(f"Email: {email}")
                    st.write(f"Connecté: {info['connected_at']}")
                with col2:
                    if st.button(f"💬 Message", key=f"msg_{email}"):
                        st.session_state[f'quick_msg_{email}'] = True
                
                # Zone de message rapide
                if st.session_state.get(f'quick_msg_{email}', False):
                    quick_msg = st.text_input(f"Message rapide pour {info['pseudo']}", key=f"input_{email}")
                    col_send, col_cancel = st.columns([1, 1])
                    with col_send:
                        if st.button("Envoyer", key=f"send_{email}"):
                            if quick_msg:
                                send_message(st.session_state.current_user, email, quick_msg)
                                st.success("Message envoyé !")
                                st.session_state[f'quick_msg_{email}'] = False
                                st.rerun()
                    with col_cancel:
                        if st.button("Annuler", key=f"cancel_{email}"):
                            st.session_state[f'quick_msg_{email}'] = False
                            st.rerun()
                
                st.markdown("---")
        else:
            st.info("Aucun joueur connecté")
    
    with tab3:
        st.subheader("📊 Statistiques de surveillance")
        
        # Statistiques générales
        total_players = len([u for u in st.session_state.users.values() if u['role'] == 'player'])
        total_messages = len(st.session_state.messages)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Joueurs connectés", total_players)
        with col2:
            st.metric("Messages échangés", total_messages)
        with col3:
            st.metric("Emails générés", len(st.session_state.generated_emails))
        
        # Conversations entre joueurs
        st.subheader("🔍 Conversations entre joueurs")
        
        player_conversations = {}
        for msg in st.session_state.messages:
            if (msg['sender'] in [email for email, info in st.session_state.users.items() if info['role'] == 'player'] and
                msg['recipient'] in [email for email, info in st.session_state.users.items() if info['role'] == 'player']):
                
                conv_key = tuple(sorted([msg['sender'], msg['recipient']]))
                if conv_key not in player_conversations:
                    player_conversations[conv_key] = []
                player_conversations[conv_key].append(msg)
        
        if player_conversations:
            for (player1, player2), messages in player_conversations.items():
                name1 = st.session_state.users.get(player1, {}).get('pseudo', player1)
                name2 = st.session_state.users.get(player2, {}).get('pseudo', player2)
                
                with st.expander(f"💬 Conversation {name1} ↔ {name2} ({len(messages)} messages)"):
                    for msg in messages[-5:]:  # 5 derniers messages
                        sender_name = st.session_state.users.get(msg['sender'], {}).get('pseudo', msg['sender'])
                        st.write(f"**{sender_name}** ({msg['timestamp']}): {msg['content']}")
        else:
            st.info("Aucune conversation entre joueurs détectée")

# Interface principale
def main():
    if st.session_state.current_user is None:
        login_interface()
    elif st.session_state.user_role == 'player':
        player_interface()
    elif st.session_state.user_role == 'master':
        master_interface()

if __name__ == "__main__":
    main()
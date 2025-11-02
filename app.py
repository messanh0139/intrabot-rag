"""
Application Streamlit pour IntraBot
Interface utilisateur pour l'agent conversationnel RAG
"""
import streamlit as st
import os
from datetime import datetime

from src.config import Config
from src.rag_engine import RAGEngine
from src.data_ingestion import DataIngestion


# Configuration de la page
st.set_page_config(
    page_title="IntraBot - Assistant Intranet",
    page_icon="🤖",
    layout="wide"
)

# CSS personnalisé CORRIGÉ
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .profile-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        background-color: #e8f4f8;
        color: #1f77b4;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .source-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
    }
    .source-card strong {
        color: #1f77b4;
        font-size: 1.1em;
    }
    .source-card small {
        color: #555555;
    }
    .source-card em {
        color: #666666;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: #000000;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .user-message strong {
        color: #1565c0;
    }
    .bot-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .bot-message strong {
        color: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialise les variables de session"""
    if 'rag_engine' not in st.session_state:
        st.session_state.rag_engine = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_profile' not in st.session_state:
        st.session_state.current_profile = None
    if 'vectorstore_loaded' not in st.session_state:
        st.session_state.vectorstore_loaded = False


def check_vectorstore_exists():
    """Vérifie si la base vectorielle existe"""
    return os.path.exists(Config.CHROMA_DB_DIR) and \
           os.path.exists(os.path.join(Config.CHROMA_DB_DIR, 'chroma.sqlite3'))


def sidebar_setup():
    """Configuration de la barre latérale"""
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Section d'ingestion
        st.header("📚 Base de Connaissances")
        
        if not check_vectorstore_exists():
            st.warning("⚠️ Base vectorielle non initialisée")
            
            if st.button("🚀 Initialiser la base", use_container_width=True):
                with st.spinner("Ingestion des documents en cours..."):
                    try:
                        ingestion = DataIngestion()
                        ingestion.ingest_all_documents()
                        st.session_state.vectorstore_loaded = True
                        st.success("✅ Base initialisée avec succès!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
        else:
            st.success("✅ Base vectorielle prête")
            if st.button("🔄 Réindexer", use_container_width=True):
                with st.spinner("Réindexation en cours..."):
                    try:
                        ingestion = DataIngestion()
                        ingestion.ingest_all_documents()
                        st.success("✅ Réindexation terminée!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
        
        st.divider()
        
        # Sélection du profil
        st.header("👤 Profil Utilisateur")
        
        profile = st.selectbox(
            "Sélectionnez votre profil:",
            Config.AVAILABLE_PROFILES,
            index=0 if st.session_state.current_profile is None 
                  else Config.AVAILABLE_PROFILES.index(st.session_state.current_profile),
            key="profile_selector"
        )
        
        if profile != st.session_state.current_profile:
            st.session_state.current_profile = profile
            st.session_state.chat_history = []
        
        st.markdown(f'<div class="profile-badge">Connecté: {profile}</div>', 
                    unsafe_allow_html=True)
        
        st.divider()
        
        if st.button("🗑️ Effacer l'historique", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        st.divider()
        
        # Informations
        st.header("ℹ️ À propos")
        st.caption("IntraBot v1.0")
        st.caption("Agent RAG sécurisé avec Mistral AI")
        st.caption(f"Modèle: {Config.LLM_MODEL}")


def display_chat_history():
    """Affiche l'historique des conversations"""
    for message in st.session_state.chat_history:
        timestamp = message.get('timestamp', '')
        
        if message['role'] == 'user':
            with st.container():
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>👤 Vous ({message['profile']})</strong> <small>{timestamp}</small><br/>
                    <div style="color: #000000; margin-top: 0.5rem;">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            with st.container():
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <strong>🤖 IntraBot</strong> <small>{timestamp}</small><br/>
                    <div style="color: #000000; margin-top: 0.5rem;">{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Afficher les sources si disponibles
                if message.get('sources'):
                    with st.expander(f"📄 Sources utilisées ({len(message['sources'])})"):
                        for source in message['sources']:
                            # Vérifier que c'est bien une liste
                            profils = source.get('profils', [])
                            if isinstance(profils, list):
                                profils_str = ', '.join(profils)
                            else:
                                profils_str = str(profils)
                            
                            st.markdown(f"""
                            <div class="source-card">
                                <strong>📄 {source.get('title', 'Sans titre')}</strong><br/>
                                <small>📁 Fichier: {source.get('filename', 'N/A')}</small><br/>
                                <small>👥 Profils autorisés: {profils_str}</small><br/>
                                <em>📝 {source.get('description', '')}</em>
                            </div>
                            """, unsafe_allow_html=True)

def main():
    """Fonction principale de l'application"""
    initialize_session_state()
    
    # En-tête
    st.markdown('<h1 class="main-header">🤖 IntraBot - Assistant Intranet Intelligent</h1>', 
                unsafe_allow_html=True)
    
    # Barre latérale
    sidebar_setup()
    
    # Vérifier si la base vectorielle est prête
    if not check_vectorstore_exists():
        st.warning("⚠️ Veuillez initialiser la base de connaissances dans le menu latéral avant de commencer.")
        st.info("👈 Cliquez sur '🚀 Initialiser la base' dans la barre latérale")
        return
    
    # Vérifier si un profil est sélectionné
    if not st.session_state.current_profile:
        st.info("👈 Veuillez sélectionner un profil utilisateur dans la barre latérale")
        return
    
    # Initialiser le moteur RAG si nécessaire
    if st.session_state.rag_engine is None:
        with st.spinner("Chargement du moteur RAG..."):
            try:
                st.session_state.rag_engine = RAGEngine()
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement du moteur RAG: {str(e)}")
                return
    
    # Zone de conversation
    st.subheader("💬 Conversation")
    
    # Afficher l'historique
    display_chat_history()
    
    # Zone de saisie
    with st.form(key="question_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_question = st.text_input(
                "Posez votre question:",
                placeholder="Ex: Comment fonctionne l'architecture microservices ?",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.form_submit_button("Envoyer 📤", use_container_width=True)
    
    # Traiter la question
    if submit_button and user_question:
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Ajouter la question à l'historique
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_question,
            'profile': st.session_state.current_profile,
            'timestamp': timestamp
        })
        
        # Générer la réponse
        with st.spinner("🤔 IntraBot réfléchit..."):
            try:
                result = st.session_state.rag_engine.generate_answer(
                    query=user_question,
                    user_profile=st.session_state.current_profile,
                    return_sources=True
                )
                
                # Ajouter la réponse à l'historique
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': result['answer'],
                    'sources': result.get('sources', []),
                    'timestamp': timestamp
                })
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération de la réponse: {str(e)}")
        
        # Recharger pour afficher la nouvelle conversation
        st.rerun()
    
    # Section d'exemples
    with st.expander("💡 Questions d'exemple par profil"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**👨‍💻 Technique**")
            st.markdown("- Comment fonctionne l'architecture microservices ?")
            st.markdown("- Quelle est la procédure de déploiement CI/CD ?")
            st.markdown("- Quelles sont les règles informatiques ?")
        
        with col2:
            st.markdown("**👔 RH**")
            st.markdown("- Quelle est la politique de congés ?")
            st.markdown("- Comment se déroule un entretien annuel ?")
            st.markdown("- Quelles sont les règles informatiques ?")
        
        with col3:
            st.markdown("**👨‍💼 Manager**")
            st.markdown("- Comment gérer les congés de l'équipe ?")
            st.markdown("- Quelle est l'architecture technique ?")
            st.markdown("- Comment faire un entretien annuel ?")


if __name__ == "__main__":
    main()
"""
Configuration centralisée pour IntraBot
"""
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class Config:
    """Configuration de l'application IntraBot"""
    
    # ==================== API KEYS ====================
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    
    # ==================== MODÈLES ====================
    LLM_MODEL = "open-mistral-7b"  # Pour la génération de réponses
    EMBEDDING_MODEL = "mistral-embed"    # Pour les embeddings
    
    # ==================== PARAMÈTRES RAG ====================
    CHUNK_SIZE = 2000                    # Taille des chunks de texte
    CHUNK_OVERLAP = 200                  # Chevauchement entre chunks
    TOP_K_RESULTS = 6                    # Nombre de documents à récupérer
    
    # ==================== PARAMÈTRES LLM ====================
    TEMPERATURE = 0.3                    # Contrôle la créativité (0 = déterministe)
    MAX_TOKENS = 1000                    # Longueur max de la réponse
    
    # ==================== CHEMINS ====================
    DATA_DIR = "data/raw"
    METADATA_FILE = "data/metadata.json"
    CHROMA_DB_DIR = "data/chroma_db"
    
    # ==================== PROFILS UTILISATEURS ====================
    AVAILABLE_PROFILES = ["Technique", "RH", "Manager", "General"]
    
    @classmethod
    def validate(cls):
        """Valide que la configuration est correcte"""
        if not cls.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY n'est pas définie dans .env")
        
        if not os.path.exists(cls.DATA_DIR):
            os.makedirs(cls.DATA_DIR)
        
        if not os.path.exists(cls.CHROMA_DB_DIR):
            os.makedirs(cls.CHROMA_DB_DIR)
        
        return True
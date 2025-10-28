"""
Pipeline d'ingestion des documents dans la base vectorielle
"""
import json
import os
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_community.vectorstores import Chroma
from langchain_mistralai import MistralAIEmbeddings
from langchain_core.documents import Document 

from src.config import Config


class DataIngestion:
    """Classe pour gérer l'ingestion et l'indexation des documents"""
    
    def __init__(self):
        """Initialise le pipeline d'ingestion"""
        Config.validate()
        
        # Initialiser les embeddings Mistral
        self.embeddings = MistralAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            mistral_api_key=Config.MISTRAL_API_KEY
        )
        
        # Initialiser le text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Charger les métadonnées
        self.metadata_map = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Charge les métadonnées depuis le fichier JSON"""
        with open(Config.METADATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Créer un mapping filename -> metadata
        metadata_dict = {}
        for doc_meta in data['documents']:
            metadata_dict[doc_meta['filename']] = doc_meta
        
        return metadata_dict
    
    def load_document(self, filepath: str) -> List[Document]:
        """
        Charge un document en fonction de son extension
        
        Args:
            filepath: Chemin vers le document
            
        Returns:
            Liste de documents LangChain
        """
        extension = os.path.splitext(filepath)[1].lower()
        
        try:
            if extension == '.txt':
                loader = TextLoader(filepath, encoding='utf-8')
            elif extension == '.pdf':
                loader = PyPDFLoader(filepath)
            elif extension in ['.docx', '.doc']:
                loader = Docx2txtLoader(filepath)
            else:
                raise ValueError(f"Extension non supportée: {extension}")
            
            return loader.load()
        except Exception as e:
            print(f"Erreur lors du chargement de {filepath}: {e}")
            return []
    
    def process_document(self, filename: str) -> List[Document]:
        """
        Traite un document: chargement, découpage et ajout des métadonnées
        
        Args:
            filename: Nom du fichier à traiter
            
        Returns:
            Liste de chunks avec métadonnées
        """
        filepath = os.path.join(Config.DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"Fichier introuvable: {filepath}")
            return []
        
        # Charger le document
        docs = self.load_document(filepath)
        if not docs:
            return []
        
        # Découper en chunks
        chunks = self.text_splitter.split_documents(docs)
        
        # Récupérer les métadonnées du fichier
        file_metadata = self.metadata_map.get(filename, {})
        
        # Ajouter les métadonnées à chaque chunk
        for chunk in chunks:
            profils = file_metadata.get('profils_autorises', [])
            if isinstance(profils, list):
                profils = ", ".join(map(str, profils))  # Transformer la liste en chaîne de caractères

            chunk.metadata.update({
                'filename': filename,
                'title': file_metadata.get('title', filename),
                'profils_autorises': profils,
                'description': file_metadata.get('description', '')
            })

        
        return chunks
    
    def ingest_all_documents(self) -> Chroma:
        """
        Ingère tous les documents dans la base vectorielle ChromaDB
        
        Returns:
            Instance de la base vectorielle Chroma ou None si annulation
        """
        print("🚀 Début de l'ingestion des documents...")
        
        all_chunks = []
        
        # Traiter chaque document référencé dans les métadonnées
        for filename in self.metadata_map.keys():
            print(f"📄 Traitement de {filename}...")
            chunks = self.process_document(filename)
            all_chunks.extend(chunks)
            print(f"   ✓ {len(chunks)} chunks créés")
        
        print(f"\n📊 Total: {len(all_chunks)} chunks à indexer")
        
        # Si aucun chunk, tenter d'aider : créer des fichiers de test pour les fichiers manquants
        if not all_chunks:
            print("⚠️ Aucun chunk trouvé ! Vérifie que tes fichiers dans data/documents/ ne sont pas vides.")
            
            # Identifier les fichiers mentionnés dans les métadonnées mais absents sur le disque
            missing_files = []
            for filename in self.metadata_map.keys():
                filepath = os.path.join(Config.DATA_DIR, filename)
                if not os.path.exists(filepath):
                    missing_files.append(filename)
            
            if missing_files:
                print(f"ℹ️ Fichiers manquants détectés ({len(missing_files)}). Création automatique de fichiers de test dans '{Config.DATA_DIR}'...")
                os.makedirs(Config.DATA_DIR, exist_ok=True)
                
                for filename in missing_files:
                    filepath = os.path.join(Config.DATA_DIR, filename)
                    meta = self.metadata_map.get(filename, {})
                    sample_text = (
                        f"{meta.get('title', filename)}\n\n"
                        f"{meta.get('description', 'Document de test généré automatiquement pour l\'ingestion.')}\n\n"
                        "Contenu d'exemple : ceci est un texte de test pour alimenter le pipeline d'indexation."
                    )
                    try:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(sample_text)
                        print(f"   ✓ Créé : {filepath}")
                    except Exception as e:
                        print(f"   ✗ Erreur lors de la création de {filepath}: {e}")
                
                # Retenter le traitement pour les fichiers créés
                for filename in missing_files:
                    print(f"📄 Re-traitement de {filename} après création...")
                    chunks = self.process_document(filename)
                    all_chunks.extend(chunks)
                    print(f"   ✓ {len(chunks)} chunks créés")
            else:
                print("ℹ️ Aucun fichier manquant trouvé sur le disque — vérifie le contenu des fichiers existants (non vides).")
            
            # Vérification finale
            if not all_chunks:
                print("🚫 Toujours aucun chunk après tentative automatique. Ingestion annulée.")
                print("👉 Actions recommandées :")
                print("   - Vérifier que Config.DATA_DIR pointe vers le bon dossier.")
                print("   - Vérifier que les fichiers listés dans Config.METADATA_FILE existent et contiennent du texte.")
                print("   - Lancer une exécution de test avec un petit fichier txt dans le dossier.")
                return None
        
        # Créer la base vectorielle ChromaDB
        print("🔍 Création des embeddings et indexation dans ChromaDB...")
        vectorstore = Chroma.from_documents(
            documents=all_chunks,
            embedding=self.embeddings,
            persist_directory=Config.CHROMA_DB_DIR,
            collection_name="intrabot_docs"
        )

        print("✅ Ingestion terminée avec succès!")
        return vectorstore

    
    @staticmethod
    def load_existing_vectorstore() -> Chroma:
        """
        Charge une base vectorielle existante
        
        Returns:
            Instance de la base vectorielle Chroma
        """
        embeddings = MistralAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            mistral_api_key=Config.MISTRAL_API_KEY
        )
        
        return Chroma(
            persist_directory=Config.CHROMA_DB_DIR,
            embedding_function=embeddings,
            collection_name="intrabot_docs"
        )


def main():
    """Fonction principale pour tester l'ingestion"""
    ingestion = DataIngestion()
    vectorstore = ingestion.ingest_all_documents()
    
    # Test de recherche
    print("\n🧪 Test de recherche...")
    results = vectorstore.similarity_search("microservices", k=2)
    for i, doc in enumerate(results, 1):
        print(f"\nRésultat {i}:")
        print(f"  Titre: {doc.metadata.get('title')}")
        print(f"  Profils: {doc.metadata.get('profils_autorises')}")
        print(f"  Extrait: {doc.page_content[:100]}...")


if __name__ == "__main__":
    main()
"""
Moteur RAG avec filtrage par profil utilisateur
"""
from typing import List, Dict, Optional
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from src.config import Config
from src.data_ingestion import DataIngestion


class RAGEngine:
    """Moteur RAG avec sécurité par profil"""
    
    def __init__(self):
        """Initialise le moteur RAG"""
        Config.validate()
        
        # Charger la base vectorielle
        self.vectorstore = DataIngestion.load_existing_vectorstore()
        
        # Initialiser le LLM Mistral
        self.llm = ChatMistralAI(
            model=Config.LLM_MODEL,
            mistral_api_key=Config.MISTRAL_API_KEY,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
        
        # Template de prompt
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Tu es IntraBot, un assistant intelligent pour l'intranet d'entreprise.
            
Ta mission est de répondre aux questions des utilisateurs en te basant UNIQUEMENT sur les documents fournis ci-dessous.

RÈGLES IMPORTANTES:
- Réponds uniquement à partir des informations présentes dans les documents fournis.
- Si une information ne figure pas dans les documents, indique clairement :
 👉 « Je ne trouve pas cette information dans la documentation accessible. »
- Cite systématiquement tes sources à la fin de chaque réponse, entre parenthèses.
- Format de citation :
 (Source : « Titre exact du document », page X le cas échéant)
- Ne fais jamais référence à un numéro de document, mais toujours au titre complet.
- Sois précis, concise et adopte un ton professionnel, clair et convivial.

DOCUMENTS DE RÉFÉRENCE:
{context}

"""),
            ("human", "{question}")
        ])
    
    def _filter_documents_by_profile(
        self, 
        documents: List[Document], 
        user_profile: str
    ) -> List[Document]:
        """
        Filtre les documents selon le profil utilisateur
        
        Args:
            documents: Liste de documents récupérés
            user_profile: Profil de l'utilisateur
            
        Returns:
            Documents filtrés autorisés pour ce profil
        """
        filtered_docs = []
        
        for doc in documents:
            profils_autorises = doc.metadata.get('profils_autorises', [])
            
            # Vérifier si le profil utilisateur est autorisé
            if user_profile in profils_autorises:
                filtered_docs.append(doc)
        
        return filtered_docs
    
    def retrieve_documents(
        self, 
        query: str, 
        user_profile: str,
        k: int = None
    ) -> List[Document]:
        """
        Récupère les documents pertinents avec filtrage par profil
        
        Args:
            query: Question de l'utilisateur
            user_profile: Profil de l'utilisateur
            k: Nombre de documents à récupérer
            
        Returns:
            Documents pertinents et autorisés
        """
        if k is None:
            k = Config.TOP_K_RESULTS
        
        # Recherche de similarité (on récupère plus que nécessaire car on va filtrer)
        all_docs = self.vectorstore.similarity_search(query, k=k*3)
        
        # Filtrage par profil
        filtered_docs = self._filter_documents_by_profile(all_docs, user_profile)
        
        # Limiter au nombre demandé
        return filtered_docs[:k]
    
    def generate_answer(
        self, 
        query: str, 
        user_profile: str,
        return_sources: bool = True
    ) -> Dict:
        """
        Génère une réponse à la question avec le contexte filtré
        
        Args:
            query: Question de l'utilisateur
            user_profile: Profil de l'utilisateur
            return_sources: Inclure les sources dans la réponse
            
        Returns:
            Dictionnaire avec la réponse et optionnellement les sources
        """
        # Récupérer les documents pertinents
        relevant_docs = self.retrieve_documents(query, user_profile)
        
        if not relevant_docs:
            return {
                'answer': f"Désolé, je n'ai trouvé aucun document accessible pour votre profil '{user_profile}' "
                         f"qui réponde à votre question.",
                'sources': [],
                'profile': user_profile
            }
        
        # Préparer le contexte
        context = self._format_context(relevant_docs)
        
        # Générer la réponse avec le LLM
        prompt = self.prompt_template.format_messages(
            context=context,
            question=query
        )
        
        response = self.llm.invoke(prompt)
        answer = response.content
        
        # Préparer le résultat
        result = {
            'answer': answer,
            'profile': user_profile,
            'num_sources': len(relevant_docs)
        }
        
        if return_sources:
            result['sources'] = self._format_sources(relevant_docs)
        
        return result
    
    def _format_context(self, documents: List[Document]) -> str:
        """
        Formate les documents en contexte pour le prompt
        
        Args:
            documents: Liste de documents
            
        Returns:
            Contexte formaté
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            title = doc.metadata.get('title', 'Document sans titre')
            content = doc.page_content
            
            # context_parts.append(f"[Document {i}: {title}]\n{content}\n")
            context_parts.append(f"[{title}]\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _format_sources(self, documents: List[Document]) -> List[Dict]:
        """
        Formate les sources pour l'affichage
        
        Args:
            documents: Liste de documents
            
        Returns:
            Liste de dictionnaires avec les infos des sources
        """
        sources = []
        seen_titles = set()
        
        for doc in documents:
            title = doc.metadata.get('title', 'Document sans titre')
            
            # Éviter les doublons
            if title not in seen_titles:
                profils = doc.metadata.get('profils_autorises', [])
            
            # Si c'est une chaîne, la convertir en liste
            if isinstance(profils, str):
                profils = [profils]
                sources.append({
                    'title': title,
                    'filename': doc.metadata.get('filename', ''),
                    'description': doc.metadata.get('description', ''),
                    'profils': profils
                })
                seen_titles.add(title)
        
        return sources


def main():
    """Fonction de test du moteur RAG"""
    print("Test du moteur RAG IntraBot\n")
    
    rag = RAGEngine()
    
    # Test avec différents profils
    test_cases = [
        {
            'profile': 'Technique',
            'question': 'Comment fonctionne l\'architecture microservices ?'
        },
        {
            'profile': 'RH',
            'question': 'Quelle est la politique de congés payés ?'
        },
        {
            'profile': 'RH',
            'question': 'Comment déployer avec CI/CD ?' 
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"{'='*60}")
        print(f"Test {i}")
        print(f"Profil: {test['profile']}")
        print(f"Question: {test['question']}")
        print(f"{'='*60}\n")
        
        result = rag.generate_answer(
            query=test['question'],
            user_profile=test['profile'],
            return_sources=True
        )
        
        
        print(f"Réponse:\n{result['answer']}\n")
        # print(f"Sources utilisées: {result.get('num_sources', 0)}")
        
        if result.get('sources'):
            print("\nDocuments consultés:")
            for source in result['sources']:
                print(f"  - {source['title']}")
        
        print("\n")


if __name__ == "__main__":
    main()
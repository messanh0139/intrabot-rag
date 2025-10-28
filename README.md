<<<<<<< HEAD
# intrabot-rag
=======
# 🤖 IntraBot - Agent Conversationnel RAG Sécurisé

Agent conversationnel intelligent basé sur l'architecture RAG (Retrieval-Augmented Generation) avec filtrage de contenu par profil utilisateur.

## 📋 Table des Matières

- [Présentation](#présentation)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Déploiement](#déploiement)
- [Structure du Projet](#structure-du-projet)

## 🎯 Présentation

IntraBot est un assistant conversationnel qui répond aux questions des utilisateurs en se basant sur une documentation interne, avec une contrainte de sécurité importante : **l'accès aux documents est filtré selon le profil de l'utilisateur**.

### Cas d'Usage

- **Profil Technique** : Accès aux documents techniques (architecture, déploiement)
- **Profil RH** : Accès aux documents RH (congés, entretiens annuels)
- **Profil Manager** : Accès mixte (technique + RH)
- **Profil General** : Accès aux documents généraux uniquement

## 🏗️ Architecture

### Stack Technique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **LLM** | Mistral AI (mistral-large-latest) | Génération de réponses |
| **Embeddings** | Mistral Embeddings (mistral-embed) | Vectorisation des documents |
| **Framework RAG** | LangChain | Orchestration du pipeline RAG |
| **Base Vectorielle** | ChromaDB | Stockage et recherche vectorielle |
| **Interface** | Streamlit | Interface utilisateur web |
| **Conteneurisation** | Docker | Déploiement standardisé |
| **Cloud** | Google Cloud Run | Hébergement scalable |

### Schéma d'Architecture

```
┌─────────────┐
│ Utilisateur │
└──────┬──────┘
       │ Profil + Question
       ▼
┌──────────────────────────────────────┐
│      Interface Streamlit (app.py)    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│      Moteur RAG (rag_engine.py)      │
│  ┌────────────────────────────────┐  │
│  │ 1. Recherche Vectorielle       │  │
│  │ 2. Filtrage par Profil  🔒     │  │
│  │ 3. Génération avec LLM         │  │
│  └────────────────────────────────┘  │
└──────┬─────────────────┬─────────────┘
       │                 │
       ▼                 ▼
┌─────────────┐   ┌─────────────┐
│  ChromaDB   │   │ Mistral API │
│  (Vectors)  │   │    (LLM)    │
└─────────────┘   └─────────────┘
```

### Pipeline RAG

1. **Ingestion** (data_ingestion.py)
   - Chargement des documents (TXT, PDF, DOCX)
   - Découpage en chunks (1000 caractères)
   - Ajout des métadonnées (profils autorisés)
   - Création des embeddings avec Mistral
   - Stockage dans ChromaDB

2. **Récupération** (rag_engine.py)
   - Recherche de similarité vectorielle
   - **Filtrage strict par profil utilisateur** 🔒
   - Sélection des top-k documents pertinents

3. **Génération** (rag_engine.py)
   - Construction du prompt avec contexte
   - Génération de la réponse avec Mistral Large
   - Attribution des sources

## ✨ Fonctionnalités

### Fonctionnalités Principales

- ✅ **Réponses contextuelles** basées sur la documentation interne
- ✅ **Filtrage sécurisé** par profil utilisateur
- ✅ **Attribution des sources** pour chaque réponse
- ✅ **Interface intuitive** avec historique de conversation
- ✅ **Support multi-formats** (TXT, PDF, DOCX)

### Sécurité

- 🔒 Chaque document est associé à des profils autorisés
- 🔒 Filtrage au niveau de la récupération vectorielle
- 🔒 Aucune fuite d'information inter-profils
- 🔒 Métadonnées de profil non visibles par l'utilisateur

## 🚀 Installation

### Prérequis

- Python 3.11+
- Docker (optionnel, pour conteneurisation)
- Compte Mistral AI avec clé API

### Installation Locale

1. **Cloner le repository**
```bash
git clone <repo-url>
cd intrabot
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env et ajouter votre clé API Mistral
nano .env
```

5. **Préparer les documents**
```bash
# Créer les répertoires
mkdir -p data/raw

# Copier vos documents dans data/raw/
# Configurer data/metadata.json avec les profils autorisés
```

6. **Ingérer les documents**
```bash
python -m src.data_ingestion
```

7. **Lancer l'application**
```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## 📖 Utilisation

### Interface Utilisateur

1. **Sélection du Profil**
   - Choisir votre profil dans la barre latérale
   - Les profils disponibles : Technique, RH, Manager, General

2. **Initialisation de la Base**
   - Cliquer sur "🚀 Initialiser la base" (première utilisation)
   - Attendre la fin de l'ingestion

3. **Poser des Questions**
   - Saisir votre question dans le champ de texte
   - Cliquer sur "Envoyer 📤"
   - Consulter la réponse et les sources

### Exemples de Questions par Profil

**Profil Technique:**
```
- Comment fonctionne l'architecture microservices ?
- Quelle est la procédure de déploiement CI/CD ?
- Quels outils de monitoring sont recommandés ?
```

**Profil RH:**
```
- Combien de jours de congés ai-je droit ?
- Comment se déroule un entretien annuel ?
- Quelle est la procédure de demande de congé ?
```

**Profil Manager:**
```
- Comment gérer les congés de mon équipe ?
- Quels sont les principes de l'architecture microservices ?
- Comment préparer un entretien annuel ?
```

### API Programmatique

Vous pouvez aussi utiliser le moteur RAG directement en Python :

```python
from src.rag_engine import RAGEngine

# Initialiser le moteur
rag = RAGEngine()

# Poser une question
result = rag.generate_answer(
    query="Comment déployer avec Kubernetes ?",
    user_profile="Technique",
    return_sources=True
)

print(result['answer'])
print(result['sources'])
```

## 🐳 Déploiement

### Déploiement Local avec Docker

1. **Build de l'image**
```bash
chmod +x build.sh
./build.sh
```

2. **Lancement du conteneur**
```bash
chmod +x run_local.sh
./run_local.sh
```

3. **Accéder à l'application**
```
http://localhost:8501
```

### Déploiement sur Google Cloud Run

#### Prérequis
- Google Cloud SDK installé et configuré
- Projet GCP créé
- Billing activé

#### Étapes de Déploiement

1. **Configurer le projet**
```bash
# Définir le projet
gcloud config set project YOUR_PROJECT_ID

# Activer les APIs nécessaires
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

2. **Modifier le script de déploiement**
```bash
nano deploy_gcp.sh
# Modifier PROJECT_ID avec votre ID de projet
```

3. **Déployer**
```bash
chmod +x deploy_gcp.sh
export MISTRAL_API_KEY="votre_clé_mistral"
./deploy_gcp.sh
```

4. **Accéder à l'application**
```bash
# L'URL sera affichée à la fin du déploiement
gcloud run services describe intrabot --region europe-west1 --format 'value(status.url)'
```

### Déploiement sur AWS (Elastic Container Service)

```bash
# Build et tag de l'image
docker build -t intrabot:latest .
docker tag intrabot:latest YOUR_AWS_ACCOUNT.dkr.ecr.eu-west-1.amazonaws.com/intrabot:latest

# Push vers ECR
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin YOUR_AWS_ACCOUNT.dkr.ecr.eu-west-1.amazonaws.com
docker push YOUR_AWS_ACCOUNT.dkr.ecr.eu-west-1.amazonaws.com/intrabot:latest

# Créer une task definition et un service ECS
aws ecs create-service --cluster intrabot-cluster --service-name intrabot --task-definition intrabot:1
```

### Déploiement sur Azure (Container Apps)

```bash
# Login Azure
az login

# Créer un groupe de ressources
az group create --name intrabot-rg --location westeurope

# Créer un Container Registry
az acr create --resource-group intrabot-rg --name intrabotregistry --sku Basic

# Build et push
az acr build --registry intrabotregistry --image intrabot:latest .

# Déployer sur Container Apps
az containerapp create \
  --name intrabot \
  --resource-group intrabot-rg \
  --image intrabotregistry.azurecr.io/intrabot:latest \
  --target-port 8501 \
  --ingress external \
  --env-vars MISTRAL_API_KEY=secretref:mistral-key
```

## 📁 Structure du Projet

```
intrabot/
├── data/
│   ├── raw/                          # Documents sources
│   │   ├── technique_1.txt
│   │   ├── technique_2.txt
│   │   ├── rh_1.txt
│   │   ├── rh_2.txt
│   │   └── general_1.txt
│   ├── metadata.json                 # Métadonnées et profils
│   └── chroma_db/                    # Base vectorielle ChromaDB
│
├── src/
│   ├── __init__.py
│   ├── config.py                     # Configuration centralisée
│   ├── data_ingestion.py            # Pipeline d'ingestion
│   ├── rag_engine.py                # Moteur RAG avec filtrage
│   └── utils.py                     # Utilitaires (optionnel)
│
├── app.py                           # Application Streamlit
├── requirements.txt                 # Dépendances Python
├── Dockerfile                       # Configuration Docker
├── .dockerignore                    # Exclusions Docker
├── .env.example                     # Template variables d'env
├── .gitignore                       # Exclusions Git
│
├── build.sh                         # Script de build
├── run_local.sh                     # Script d'exécution locale
├── deploy_gcp.sh                    # Script de déploiement GCP
└── README.md                        # Documentation
```

## 🔧 Configuration Avancée

### Personnalisation des Paramètres RAG

Éditez `src/config.py` pour ajuster :

```python
# Taille des chunks de texte
CHUNK_SIZE = 1000              # Augmenter pour plus de contexte
CHUNK_OVERLAP = 200            # Chevauchement entre chunks

# Nombre de documents récupérés
TOP_K_RESULTS = 4              # Plus = plus de contexte

# Paramètres du LLM
TEMPERATURE = 0.3              # 0 = déterministe, 1 = créatif
MAX_TOKENS = 1000              # Longueur max de la réponse

# Modèles Mistral
LLM_MODEL = "mistral-large-latest"     # ou "mistral-medium"
EMBEDDING_MODEL = "mistral-embed"
```

### Ajout de Nouveaux Documents

1. **Ajouter le fichier** dans `data/raw/`

2. **Mettre à jour** `data/metadata.json` :
```json
{
  "filename": "nouveau_doc.txt",
  "title": "Titre du Document",
  "profils_autorises": ["Technique", "Manager"],
  "description": "Description du document"
}
```

3. **Réindexer** :
```bash
python -m src.data_ingestion
```

### Ajout de Nouveaux Profils

1. **Modifier** `src/config.py` :
```python
AVAILABLE_PROFILES = ["Technique", "RH", "Manager", "General", "Nouveau_Profil"]
```

2. **Mettre à jour** les métadonnées des documents concernés

3. **Réindexer** la base

## 🧪 Tests et Validation

### Test du Pipeline d'Ingestion

```bash
python -m src.data_ingestion
```

Vérifications :
- ✅ Tous les documents sont chargés
- ✅ Les chunks sont créés correctement
- ✅ Les métadonnées sont attachées
- ✅ Les embeddings sont générés

### Test du Moteur RAG

```bash
python -m src.rag_engine
```

Vérifications :
- ✅ La recherche vectorielle fonctionne
- ✅ Le filtrage par profil est effectif
- ✅ Les réponses sont pertinentes
- ✅ Les sources sont correctement citées

### Test de Filtrage par Profil

Scénario de test à démontrer :

1. **Utilisateur RH** pose : "Comment déployer avec CI/CD ?"
   - ❌ Devrait répondre qu'aucun document n'est accessible
   
2. **Utilisateur Technique** pose : "Comment déployer avec CI/CD ?"
   - ✅ Devrait répondre avec le contenu de technique_2.txt

3. **Utilisateur Manager** pose les deux questions
   - ✅ Devrait avoir accès aux deux types de documents

## 📊 Monitoring et Logs

### Logs de l'Application

```bash
# Logs Docker
docker logs -f intrabot-local

# Logs Streamlit
tail -f ~/.streamlit/logs/streamlit.log
```

### Métriques Cloud Run (GCP)

```bash
# Consulter les logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=intrabot" --limit 50

# Métriques de performance
gcloud monitoring timeseries list --filter='metric.type="run.googleapis.com/request_count"'
```

## 🔒 Sécurité

### Bonnes Pratiques Implémentées

- ✅ **Filtrage strict** : Documents filtrés avant envoi au LLM
- ✅ **Métadonnées protégées** : Non exposées dans l'interface
- ✅ **API Key sécurisée** : Stockée dans variables d'environnement
- ✅ **Pas de stockage sensible** : Aucune donnée utilisateur persistée

### Recommandations Supplémentaires

- Ajouter une authentification utilisateur (OAuth, SAML)
- Implémenter des logs d'audit des requêtes
- Chiffrer les données au repos (base vectorielle)
- Utiliser des secrets managers (GCP Secret Manager, AWS Secrets Manager)

## 🐛 Dépannage

### Erreur "MISTRAL_API_KEY not found"

```bash
# Vérifier que .env existe et contient la clé
cat .env

# Recharger les variables
export $(cat .env | xargs)
```

### Erreur "ChromaDB collection not found"

```bash
# Réinitialiser la base
rm -rf data/chroma_db
python -m src.data_ingestion
```

### L'application ne démarre pas

```bash
# Vérifier les dépendances
pip install -r requirements.txt --upgrade

# Vérifier les ports
lsof -i :8501  # Port déjà utilisé ?

# Relancer avec logs verbeux
streamlit run app.py --logger.level=debug
```

## 📚 Ressources

### Documentation

- [Mistral AI Documentation](https://docs.mistral.ai/)
- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Références RAG

- [RAG Paper (Lewis et al.)](https://arxiv.org/abs/2005.11401)
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)

## 👥 Contribution

Pour contribuer au projet :

1. Fork le repository
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit les changements (`git commit -am 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT.

## 📧 Contact

Pour toute question ou support :
- Email: support@intrabot.com
- Issues: [GitHub Issues](https://github.com/your-org/intrabot/issues)

---

**IntraBot v1.0** - Propulsé par Mistral AI et LangChain 🚀
>>>>>>> 020ccc0 (premier commit)

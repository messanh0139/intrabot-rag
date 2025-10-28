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
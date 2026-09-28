# 📁 FICHE TECHNIQUE & SYSTEM DESIGN : AI PLAYLIST CURATION (ARTISHOW)
> **Guide de Préparation Entretien Mistral AI — Forward Deployed ML Engineer (FD-MLE)**

---

## 🌐 1. Architecture System Design (Diagramme Mermaid)

### 🔷 Schéma Visuel Universel (Lisible Nativement)

```text
  ┌─────────────────────────────────────────────────────────────────────────────────────────┐
  │                                📱 FRONTEND / CLIENT LAYER                               │
  │   [ 👤 Utilisateur ] ───► [ 📱 App Android (Java) ] ◄──► [ 🌐 Appetize.io Cloud Demo ]   │
  └──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                             │
                       ┌─────────────────────┴──────────────────────┐
                       │  Requêtes HTTP REST (MP3 Audio ou Texte)   │
                       ▼                                            ▼
  ┌──────────────────────────────────────────┐  ┌──────────────────────────────────────────┐
  │ ⚡ ENDPOINT 1: POST /predict (Fichier MP3) │  │ ⚡ ENDPOINT 2: POST /moodPhrasePredict  │
  └────────────────────┬─────────────────────┘  └────────────────────┬─────────────────────┘
                       │                                             │
        ┌──────────────┴──────────────┐                              │
        ▼                             ▼                              │
┌───────────────────────────┐ ┌───────────────────────────┐         │
│  Librosa Mel-Spectrogram  │ │ 64 Audio Features Extracted│         │
│      (224x224 RGB)        │ │  (MFCCs, Tempo, Tonnetz)  │         │
└─────────────┬─────────────┘ └─────────────┬─────────────┘         │
              ▼                             ▼                       │
┌───────────────────────────┐ ┌───────────────────────────┐         ▼
│ Keras CRNN (VGG16 Model)  │ │ StandardScaler + KNN Model│ ┌───────────────────────────┐
│   (13 Genres Audio)       │ │     (10 Moods Audio)      │ │ HF Inference API (ZeroShot)│
└─────────────┬─────────────┘ └─────────────┬─────────────┘ │ (bart-large-mnli NLI NLP) │
              ▼                             ▼               └─────────────┬─────────────┘
      [ Top 2 Genres ]               [ Audio Mood ]                       ▼
              │                             │                      [ Text Mood ]
              └──────────────┬──────────────┘                             │
                             ▼                                            │
  ┌───────────────────────────────────────────────────────────────────────┴─────────────────┐
  │                          🎶 MOTEUR DE CURATION & RECOMMANDATION                         │
  │  1. Génération de requêtes hybrides : "{genre1} {mood}" & "{genre2} {mood}"            │
  │  2. Interrogation API REST Deezer (Search Playlists & Filter 30s audio previews)         │
  │  3. Shuffling & Assemblage final de la Playlist (8 Titres)                              │
  └──────────────────────────────────────────┬──────────────────────────────────────────────┘
                                             │
                                             ▼
                          [ 📱 Retour JSON (Track IDs) vers l'App ]

  ┌─────────────────────────────────────────────────────────────────────────────────────────┐
  │                                🔄 MLOPS & CI/CD PIPELINE                                │
  │   [ 🐙 GitHub Repo (main) ] ──► [ ⚙️ GitHub Actions ] ──► [ 🤖 Hugging Face Spaces ]     │
  │                                 (git subtree split)         (Auto Docker Deployment)    │
  └─────────────────────────────────────────────────────────────────────────────────────────┘
```

### 🔷 Diagramme Mermaid (Requis sur GitHub ou avec extension VS Code Mermaid)

```mermaid
flowchart TD
    subgraph CLIENT["📱 Client & Interface"]
        USER["👤 Utilisateur"]
        APP["📱 App Android (Java)"]
        DEMO["🌐 appetize.io (Cloud Demo)"]
    end

    subgraph API["⚡ Backend Flask API (Docker sur Hugging Face Spaces)"]
        ROUTE_AUDIO["POST /predict (MP3)"]
        ROUTE_TEXT["POST /moodPhrasePredict (Texte)"]
    end

    subgraph AUDIO_ML["🧠 Pipeline ML Audio (Librosa + Keras + Sklearn)"]
        LIBROSA_SPEC["Librosa: Mel-Spectrogram 224x224"]
        CNN_MODEL["Keras CRNN / VGG16 (13 Genres)"]
        GENRES_OUT["Top 2 Genres Prédits"]

        LIBROSA_FEAT["Librosa: 64 Audio Features (MFCCs, Tempo...)"]
        SCALER_KNN["StandardScaler + KNN (10 Moods)"]
        AUDIO_MOOD_OUT["Audio Mood Prédit"]
    end

    subgraph NLP_ML["💬 Pipeline NLP (Zero-Shot)"]
        HF_NLI["HF API (facebook/bart-large-mnli)"]
        TEXT_MOOD_OUT["Text Mood Prédit"]
    end

    subgraph ENGINE["🎶 Moteur de Curation & Recommandation"]
        QUERY_GEN["Générateur de Requêtes Hybrides"]
        DEEZER_API["API REST Deezer (Search Playlists)"]
        FILTER["Filtre Previews 30s Valides"]
        PLAYLIST_OUT["Playlist Curatée (8 Titres)"]
    end

    subgraph MLOPS["🔄 Infrastructure MLOps & CI/CD"]
        GH_REPO["GitHub Repo (main)"]
        GH_ACTIONS["GitHub Actions (git subtree split)"]
        HF_SPACES["Hugging Face Spaces Registry"]
    end

    USER --> APP
    APP <--> DEMO

    APP -->|MP3 File| ROUTE_AUDIO
    APP -->|Text Prompt| ROUTE_TEXT

    ROUTE_AUDIO --> LIBROSA_SPEC --> CNN_MODEL --> GENRES_OUT
    ROUTE_AUDIO --> LIBROSA_FEAT --> SCALER_KNN --> AUDIO_MOOD_OUT
    ROUTE_TEXT --> HF_NLI --> TEXT_MOOD_OUT

    GENRES_OUT --> QUERY_GEN
    AUDIO_MOOD_OUT --> QUERY_GEN
    TEXT_MOOD_OUT --> QUERY_GEN

    QUERY_GEN --> DEEZER_API --> FILTER --> PLAYLIST_OUT
    PLAYLIST_OUT -->|JSON Response (Track IDs)| APP

    GH_REPO --> GH_ACTIONS --> HF_SPACES --> API
```

---

## 🧠 2. Pipeline Machine Learning & Deep Learning (Deep Dive)

### 🅰️ Classification des Genres (Audio ➔ Vision via CRNN/VGG16)
* **Concept clé :** Traiter l'analyse audio comme un problème de Computer Vision (*Audio Spectrogram Classification*).
* **Pré-traitement (Librosa) :**
  * Sampling rate : `22,050 Hz`, durée fixe de `30 secondes` (padding/wrap si plus court, tronquage si plus long).
  * Génération du **Mel-Spectrogramme** avec `n_mels=224`, `hop_length=512`.
  * Conversion en logarithme dB via `librosa.power_to_db`.
  * Export sous forme d'image RGB temporaire **224x224 pixels** (colormap `magma`).
* **Architecture du Modèle :**
  * Réseau de neurones convolutif / CRNN inspiré de **VGG16**, entraîné avec **TensorFlow / Keras 3** (`modele_crnn_hd_final_13genres.keras`).
  * **13 Classes de genres :** *Blues, Classical, Country, Disco, Hiphop, Jazz, Metal, Pop, Reggae, Rock, etc.*
  * **Inference Strategy :** Extraire les **2 probabilités de genres les plus élevées** (`genre1`, `genre2`) pour capturer les sous-genres hybrides (ex: *Rock/Metal*).

### 🅱️ Classification du Mood Audio (Feature Engineering Tabulaire + KNN)
* **Feature Extraction (64 dimensions au total) :**
  Pour chaque descripteur audio, calcul de la **moyenne (mean)** et de l'**écart-type (std)** :
  1. **13 MFCCs** (Mel-Frequency Cepstral Coefficients) -> 26 valeurs.
  2. **RMS Energy** (Root Mean Square) -> 2 valeurs.
  3. **Spectral Centroid** (Centre de gravité du spectre / "brillance") -> 2 valeurs.
  4. **Spectral Bandwidth** -> 2 valeurs.
  5. **Spectral Contrast** -> 2 valeurs.
  6. **Spectral Flatness** (Bruit vs Tonalité) -> 2 valeurs.
  7. **Spectral Rolloff** (Fréquence seuil 85% d'énergie) -> 2 valeurs.
  8. **Tonnetz** (Harmoniques et caractéristiques tonales) -> 12 valeurs.
  9. **Zero-Crossing Rate** (Taux de changement de signe) -> 2 valeurs.
  10. **Tempo (BPM)** via `librosa.beat.beat_track` -> 1 valeur.
* **Modèle Tabulaire :**
  * **StandardScaler** (`scaler.pkl`) pour normalisation.
  * **K-Nearest Neighbors Classifier** (`knn_model_mood.pkl`).
  * **10 Moods :** *dark, deep, dream, emotional, epic, happy, motivational, relaxing, romantic, sad*.

### Ⓒ Classification du Mood Texte (Zero-Shot NLP)
* **Endpoint :** `/moodPhrasePredict`
* **Modèle :** `facebook/bart-large-mnli` via Hugging Face Inference API.
* **Fonctionnement :** Classification Zero-Shot de la phrase utilisateur parmi les 10 candidats de moods.

---

## 🎶 3. Moteur de Recommandation & Algorithme de Curating

1. **Combinaisons de requêtes hybrides :**
   * Requête 1 : `"{genre1} {mood}"` ➔ Récupère 4 titres.
   * Requête 2 : `"{genre2} {mood}"` ➔ Récupère 4 titres.
   * *Fallback :* Si pas de 2ème genre distinct, bascule sur `"{mood} vibe"`.
2. **API Deezer (`https://api.deezer.com/search/playlist`) :**
   * Recherche 15 playlists pertinentes, filtre celles ayant > 5 titres, sélectionne une playlist aléatoirement pour **varier les résultats à chaque écoute**.
3. **Validation & Curation :**
   * Filtre les morceaux avec previews audio 30s actives (`t['preview']`).
   * Mélange aléatoire (`random.shuffle`) des 8 titres finaux.

---

## 🛠️ 4. Stack Infrastructure & MLOps

* **Docker Containerization :**
  * Base Image : `python:3.12-slim`.
  * Dépendances système C/C++ : `libsndfile1` et `ffmpeg`.
  * CPU Optimization : `tensorflow-cpu` pour alléger l'image.
* **CI/CD Pipeline (GitHub Actions) :**
  * Workflow `.github/workflows/sync_huggingface.yml`.
  * Commande magique : `git push space $(git subtree split --prefix artishow-api main):main --force`.
  * Isole le sous-dossier `artishow-api` pour un déploiement continu sur Hugging Face Spaces.
* **Client & Testing :**
  * App Android Java native.
  * Integration **Appetize.io** pour démonstration interactive en navigateur.

---

## 🎯 5. FAQ Technique pour Entretien Mistral AI (FD-MLE)

### Q1 : "Pourquoi transformer l'audio en image PNG pour un CNN 2D ?"
> **Réponse FD-MLE :**  
> *"C'était un arbitrage pragmatique entre transfert d'apprentissage et facilité de développement. En convertissant l'audio en Mel-spectrogramme 2D, on réutilise des architectures vision éprouvées (VGG16) pré-entraînées. En production à grande échelle, nous passerions directement les tensors 2D float32 en mémoire pour supprimer le passage par disque."*

### Q2 : "Comment optimiser la latence d'inférence ?"
> **Réponse FD-MLE :**  
> *"Passage des buffers audio en RAM (`io.BytesIO`), conversion des modèles vers ONNX Runtime / TensorRT CPU, et architecture asynchrone (Celery + Redis) avec push notifications pour le client mobile."*

### Q3 : "En quoi le rôle de Chef de Projet a apporté de la valeur technique ?"
> **Réponse FD-MLE :**  
> *"Définition du contrat d'API REST, stratégie de fallback en cas de panne Deezer, et automatisation MLOps via GitHub Actions pour que le dev Android et les devs ML travaillent en intégration continue sans friction."*

---

## 🏆 6. Storytelling STAR (Projet dont tu es fier & Auto-apprentissage)

### 🥇 Projet dont tu es fier
* **Situation :** Projet 1A Télécom Paris. Volonté d'aller au-delà d'un simple notebook et créer un produit complet.
* **Task :** Chef de projet & lead architecture pour délivrer une app Android + backend ML déployé de A à Z.
* **Action :** Choix d'architecture (CNN + KNN + Zero-Shot NLP), conteneurisation Docker, CI/CD GitHub Actions ➔ Hugging Face, tests utilisateurs massifs.
* **Result :** **Top 5 Favoris du Jury** Télécom Paris, retour très enthousiaste des utilisateurs pour le potentiel produit.

### 🥈 Auto-apprentissage (Curiosité)
* **Situation :** Projet démarré en 1A sans aucun cours préalable de Machine Learning ou Deep Learning.
* **Task :** Monter en compétence de façon autonome et ultra-rapide sur le traitement du signal et les réseaux de neurones.
* **Action :** Lecture autonome de papiers de recherche, cours en ligne, documentation Librosa/TensorFlow, prototypage itératif.
* **Result :** Maîtrise complète de la chaîne audio-to-ML et transmission des connaissances à l'équipe.

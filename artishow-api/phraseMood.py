import os
import sys
import re
import random
import unicodedata
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Encodage UTF-8 sécurisé pour Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

moods = ['happy', 'relaxing', 'dark', 'epic', 'dream', 'sad', 'motivational', 'deep', 'romantic', 'emotional']

ROUTER_API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
LEGACY_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
HF_TOKEN = os.environ.get("HF_TOKEN")

# Lexique bilingue (EN / FR) complet et racinisé pour chaque catégorie de Mood
LEXICON_MOODS = {
    'dark': [
        'angr', 'anger', 'mad', 'furi', 'rage', 'pissed', 'hate', 'hating', 'irritat', 'hostil',
        'wrath', 'annoy', 'scream', 'destruct', 'pain', 'agony', 'death', 'dead', 'nightmare',
        'demon', 'evil', 'sinister', 'dark', 'metal', 'brutal', 'aggress', 'revenge', 'toxic',
        'shadow', 'colere', 'enerve', 'haine', 'sombre', 'noir', 'obscur', 'meurtr', 'mort',
        'horreur', 'demoni', 'agressi', 'vengeance', 'tuer', 'massacr', 'frustr', 'diable',
        'grr', 'argh', 'fuck', 'merde', 'bordel', 'putain', 'deteste'
    ],
    'sad': [
        'sad', 'crying', 'cry', 'cried', 'weep', 'depress', 'broken', 'heartbreak', 'unloved',
        'lonely', 'alone', 'loneliness', 'hopeless', 'hurt', 'misery', 'despair', 'grief',
        'sorrow', 'blue', 'melanchol', 'blues', 'regret', 'lost', 'mourn', 'tear', 'tears',
        'triste', 'pleur', 'deuil', 'chagrin', 'seul', 'solitude', 'malheureu', 'brise',
        'blesse', 'peine', 'decu', 'larm', 'suicid', 'vide', 'abandon', 'manques'
    ],
    'happy': [
        'happy', 'happi', 'joy', 'cheer', 'smile', 'smiling', 'laugh', 'fun', 'party',
        'celebrat', 'sunshine', 'bliss', 'excit', 'ecstat', 'radiant', 'dance', 'dancing',
        'good vibe', 'feelgood', 'sunny', 'festiv', 'optimis', 'fete', 'joie', 'heureu',
        'sourire', 'rire', 'rigol', 'soleil', 'danse', 'ambiance', 'bonne humeur', 'delir',
        'top', 'cool', 'super', 'genial', 'yay', 'chouette', 'content'
    ],
    'motivational': [
        'motivat', 'workout', 'gym', 'fit', 'fitness', 'train', 'training', 'exercis', 'hustle',
        'grind', 'focus', 'beast', 'power', 'strength', 'strong', 'win', 'winner', 'victor',
        'champion', 'conquer', 'disciplin', 'hard work', 'stamina', 'muscl', 'cardio', 'sport',
        'energie', 'energy', 'musculation', 'entrainement', 'force', 'puissance', 'determinat',
        'guerrier', 'depassement', 'gagner', 'courir', 'run', 'running', 'push'
    ],
    'relaxing': [
        'relax', 'chill', 'calm', 'peace', 'cozy', 'quiet', 'sleep', 'bedtime', 'seren',
        'ambient', 'tranquil', 'rest', 'breath', 'soft', 'meditat', 'tea', 'spa', 'slow',
        'lofi', 'lounge', 'pause', 'detente', 'repos', 'zen', 'doux', 'douceur', 'paix',
        'sommeil', 'dormir', 'sieste', 'tranquill', 'reposant', 'pluie', 'tisane', 'bain'
    ],
    'romantic': [
        'romant', 'romance', 'love', 'lover', 'couple', 'dating', 'kiss', 'passion',
        'heart', 'affection', 'crush', 'date', 'sweetheart', 'cuddle', 'intima', 'beloved',
        'girlfriend', 'boyfriend', 'tender', 'amour', 'amoureu', 'aimer', 'baiser',
        'bisou', 'calin', 'cheri', 'tendresse', 'seduction', 'valentin', 'coeur'
    ],
    'emotional': [
        'emotion', 'touching', 'moving', 'nostalg', 'memori', 'memory', 'sentiment',
        'goosebump', 'chill', 'tearjerker', 'feelings', 'heartfelt', 'soul', 'poignant',
        'vulnerab', 'bittersweet', 'emouvant', 'touchant', 'souvenir', 'frisson', 'sensibl',
        'boulevers', 'larmoyant'
    ],
    'epic': [
        'epic', 'legend', 'hero', 'battle', 'warrior', 'fight', 'war', 'glory', 'empire',
        'cinemat', 'blockbust', 'orchestr', 'triumph', 'destiny', 'majest', 'myth', 'titan',
        'valhalla', 'grand', 'conquest', 'epique', 'heroi', 'heros', 'bataille', 'gloire',
        'cinema', 'film', 'legende', 'guerre', 'grandiose', 'triomphe', 'conquete'
    ],
    'dream': [
        'dream', 'dreamy', 'fantas', 'star', 'cloud', 'space', 'galaxy', 'cosmic', 'float',
        'surreal', 'wonderland', 'psychedel', 'imagin', 'astral', 'sleep', 'flying', 'magic',
        'myster', 'vision', 'illus', 'reve', 'planer', 'nuage', 'etoile', 'cosmos',
        'feerique', 'voyage astral', 'mysti'
    ],
    'deep': [
        'deep', 'thinking', 'thought', 'philosoph', 'meditat', 'spirit', 'universe',
        'exist', 'meaning', 'wisdom', 'conscious', 'introspect', 'contemplat', 'ponder',
        'intellect', 'profound', 'profond', 'profondeur', 'pensee', 'reflexion',
        'sens', 'sagesse', 'conscience', 'ame'
    ]
}

EMOJIS_MAP = {
    'dark': ['😡', '🤬', '👿', '😈', '💀', '☠️', '💣', '⚡', '😤', '😠', '🩸', '🗡️'],
    'sad': ['😢', '😭', '😿', '💔', '😞', '😔', '🥺', '🌧️', '🥀', '🖤'],
    'happy': ['🥳', '🎉', '😊', '😀', '😃', '😄', '😁', '😆', '💃', '🕺', '✨', '☀️'],
    'motivational': ['💪', '🏋️', '🏃', '🏆', '🥇', '🥊', '🚀', '🔥'],
    'relaxing': ['😌', '🧘', '☕', '🍵', '🛋️', '🛌', '🌿', '🍃', '🌊', '😴', '🥱'],
    'romantic': ['❤️', '💖', '💕', '💓', '💗', '💘', '🌹', '💍', '💋', '😘', '🥰', '😍'],
    'emotional': ['🥲', '🫂', '🎶', '🎭', '🎻'],
    'epic': ['⚔️', '🛡️', '👑', '🏰', '🐉', '💥', '🌋', '🦅', '🏔️'],
    'dream': ['🌌', '🌠', '🪐', '🌙', '☁️', '🦄', '🔮', '🪄'],
    'deep': ['🤔', '🧠', '📖', '⏳', '📜']
}

# Initialisation unique du modèle TF-IDF pour capture sémantique continue
try:
    _tfidf_corpus = [' '.join(LEXICON_MOODS[m]) for m in moods]
    _vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    _tfidf_matrix = _vectorizer.fit_transform(_tfidf_corpus)
except Exception:
    _vectorizer = None
    _tfidf_matrix = None

def normalize_text(text):
    """Supprime les accents et met en minuscules pour faciliter le matching."""
    text = unicodedata.normalize('NFD', text.lower())
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

def semantic_nlp_predict(phrase_utilisateur):
    """
    Classifieur hybride NLP haute performance :
    - Racines lexicales bilingues (FR/EN)
    - Analyse des émojis
    - Gestion des négations ('not happy' -> sad)
    - Similarité cosinus TF-IDF
    - Sans biais systématique vers 'relaxing'
    """
    raw_text = phrase_utilisateur.strip()
    norm = normalize_text(raw_text)
    scores = {m: 0.0 for m in moods}

    # 1. Matching de racines lexicales (FR/EN)
    for mood, roots in LEXICON_MOODS.items():
        for r in roots:
            pat = r'\b' + re.escape(r)
            matches = len(re.findall(pat, norm))
            if matches > 0:
                scores[mood] += matches * 3.0
            elif r in norm:
                scores[mood] += 1.5

    # 2. Matching d'émojis
    for mood, ems in EMOJIS_MAP.items():
        for em in ems:
            if em in raw_text:
                scores[mood] += 4.0

    # 3. Gestion des négations
    for neg in ['not ', 'no ', 'pas ', 'ne pas ', 'never ', 'dont ', "don't "]:
        if neg in norm:
            for mood in ['happy', 'relaxing']:
                for r in LEXICON_MOODS[mood][:6]:
                    if f'{neg}{r}' in norm:
                        scores[mood] -= 4.0
                        scores['sad'] += 3.0

    # 4. Similarité cosinus TF-IDF (nuances sémantiques supplémentaires)
    if _vectorizer is not None and _tfidf_matrix is not None:
        try:
            user_vec = _vectorizer.transform([norm])
            sims = cosine_similarity(user_vec, _tfidf_matrix)[0]
            for i, m in enumerate(moods):
                scores[m] += float(sims[i]) * 5.0
        except Exception:
            pass

    # 5. Détermination du meilleur mood
    best_mood = max(scores, key=scores.get)
    best_score = scores[best_mood]

    if best_score <= 0.0:
        # Aucune correspondance sémantique claire : sélection dynamique neutre
        fallback_choice = random.choice(['happy', 'relaxing'])
        print(f"  ℹ️ Aucun signal émotionnel détecté, sélection dynamique par défaut : '{fallback_choice}'", flush=True)
        return fallback_choice

    print(f"  🧠 NLP Sémantique local : Mood détecté '{best_mood}' (score: {best_score:.2f})", flush=True)
    return best_mood

def phraseMoodPredict(phrase_utilisateur):
    print(f"  📝 Phrase à analyser : '{phrase_utilisateur}'", flush=True)

    # 1. Si un token HF est configuré, tenter l'API Serverless BART-Large-MNLI
    if HF_TOKEN and HF_TOKEN.strip():
        payload = {
            "inputs": phrase_utilisateur,
            "parameters": {"candidate_labels": moods}
        }
        headers = {"Authorization": f"Bearer {HF_TOKEN.strip()}"}

        for url in [ROUTER_API_URL, LEGACY_API_URL]:
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=5)
                if response.status_code == 200:
                    resultat = response.json()
                    if isinstance(resultat, dict) and "labels" in resultat and len(resultat["labels"]) > 0:
                        top_label = resultat['labels'][0]
                        top_score = resultat.get('scores', [0.0])[0]
                        print(f"  ✅ Mood dominant NLI (BART HF) : {top_label} ({top_score:.2%})", flush=True)
                        return top_label
                else:
                    print(f"  ⚠️ Erreur API HF ({response.status_code}) sur {url} : {response.text[:150]}", flush=True)
            except Exception as e:
                print(f"  ⚠️ Exception connexion API HF sur {url} : {e}", flush=True)
    else:
        print("  ℹ️ HF_TOKEN non configuré : utilisation du moteur NLP sémantique local haute précision", flush=True)

    # 2. Moteur NLP sémantique local (0 latence, bilingue, gestion d'émojis, négations)
    return semantic_nlp_predict(phrase_utilisateur)
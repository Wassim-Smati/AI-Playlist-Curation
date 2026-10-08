import os
import sys
import requests

# Encodage UTF-8 sécurisé pour Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

moods = ['happy', 'relaxing', 'dark', 'epic', 'dream', 'sad', 'motivational', 'deep', 'romantic', 'emotional']

# Nouvelle URL du router Hugging Face Serverless (l'ancienne api-inference est dépréciée)
ROUTER_API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
LEGACY_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"

HF_TOKEN = os.environ.get("HF_TOKEN")

KEYWORD_MOOD_MAP = {
    "happy": ["heureux", "joie", "fete", "party", "happy", "sourire", "fun", "soleil", "danse", "good", "cool", "ambiance"],
    "sad": ["triste", "pleur", "seul", "deuil", "mal", "sad", "bad", "chagrin", "coeur brise", "depress", "larmes"],
    "relaxing": ["calme", "detente", "repos", "relax", "pluie", "zen", "doux", "chill", "paix", "sommeil", "nuit", "quiet"],
    "dark": ["sombre", "peur", "noir", "dark", "colere", "rage", "metal", "orage", "obscur", "demon", "hard"],
    "motivational": ["sport", "motivation", "energie", "work", "gym", "force", "go", "focus", "training", "victoire", "running"],
    "romantic": ["amour", "love", "romantique", "coeur", "cheri", "passion", "couple", "baiser", "kiss"],
    "emotional": ["emotion", "nostalgie", "souvenir", "frisson", "touchant", "sensible", "deep"],
    "epic": ["epique", "hero", "bataille", "puissant", "grand", "guerre", "cinematique", "legend", "epic"],
    "dream": ["reve", "planer", "etoile", "espace", "nuage", "dream", "voyage", "magie"],
    "deep": ["profond", "pensee", "philosophie", "meditation", "introspect", "sens"]
}

def fallback_keyword_mood(phrase_utilisateur):
    """Fallback intelligent si l'API Hugging Face est indisponible, sans token ou en erreur."""
    p = phrase_utilisateur.lower()
    for mood, kws in KEYWORD_MOOD_MAP.items():
        if any(kw in p for kw in kws):
            return mood
    return "relaxing"  # Mood musical valide pour Deezer (au lieu de 'neutral')

def phraseMoodPredict(phrase_utilisateur):
    print(f"  📝 Phrase à analyser : '{phrase_utilisateur}'", flush=True)

    payload = {
        "inputs": phrase_utilisateur,
        "parameters": {"candidate_labels": moods}
    }

    headers = {}
    if HF_TOKEN and HF_TOKEN.strip():
        headers["Authorization"] = f"Bearer {HF_TOKEN.strip()}"

    # 1. Tenter le nouvel endpoint Router Hugging Face
    for url in [ROUTER_API_URL, LEGACY_API_URL]:
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=8)
            if response.status_code == 200:
                resultat = response.json()
                if isinstance(resultat, dict) and "labels" in resultat and len(resultat["labels"]) > 0:
                    top_label = resultat['labels'][0]
                    top_score = resultat.get('scores', [0.0])[0]
                    print(f"  ✅ Mood dominant NLI (BART) : {top_label} ({top_score:.2%})", flush=True)
                    return top_label
            else:
                print(f"  ⚠️ Erreur API HF ({response.status_code}) sur {url} : {response.text[:200]}", flush=True)
        except Exception as e:
            print(f"  ⚠️ Exception connexion API HF sur {url} : {e}", flush=True)

    # 2. Si l'API échoue (token manquant, 404/410, quota), bascule sur l'heuristique sans bloquer
    fallback = fallback_keyword_mood(phrase_utilisateur)
    print(f"  ℹ️ Utilisation du fallback heuristique pour le mood : '{fallback}'", flush=True)
    return fallback
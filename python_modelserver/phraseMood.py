from imports import *
<<<<<<< HEAD
import requests
import os

moods = ['happy', 'relaxing', 'dark', 'epic', 'dream', 'sad', 'motivational', 'deep', 'romantic', 'emotional']

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
HF_TOKEN = os.environ.get("HF_TOKEN")

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def phraseMoodPredict(phrase_utilisateur):
    print(f"Phrase à analyser via API : '{phrase_utilisateur}'")
    
    payload = {
        "inputs": phrase_utilisateur,
        "parameters": {"candidate_labels": moods}
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        resultat = response.json()

        if "error" in resultat:
            print(f"Erreur API : {resultat['error']}")
            return "error"
        
        top_label = resultat['labels'][0]
        top_score = resultat['scores'][0]
        
        print(f"Mood dominant : {top_label} ({top_score:.2%})")
        return top_label

    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return "neutral" 
=======

print("bonjour")
moods = ['happy', 'relaxing', 'dark', 'epic', 'dream', 'sad', 'motivational', 'deep', 'romantic', 'emotional']

classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli")

def phraseMoodPredict(phrase_utilisateur):
    resultat = classifier(phrase_utilisateur, moods)

    print(f"Phrase à analyser : '{resultat['sequence']}'")
    print("\nRésultats du classement des moods :")

    top3_labels = resultat['labels'][:1]
    top3_scores = resultat['scores'][:1]

    for label, score in zip(top3_labels, top3_scores):
        print(f"- Mood : {label}, Score : {score:.2%}")

    string_result = " / ".join(top3_labels)

    return string_result
>>>>>>> ddd625d97fddd4a5e96fd9183369401ea3821d4f

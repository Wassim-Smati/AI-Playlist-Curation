from imports import *

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

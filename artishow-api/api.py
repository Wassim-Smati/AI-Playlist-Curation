import sys
import os
import warnings

# 1. Configuration de l'encodage et désactivation du buffering des logs (résout le décalage de 1)
try:
    sys.stdout.reconfigure(line_buffering=True, encoding='utf-8')
    sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')
except Exception:
    pass

# 2. Filtrage des avertissements verbeux (InconsistentVersionWarning scikit-learn, libmpg123, TF)
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger("artishow-api")

from flask import Flask, request, jsonify
from GenreMoodClassification import *
from CnnClassification import *
from phraseMood import *
import uuid
import joblib
from playlistGeneration import *

# Configuration Datadog Tracer (avec fallback en mode local sans ddtrace)
try:
    from ddtrace import tracer
except ImportError:
    class DummySpan:
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def set_tag(self, key, value):
            pass
        def set_tags(self, tags):
            pass
    class DummyTracer:
        def trace(self, name, service=None, resource=None, span_type=None):
            return DummySpan()
        def wrap(self, *args, **kwargs):
            def decorator(fn):
                return fn
            return decorator
    tracer = DummyTracer()

app = Flask(__name__)

# 3. Chargement des modèles au DÉMARRAGE (et non à chaque requête pour éviter latence et avertissements répétés)
logger.info("⏳ Initialisation des modèles Mood (Scaler & KNN)...")
scaler_path = "models/scaler_mood.pkl" if os.path.exists("models/scaler_mood.pkl") else "models/scaler (1).pkl"
knn_path = "models/knn_model_mood.pkl" if os.path.exists("models/knn_model_mood.pkl") else "models/knn_model_mood (1).pkl"
scaler_mood = joblib.load(scaler_path)
knn_model_mood = joblib.load(knn_path)
logger.info("✅ Modèles Mood chargés avec succès !")

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé pour Datadog Synthetics et Docker Healthcheck."""
    return jsonify({'status': 'ok', 'service': 'artishow-api'}), 200

@app.route('/predict', methods=['POST'])
def predict(): 
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not os.path.exists('uploads'): 
        os.makedirs('uploads', exist_ok=True)

    filename = f"temp_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    logger.info(f"🎵 [PREDICT] Nouvelle requête reçue (fichier audio: {file.filename})")

    try:
        # 1. Chargement audio UNIQUE (évite les chargements multiples et les warnings mpg123 en boucle)
        with tracer.trace("ml.load_audio", service="artishow-ml") as span:
            span.set_tag("audio.file_path", filepath)
            y, sr = librosa.load(filepath, sr=22050, duration=30)

        # 2. CNN Genre (avec prédiction silencieuse verbose=0)
        with tracer.trace("ml.predict_genre_cnn", service="artishow-ml") as span:
            predCnn = predict_genre(y, sr)
            if predCnn is None or len(predCnn) == 0:
                raise ValueError("Échec de la prédiction des genres par le CNN")
            predicted_indices = np.argsort(predCnn[0])[-2:][::-1]
            genre1 = genre_map[predicted_indices[0]] 
            genre2 = genre_map[predicted_indices[1]]
            span.set_tag("ml.genre_1", genre1)
            span.set_tag("ml.genre_2", genre2)

        # 3. Features Librosa & KNN Mood
        with tracer.trace("ml.extract_features_librosa", service="artishow-ml"):
            songFeatures = extract_features(y, sr=sr)
            
        df_test_mood = pd.DataFrame(songFeatures, index=[0]) 
        df_test_scaled_mood = scaler_mood.transform(df_test_mood)
        
        with tracer.trace("ml.predict_mood_knn", service="artishow-ml") as span:
            predicted_mood_array = knn_model_mood.predict(df_test_scaled_mood)
            mood = predicted_mood_array[0]
            detected_mood = mood_map[mood]
            span.set_tag("ml.mood", detected_mood)
        
        logger.info(f"🎶 Genres prédits : {genre1}, {genre2} | 🎭 Mood prédit : {detected_mood}")

        # 4. Deezer Playlist Generation
        with tracer.trace("deezer.generate_playlist", service="artishow-api") as span:
            span.set_tag("playlist.genre1", genre1)
            span.set_tag("playlist.genre2", genre2)
            span.set_tag("playlist.mood", detected_mood)
            listId = playlist_generator_music(genre1, genre2, detected_mood)
            span.set_tag("playlist.tracks_count", len(listId) if listId else 0)

        logger.info(f"✅ Playlist générée avec succès ({len(listId)} titres) : {listId}")
        return jsonify({'resultat': listId})

    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement /predict : {e}")
        return jsonify({'error': 'Failed to process audio file', 'details': str(e)}), 500

    finally:
        # Nettoyage immédiat du fichier audio temporaire
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass
        sys.stdout.flush()

@app.route('/moodPhrasePredict', methods=['POST'])
def mood_phrase_predict():
    phrase = request.form.get('string')
    if not phrase:
        return jsonify({'error': 'No string provided'}), 400

    logger.info(f"📝 [MOOD_PHRASE] Nouvelle phrase reçue : \"{phrase}\"")

    try:
        with tracer.trace("ml.phrase_mood_predict", service="artishow-ml") as span:
            result = phraseMoodPredict(phrase)
            span.set_tag("ml.mood_phrase_result", result)

        logger.info(f"🎭 Mood détecté : {result}")

        with tracer.trace("deezer.generate_playlist_mood", service="artishow-api") as span:
            span.set_tag("playlist.mood", result)
            listId = playlist_generator_mood(result)
            span.set_tag("playlist.tracks_count", len(listId) if listId else 0)

        logger.info(f"✅ Playlist générée avec succès ({len(listId)} titres) : {listId}")
        return jsonify({'resultat': listId})

    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement /moodPhrasePredict : {e}")
        return jsonify({'error': str(e)}), 500

    finally:
        sys.stdout.flush()

if __name__ == '__main__': 
    logger.info("🚀 Démarrage du serveur Artishow API sur le port 7860...")
    app.run(host='0.0.0.0', port=7860)

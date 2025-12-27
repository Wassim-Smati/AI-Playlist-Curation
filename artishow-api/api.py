from flask import Flask, request, jsonify
from GenreMoodClassification import *
from CnnClassification import *
from phraseMood import *
import uuid
from playlistGeneration import *

app = Flask(__name__)
@app.route('/predict', methods=['POST'])
def predict(): 

    if not os.path.exists('uploads'): 
        os.makedirs('uploads')

    if not os.path.exists('images'): 
        os.makedirs('images')

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = f"temp_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join("uploads", filename)
    file.save(filepath)

    """img = audio_to_mel_spec(filepath, "images/spectrogramme")
    img_array = load_image("images/spectrogramme.png")""" 

    #crnn
    spectro_path = os.path.join("images", f"spec_{uuid.uuid4().hex}.png")
    audio_to_mel_spec(filepath, spectro_path)
    img = image.load_img(spectro_path, target_size=(128, 128)) 
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)

    predCnn = model_CNN.predict(img_array)

    predicted_indices = np.argsort(predCnn[0])[-2:][::-1]
    genre1 = genre_map[predicted_indices[0]] 
    genre2 = genre_map[predicted_indices[1]]

    print(f"Genre Predicted : {genre1}, {genre2}")
    try:
        songFeatures = extract_features(filepath)
    except Exception as e:

        print(f"Erreur lors de l'extraction des features: {e}")
        return jsonify({'error': 'Failed to process audio file'}), 500
        
    df_test_mood = pd.DataFrame(songFeatures, index=[0]) 
    scaler_mood = joblib.load("models/scaler (1).pkl")
    knn_model_mood = joblib.load("models/knn_model_mood (1).pkl")
    df_test_scaled_mood = scaler_mood.transform(df_test_mood)
    
    predicted_mood_array = knn_model_mood.predict(df_test_scaled_mood)
    
    mood = predicted_mood_array[0]
    
    print(f"Mood Predicted: {mood_map[mood]}")

    if (genre1 == "country"):
        listId = playlist_generator_music(genre2, mood_map[mood])
    else: 
        listId = playlist_generator_music(genre1, mood_map[mood])

    print(f"Playlist générée : {listId}")

    return jsonify({'resultat': listId})

@app.route('/moodPhrasePredict', methods=['POST'])
def mood_phrase_predict():
    phrase = request.form.get('string')
    print(f"Phrase reçue : {phrase}")

    if not phrase:
        return jsonify({'error': 'No string provided'}), 400

    result = phraseMoodPredict(phrase)
    print(f"Mood détecté : {result}")

    listId = playlist_generator_mood(result)
    print(listId)
    return jsonify({'resultat': listId})


if __name__ == '__main__': 
    app.run(host='0.0.0.0', port=7860)


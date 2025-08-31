from imports import *
print("Versions des librairies importantes :")
print(f"  Librosa:      {librosa.__version__}")
print(f"  NumPy:        {np.__version__}")

def extract_features(file_path, duration=30, sr=22050): 
    y, sr_loaded = librosa.load(file_path, duration=30, sr=22050) 

    def stats(feature):
        return list(map(float, np.mean(feature, axis=1))) + list(map(float, np.std(feature, axis=1)))

    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    rms = librosa.feature.rms(y=y)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
    contrast = librosa.feature.spectral_contrast(y=y, sr=sr)
    flatness = librosa.feature.spectral_flatness(y=y)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    tonnetz = librosa.feature.tonnetz(y=y, sr=sr) 
    zero_crossing = librosa.feature.zero_crossing_rate(y=y)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

    features_raw = [] 
    for f_val in [mfcc, rms, spectral_centroid, bandwidth, contrast, flatness, rolloff, tonnetz, zero_crossing]:
        features_raw.extend(stats(f_val))
    features_raw.append(float(tempo))

    return [features_raw]

mood_map = {0: 'dark', 1: 'deep', 2: 'dream', 3: 'emotional', 4: 'epic', 5: 'happy', 6: 'motivational', 7: 'relaxing', 8: 'romantic', 9: 'sad'}

song = "Musiques/Dua Lipa - Houdini.mp3"
songFeatures = extract_features(song)
df_test_mood = pd.DataFrame(songFeatures)
scaler = joblib.load("Models/scaler (1).pkl")
df_test_scaled_mood = scaler.transform(df_test_mood)
knn_model_mood = joblib.load("Models/knn_model_mood (1).pkl")
prediction = knn_model_mood.predict(df_test_scaled_mood)
print(f"Prédiction (Mood): {mood_map[int(prediction[0])]}")

#dataFeatures = pd.DataFrame(songFeatures)
#scaler = joblib.load("Models/scaler.pkl")
#scaler_mood = joblib.load("Models/scaler_mood.pkl")
#featuresScaled = scaler.transform(dataFeatures)
#featuresScaled_mood = scaler_mood.transform(dataFeatures)
#print(featuresScaled)

#svm_model = joblib.load("Models/svm_model.pkl")
#LogisticRegModel = joblib.load("Models/LogisticRegModel.pkl")
#rf_model = joblib.load("Models/rf_model.pkl")
#gbt_model = joblib.load("Models/gbt_model.pkl")
#knn_model = joblib.load("Models/knn_model.pkl")


genre_map = {
    0: "blues",
    1: "classical",
    2: "country",
    3: "disco",
    4: "hiphop",
    5: "jazz",
    6: "metal",
    7: "pop",
    8: "reggae",
    9: "rock"
}


#pred = svm_model.predict(featuresScaled)
#print(genre_map[int(pred)])
#pred = knn_model.predict(featuresScaled)
#print(genre_map[int(pred)])
#pred = gbt_model.predict(featuresScaled)
#print(genre_map[int(pred)])
#pred = rf_model.predict(featuresScaled)
#print(genre_map[int(pred)])
#pred = LogisticRegModel.predict(featuresScaled)
#print(genre_map[int(pred)])
#pred = knn_model_mood.predict(featuresScaled_mood)
#print(mood_map[int(pred)])


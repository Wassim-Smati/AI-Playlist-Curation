from imports import *

def extract_features(audio_input, duration=30, sr=22050): 
    if isinstance(audio_input, (str, bytes, os.PathLike)):
        y, _ = librosa.load(audio_input, duration=duration, sr=sr) 
    else:
        y = audio_input 

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
    tempo_val = float(np.atleast_1d(tempo)[0])
    features_raw.append(tempo_val)

    return [features_raw]

mood_map = {0: 'dark', 1: 'deep', 2: 'dream', 3: 'emotional', 4: 'epic', 5: 'happy', 6: 'motivational', 7: 'relaxing', 8: 'romantic', 9: 'sad'}

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

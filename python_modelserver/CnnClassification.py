from imports import *

save_path = ""

def audio_to_mel_spec(audio, save_path, sr=22050, n_mels=128, hop_length=512):
    y, sr = librosa.load(audio, sr=sr, duration=30)
    melspec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, hop_length=hop_length)
    melspec_db = librosa.power_to_db(melspec, ref=np.max)

    plt.figure(figsize=(4.32, 2.88), dpi=100) 
    plt.imshow(melspec_db, aspect='auto', origin='lower', cmap='magma', vmin=-42, vmax=0)
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0)

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

img = audio_to_mel_spec("Musiques/System-Of-A-Down-Toxicity-_Official-HD-Video_-[AudioTrimmer.com].wav", "Images/spectrogramme")


def load_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255. 
    return img_array

model_CNN = tf.keras.models.load_model("Models/vgg16.h5")
img_array = load_image("Images/spectrogramme.png")

# Prédiction
print("bonjour")
prediction = model_CNN.predict(img_array)
print(prediction)
predicted_indices = np.argsort(prediction)[0][-2:][::-1]
print(f"Genres prédits : {genre_map[int(predicted_indices[0])],genre_map[int(predicted_indices[1])]}")
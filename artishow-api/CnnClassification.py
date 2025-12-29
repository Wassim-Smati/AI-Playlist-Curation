from imports import *
import json 
import os
import os
import json
import numpy as np
import librosa
import matplotlib.pyplot as plt
import tensorflow as tf

save_path = ""

def audio_to_mel_spec(audio, save_path, sr=22050, n_mels=128, hop_length=512):
    y, sr = librosa.load(audio, sr=sr, duration=30)
    melspec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=n_mels, hop_length=hop_length)
    melspec_db = librosa.power_to_db(melspec, ref=np.max)

    """plt.figure(figsize=(4.32, 2.88), dpi=100)""" 
    plt.figure(figsize=(1.28, 1.28), dpi=100) #taille crnn
    plt.imshow(melspec_db, aspect='auto', origin='lower', cmap='magma', vmin=-42, vmax=0)
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0)
"""
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
}"""

# mapping crnn
with open("models/genre_mapping.json", 'r') as f:
    mapping_data = json.load(f)
    genre_map = {v: k for k, v in mapping_data.items()}

def load_image(img_path):
    """img = image.load_img(img_path, target_size=(224, 224))"""
    img = image.load_img(img_path, target_size=(224, 224)) #crnn
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255. 
    return img_array

MODEL_PATH = os.path.join("", "models\modele_crnn_hd_final_13genres.keras")
MAPPING_PATH = os.path.join("", "models\genre_mapping.json")

# ==========================================
# 2. CHARGEMENT DU MODÈLE ET DU MAPPING
# ==========================================
print("⏳ Chargement du modèle...")
model_CNN = tf.keras.models.load_model("models\modele_crnn_hd_final_13genres.keras")
print("✅ Modèle chargé !")

print("⏳ Chargement des genres...")
with open("models\genre_mapping.json", 'r') as f:
    mapping = json.load(f)
    classes = {v: k for k, v in mapping.items()}
print(f"✅ {len(classes)} genres connus.")

def predict_genre(audio_path):
    try:
        # 1. Chargement audio
        y, sr = librosa.load(audio_path, sr=22050, duration=30)

        if len(y) < 22050 * 30:
            y = np.pad(y, (0, 22050 * 30 - len(y)), mode='wrap')
        else:
            y = y[:22050 * 30]

        # 2. Mel-spectrogramme (244 bandes)
        melspec = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_mels=224
        )
        melspec_db = librosa.power_to_db(melspec, ref=np.max)

        # 3. Sauvegarde image temporaire (244x244)
        temp_img_path = "temp_pred.png"
        plt.figure(figsize=(2.24, 2.24), dpi=100)  # 244x244 pixels
        plt.imshow(melspec_db, aspect='auto', origin='lower', cmap='magma')
        plt.axis('off')
        plt.savefig(temp_img_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        # 4. Chargement image pour le modèle
        img = tf.keras.utils.load_img(
            temp_img_path,
            target_size=(224, 224)
        )
        img_array = tf.keras.utils.img_to_array(img)
        img_array = tf.expand_dims(img_array, axis=0)

        # 5. Prédiction
        predictions = model_CNN.predict(img_array)

        return predictions#test

    except Exception as e:
        print(f"❌ Erreur lors de l'analyse : {e}")


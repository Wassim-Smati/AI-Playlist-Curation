import tensorflow as tf
import os

old_model_path = "models/vgg16.h5"
new_model_path = "models/vgg16.keras"

print(f"Chargement de {old_model_path} avec TF {tf.__version__}...")

model = tf.keras.models.load_model(old_model_path, compile=False)

print("Modèle chargé ! Sauvegarde au nouveau format .keras...")

model.save(new_model_path)

print(f"✅ Succès ! Nouveau modèle créé : {new_model_path}")


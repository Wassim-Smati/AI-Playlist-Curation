import tensorflow as tf
import os

input_path = "models/vgg16.keras"  # Ton fichier actuel
output_path = "models/vgg16_clean.keras" # Le fichier final

print(f"Chargement du modèle : {input_path}")
# On charge l'ancien
old_model = tf.keras.models.load_model(input_path, compile=False)

# On définit l'entrée proprement
input_tensor = tf.keras.Input(shape=(224, 224, 3))
x = input_tensor

print("Reconstruction étage par étage...")

for i, layer in enumerate(old_model.layers):
    # On saute la couche d'Input de l'ancien modèle pour ne pas faire doublon
    if isinstance(layer, tf.keras.layers.InputLayer):
        continue
        
    print(f" - Ajout couche {i}: {layer.name}")
    
    # On passe x dans la couche
    x = layer(x)
    
    # --- LE FIX MAGIQUE ---
    # Si la couche a renvoyé une LISTE (le bug), on prend juste le premier élément
    if isinstance(x, list):
        print("   ⚠️ LISTE DÉTECTÉE ! Correction appliquée -> Conversion en Tenseur.")
        x = x[0]
    # ----------------------

# On crée le nouveau modèle propre
new_model = tf.keras.Model(inputs=input_tensor, outputs=x)

print("Sauvegarde...")
new_model.save(output_path)
print(f"✅ FINI ! Le modèle propre est ici : {output_path}")